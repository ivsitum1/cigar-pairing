#!/usr/bin/env python3
"""Phase 3 W3 + W4 finish.

W3: brands with 2–4 live records
W4: single-line brands (mostly confirm / light clean)

Writes taxonomy JSON only; parent runs apply-taxonomy.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from taxonomy_lib import (
    TAXONOMY_DIR,
    brand_slug,
    is_sampler_line,
    line_ends_with_shape,
    load_json,
    shape_words,
    split_trailing_dimensions,
    write_json,
)
from phase3_w2_status import W1

APP = Path(__file__).resolve().parent.parent
CIGARS_PATH = APP / "src/data/cigars.json"
OUT = Path(__file__).resolve().parent / "output"
SHAPES = shape_words()

HABANOS = {
    "Bolivar",
    "Cohiba",
    "Cuaba",
    "Diplomaticos",
    "Fonseca",
    "H. Upmann",
    "Hoyo de Monterrey",
    "José L. Piedra",
    "Juan Lopez",
    "Montecristo",
    "Partagás",
    "Por Larranaga",
    "Punch",
    "Quai d'Orsay",
    "Rafael Gonzalez",
    "Ramón Allones",
    "Romeo y Julieta",
    "San Cristobal",
    "Sancho Panza",
    "Trinidad",
    "Vegueros",
}


def strip_pack(raw: str) -> str:
    return re.sub(r"/\d+\s*$", "", raw).strip()


def dedupe_words(s: str) -> str:
    return re.sub(r"\b(\w+)(?:\s+\1)+\b", r"\1", s, flags=re.I)


def strip_brand_prefix(raw: str, brand: str) -> str:
    for prefix in (brand, brand.replace(".", ""), brand.split()[0] if brand else ""):
        if not prefix or len(prefix) < 3:
            continue
        if raw.lower().startswith(prefix.lower() + " "):
            return raw[len(prefix) :].strip()
        folded = prefix.lower().replace("ñ", "n").replace("á", "a")
        if raw.lower().startswith(folded + " "):
            return raw[len(prefix) :].strip()
    return raw


def generic_remap(brand: str, raw: str, vitola_name: str | None) -> dict:
    cleaned = dedupe_words(strip_pack(raw)).strip()
    cleaned = strip_brand_prefix(cleaned, brand)

    if is_sampler_line(cleaned, vitola_name or ""):
        return {"line": cleaned or raw, "sampler": True}

    dim = split_trailing_dimensions(cleaned)
    if dim:
        base, _fmt = dim
        return {"line": base}

    sh = line_ends_with_shape(cleaned, SHAPES)
    if sh and " " in cleaned and cleaned.lower().endswith(sh) and cleaned.lower() != sh:
        base = cleaned[: -len(sh)].strip(" -·|/")
        if base and len(base) >= 2:
            vit = cleaned[len(base) :].strip() or sh
            return {"line": base, "vitola": vit}

    if re.match(r"^Year Of The ", cleaned, re.I) or re.match(r"^Year of ", cleaned):
        norm = re.sub(r"^Year Of The ", "Year of the ", cleaned, flags=re.I)
        norm = re.sub(r"^Year of (?!the )", "Year of the ", norm, flags=re.I)
        return {"line": norm}

    return {"line": cleaned or raw}


def w4_remap(brand: str, raw: str, vitola_name: str | None) -> dict:
    """Single-line brands: prefer brand-as-core-line when line echoes brand."""
    g = generic_remap(brand, raw, vitola_name)
    line = g.get("line") or raw

    # Class H: line == brand (or emptied after prefix strip) → keep brand as line
    if not line or line.lower() == brand.lower() or normalize_eq(line, brand):
        return {"line": brand}

    # line is only a shape → brand core + vitola
    sh = line_ends_with_shape(line, SHAPES)
    if sh and line.lower() == sh:
        return {"line": brand, "vitola": line}

    return g


def normalize_eq(a: str, b: str) -> bool:
    def fold(s: str) -> str:
        s = re.sub(r"[^a-z0-9]+", "", s.lower())
        return s

    return fold(a) == fold(b)


def write_brand(brand: str, rows: list, wave: str) -> dict:
    fname = f"{brand_slug(brand)}.json"
    path = TAXONOMY_DIR / fname
    existing = load_json(path, {}) or {}
    lines: dict[str, dict] = {}
    unr: list[str] = list(existing.get("unresolved") or [])

    for r in rows:
        raw = r.get("line") or ""
        vname = (r.get("vitolas") or [{}])[0].get("name")
        if wave == "W4":
            lines[raw] = w4_remap(brand, raw, vname)
        else:
            lines[raw] = generic_remap(brand, raw, vname)

    if brand in HABANOS and wave == "W3":
        msg = f"{brand}: Habanos small set — verify Clásica folds if any"
        if msg not in unr:
            unr.append(msg)

    doc = {
        "brand": brand,
        "renameBrand": existing.get("renameBrand"),
        "status": "done",
        "reviewedAt": "2026-07-24",
        "sources": list(
            dict.fromkeys(
                (existing.get("sources") or [])
                + [
                    f"phase3_w3_w4_finish {wave}",
                    "docs/superpowers/plans/2026-07-23-cigar-taxonomy-brand-line-vitola.md §7.3",
                ]
            )
        ),
        "lines": lines,
        "vitolaRenames": existing.get("vitolaRenames") or {},
        "shapes": existing.get("shapes") or {},
        "keepSeparate": existing.get("keepSeparate") or [],
        "lineNotes": existing.get("lineNotes") or {},
        "unresolved": unr,
    }
    write_json(path, doc)
    return {"file": fname, "remaps": len(lines), "unresolved": len(unr), "skipped": False}


def collect(lo: int, hi: int) -> list[str]:
    cigars = json.loads(CIGARS_PATH.read_text(encoding="utf-8"))
    counts = Counter(c["brand"] for c in cigars)
    brands = []
    for brand, n in counts.most_common():
        if brand in W1:
            continue
        if lo <= n <= hi:
            brands.append(brand)
    return brands


def main() -> None:
    cigars = json.loads(CIGARS_PATH.read_text(encoding="utf-8"))
    by_brand: dict[str, list] = defaultdict(list)
    for c in cigars:
        by_brand[c["brand"]].append(c)

    report = {"W3": {}, "W4": {}}
    snap = {"W3": {}, "W4": {}}

    w3 = collect(2, 4)
    w4 = collect(1, 1)

    for brand in w3:
        rows = by_brand[brand]
        snap["W3"][brand] = [
            {"id": r.get("id"), "line": r.get("line"), "vitolas": r.get("vitolas")} for r in rows
        ]
        report["W3"][brand] = write_brand(brand, rows, "W3")

    for brand in w4:
        rows = by_brand[brand]
        snap["W4"][brand] = [
            {"id": r.get("id"), "line": r.get("line"), "vitolas": r.get("vitolas")} for r in rows
        ]
        report["W4"][brand] = write_brand(brand, rows, "W4")

    write_json(OUT / "phase3_w3_w4_snapshot.json", snap)
    write_json(OUT / "phase3_w3_w4_report.json", report)
    summary = {
        "W3_brands": len(report["W3"]),
        "W3_written": sum(1 for v in report["W3"].values() if not v.get("skipped")),
        "W4_brands": len(report["W4"]),
        "W4_written": sum(1 for v in report["W4"].values() if not v.get("skipped")),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
