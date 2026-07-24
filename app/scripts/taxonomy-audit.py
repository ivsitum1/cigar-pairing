#!/usr/bin/env python3
"""Audit cigars.json into taxonomy_audit.json + per-brand worklist stubs.

Usage:
  python scripts/taxonomy-audit.py
  python scripts/taxonomy-audit.py --fail-on-new   # CI: every brand/line covered
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

from taxonomy_lib import (
    OUT_DIR,
    TAXONOMY_DIR,
    WORKLIST_DIR,
    brand_slug,
    format_missing,
    is_sampler_line,
    line_ends_with_shape,
    line_has_dimensions,
    load_json,
    normalize_line_key,
    shape_words,
    taxonomy_brand_files,
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


def _known_lines_from_tax(data: dict) -> set[str]:
    known: set[str] = set()
    for key, rem in (data.get("lines") or {}).items():
        known.add(key)
        if isinstance(rem, dict) and rem.get("line"):
            known.add(str(rem["line"]))
        elif isinstance(rem, str):
            known.add(rem)
    for pair in data.get("keepSeparate") or []:
        if isinstance(pair, (list, tuple)):
            for item in pair:
                if isinstance(item, str):
                    known.add(item)
    for u in data.get("unresolved") or []:
        if isinstance(u, str) and u.strip() and "'" not in u and len(u) < 80:
            # bare line names only; prose notes are ignored
            known.add(u.strip())
        elif isinstance(u, dict) and u.get("line"):
            known.add(str(u["line"]))
    return known


def index_taxonomy_by_brand() -> dict[str, dict]:
    """Map canonical brand name → taxonomy dict (renameBrand targets included)."""
    by_brand: dict[str, dict] = {}
    for p in taxonomy_brand_files():
        data = load_json(p, {}) or {}
        if not isinstance(data, dict):
            continue
        data = {**data, "_file": p.name}
        brand = data.get("brand")
        if isinstance(brand, str) and brand:
            by_brand[brand] = data
        rb = data.get("renameBrand")
        if isinstance(rb, str) and rb:
            # Prefer a file whose renameBrand points at the live brand when present
            by_brand.setdefault(rb, data)
    return by_brand


def fail_on_new_violations(cigars: list) -> list[str]:
    """Brands/lines in corpus that lack taxonomy coverage (Phase 5)."""
    by_brand: dict[str, set[str]] = collections.defaultdict(set)
    for c in cigars:
        brand = c.get("brand") or ""
        line = c.get("line") or ""
        if brand:
            by_brand[brand].add(line)

    tax = index_taxonomy_by_brand()
    errors: list[str] = []

    for brand in sorted(by_brand, key=str.lower):
        data = tax.get(brand)
        if data is None:
            slug_path = TAXONOMY_DIR / f"{brand_slug(brand)}.json"
            if slug_path.exists():
                data = load_json(slug_path, {}) or {}
                data = {**data, "_file": slug_path.name}
            else:
                errors.append(f"missing taxonomy file for brand: {brand}")
                continue

        status = data.get("status") or "todo"
        # brand-only / todo / partial: file existence is enough until review finishes
        if status != "done":
            continue

        known = _known_lines_from_tax(data)
        for line in sorted(by_brand[brand], key=str.lower):
            if line and line not in known:
                errors.append(
                    f"new line without taxonomy entry: {brand} · {line} "
                    f"(add to {data.get('_file', brand_slug(brand) + '.json')} lines or unresolved)"
                )
    return errors


def run_audit(*, write_worklist: bool = True) -> dict:
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

    if write_worklist:
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

        truncated = False
        if first_tokens:
            common, n = collections.Counter(first_tokens).most_common(1)[0]
            brand_first = (brand.split()[0] if brand else "").lower()
            if n / len(first_tokens) >= 0.8 and common and common != brand_first:
                truncated = True
            if len(brand.split()) == 1 and n / len(first_tokens) >= 0.8:
                truncated = True

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

        if write_worklist:
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
        "source": CIGARS_PATH.name,
        "totals": totals,
        "brand_truncated": sorted(brand_truncated),
        "brands": brands_out,
    }
    write_json(OUT_DIR / "taxonomy_audit.json", audit)
    return {
        "brands": totals["brands"],
        "records": totals["records"],
        "brand_truncated": len(brand_truncated),
        "worklist": len(list(WORKLIST_DIR.glob("*.json"))) if WORKLIST_DIR.exists() else 0,
        "dims_in_line": totals["has_dimensions_in_line"],
        "ends_with_shape": totals["ends_with_shape"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fail-on-new",
        action="store_true",
        help="Exit 1 if any brand/line in cigars.json lacks taxonomy coverage",
    )
    ap.add_argument(
        "--no-worklist",
        action="store_true",
        help="Do not rewrite taxonomy/_worklist stubs",
    )
    ap.add_argument(
        "--check-only",
        action="store_true",
        help="Only run --fail-on-new checks (no audit JSON / worklist writes)",
    )
    args = ap.parse_args()

    cigars = load_json(CIGARS_PATH, [])
    if not isinstance(cigars, list):
        print("cigars.json is not a list", file=sys.stderr)
        sys.exit(2)

    if args.fail_on_new or args.check_only:
        violations = fail_on_new_violations(cigars)
        if violations:
            print(json.dumps({"ok": False, "violations": violations}, indent=2, ensure_ascii=False))
            sys.exit(1)
        print(json.dumps({"ok": True, "violations": []}, indent=2))
        if args.check_only:
            return

    summary = run_audit(write_worklist=not (args.no_worklist or args.fail_on_new))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
