#!/usr/bin/env python3
"""Audit cigars.json into taxonomy_audit.json + per-brand worklist stubs.

Usage:  python scripts/taxonomy-audit.py
"""
from __future__ import annotations

import collections
from pathlib import Path

from taxonomy_lib import (
    OUT_DIR,
    WORKLIST_DIR,
    brand_slug,
    cigar_id,
    format_missing,
    is_sampler_line,
    line_ends_with_shape,
    line_has_dimensions,
    load_json,
    normalize_line_key,
    shape_words,
    vitola_repeats_line_tokens,
    write_json,
    CIGARS_PATH,
)

APP = Path(__file__).resolve().parent.parent


def suggest_split_b(line: str) -> dict | None:
    """Class B: strip trailing dimension group."""
    import re

    m = re.search(
        r"(?i)^(.+?)\s+(\d+(?:\s+\d+/\d+)?)\s*[x×]\s*(\d+)\s*$",
        (line or "").strip(),
    )
    if not m:
        return None
    return {
        "line": m.group(1).strip(),
        "format_hint": f"{m.group(2)} x {m.group(3)}",
        "class": "B",
    }


def suggest_split_c(line: str, shapes: set[str]) -> dict | None:
    sh = line_ends_with_shape(line, shapes)
    if not sh:
        return None
    low = line.strip().lower()
    cut = len(line) - len(sh) if low.endswith(sh) else None
    if cut is None:
        return None
    base = line[:cut].strip()
    if not base:
        return None
    return {"line": base, "vitola": sh.title() if sh.islower() else sh, "shape": sh.title(), "class": "C"}


def main() -> None:
    cigars = load_json(CIGARS_PATH, [])
    shapes = shape_words()
    by_brand: dict[str, list] = collections.defaultdict(list)
    for c in cigars:
        by_brand[c.get("brand") or ""].append(c)

    brands_out = {}
    brand_truncated = []
    totals = {
        "records": len(cigars),
        "brands": len(by_brand),
        "has_dimensions_in_line": 0,
        "ends_with_shape": 0,
        "line_eq_brand": 0,
        "single_vitola": 0,
        "is_sampler": 0,
        "vitola_repeats_line_tokens": 0,
        "format_missing": 0,
    }

    WORKLIST_DIR.mkdir(parents=True, exist_ok=True)

    for brand, rows in sorted(by_brand.items(), key=lambda x: x[0].lower()):
        bslug = brand_slug(brand)
        records = []
        first_tokens = []
        lines_norm: dict[str, list[str]] = collections.defaultdict(list)
        raw_lines = []

        for c in rows:
            line = c.get("line") or ""
            vitolas = c.get("vitolas") or []
            vnames = [v.get("name") or "" for v in vitolas]
            flags = {
                "has_dimensions_in_line": line_has_dimensions(line),
                "ends_with_shape": line_ends_with_shape(line, shapes),
                "line_eq_brand": line.strip().lower() == brand.strip().lower(),
                "single_vitola": len(vitolas) == 1,
                "is_sampler": is_sampler_line(line, c.get("vitola") or ""),
                "vitola_repeats_line_tokens": any(
                    vitola_repeats_line_tokens(line, n) for n in vnames
                ),
                "format_missing": any(format_missing(v.get("format")) for v in vitolas)
                or format_missing(c.get("format")),
            }
            for k, v in flags.items():
                if k not in totals:
                    continue
                if k == "ends_with_shape":
                    if v:
                        totals[k] += 1
                elif v:
                    totals[k] += 1

            suggested = None
            if flags["has_dimensions_in_line"]:
                suggested = suggest_split_b(line)
            elif flags["ends_with_shape"] and flags["single_vitola"]:
                suggested = suggest_split_c(line, shapes)

            rec = {
                "id": c.get("id"),
                "line": line,
                "vitola": c.get("vitola"),
                "vitolas": [
                    {
                        "name": v.get("name"),
                        "format": v.get("format"),
                        "priceEUR": v.get("priceEUR"),
                        "url": v.get("url"),
                    }
                    for v in vitolas
                ],
                "format": c.get("format"),
                "priceUrl": c.get("priceUrl"),
                "regionLinks": c.get("regionLinks"),
                "flags": {
                    **{k: (bool(v) if k != "ends_with_shape" else v) for k, v in flags.items()}
                },
                "suggested_split": suggested,
            }
            records.append(rec)
            ft = (line or brand).split()[0] if (line or brand) else ""
            if ft:
                first_tokens.append(ft.lower())
            lines_norm[normalize_line_key(line)].append(line)
            raw_lines.append(line)

        # brand_truncated: ≥80% of lines share first token AND that token != brand first token
        # meaning the brand name was cut and the rest spilled into lines
        truncated = False
        if first_tokens:
            common, n = collections.Counter(first_tokens).most_common(1)[0]
            brand_first = (brand.split()[0] if brand else "").lower()
            if n / len(first_tokens) >= 0.8 and common and common != brand_first:
                # weaker signal: many lines start with same word that looks like brand continuation
                truncated = True
            # stronger: brand is a single short token and lines start with a shared second brand word
            if len(brand.split()) == 1 and n / len(first_tokens) >= 0.8:
                truncated = True

        # prefix overlap pairs within brand
        prefix_pairs = []
        uniq_lines = sorted(set(raw_lines), key=str.lower)
        for i, a in enumerate(uniq_lines):
            na = normalize_line_key(a)
            for b in uniq_lines[i + 1 :]:
                nb = normalize_line_key(b)
                if not na or not nb or na == nb:
                    continue
                if na.startswith(nb + " ") or nb.startswith(na + " "):
                    prefix_pairs.append([a, b])

        norm_dups = {k: v for k, v in lines_norm.items() if len(set(v)) > 1}

        entry = {
            "brand": brand,
            "slug": bslug,
            "record_count": len(records),
            "brand_truncated": truncated,
            "prefix_overlap_pairs": prefix_pairs[:50],
            "normalized_duplicate_lines": {k: sorted(set(v)) for k, v in list(norm_dups.items())[:30]},
            "records": records,
        }
        brands_out[brand] = entry
        if truncated:
            brand_truncated.append(brand)

        # worklist stub (agent starting point; never overwrite richer taxonomy/*.json)
        stub = {
            "brand": brand,
            "renameBrand": None,
            "status": "todo",
            "reviewedAt": None,
            "sources": [],
            "lines": {},
            "vitolaRenames": {},
            "shapes": {},
            "keepSeparate": [],
            "lineNotes": {},
            "unresolved": [],
            "_from_audit": {
                "record_count": len(records),
                "brand_truncated": truncated,
                "prefix_overlap_pairs": len(prefix_pairs),
            },
        }
        write_json(WORKLIST_DIR / f"{bslug}.json", stub)

    audit = {
        "source": str(CIGARS_PATH.relative_to(APP.parent) if False else CIGARS_PATH.name),
        "totals": totals,
        "brand_truncated": sorted(brand_truncated),
        "brands": brands_out,
    }
    write_json(OUT_DIR / "taxonomy_audit.json", audit)
    import json as _json

    print(
        _json.dumps(
            {
                "brands": totals["brands"],
                "records": totals["records"],
                "brand_truncated": len(brand_truncated),
                "worklist": len(list(WORKLIST_DIR.glob("*.json"))),
                "dims_in_line": totals["has_dimensions_in_line"],
                "ends_with_shape": totals["ends_with_shape"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
