#!/usr/bin/env python3
"""Seed taxonomy/<brand>.json stubs from line_map.json + line_merge_decisions.json.

Only writes files that do not already exist (or have status todo/partial from seed).
Does not invent new judgements beyond what the legacy stores encode.

Usage:  python scripts/seed-taxonomy-from-legacy.py
"""
from __future__ import annotations

import collections
from pathlib import Path

from taxonomy_lib import (
    CIGARS_PATH,
    LINE_MAP_PATH,
    LINE_MERGES_PATH,
    TAXONOMY_DIR,
    brand_slug,
    load_json,
    write_json,
)


def parse_line_map(line_map: dict) -> dict[str, dict[str, str]]:
    """brand -> { raw_line -> canonical_line }"""
    out: dict[str, dict[str, str]] = collections.defaultdict(dict)
    for k, v in line_map.items():
        if k.startswith("_") or not isinstance(v, str):
            continue
        if "::" not in k:
            continue
        brand, raw = k.split("::", 1)
        if raw == "*":
            continue  # wildcard handled separately if needed
        out[brand][raw] = v
    return out


def seed_from_merges(cigars_by_id: dict, merges: dict, by_brand: dict[str, dict]) -> None:
    """Translate absorb decisions into line remaps where the absorbed id's line
    should become a vitola of the canonical id's line."""
    for canon_id, spec in merges.items():
        if canon_id.startswith("_") or not isinstance(spec, dict):
            continue
        canon = cigars_by_id.get(canon_id)
        if not canon:
            continue
        brand = canon.get("brand") or ""
        entry = by_brand.setdefault(
            brand,
            {
                "brand": brand,
                "renameBrand": None,
                "status": "partial",
                "reviewedAt": None,
                "sources": ["seed-taxonomy-from-legacy.py / line_merge_decisions.json"],
                "lines": {},
                "vitolaRenames": {},
                "shapes": {},
                "keepSeparate": [],
                "lineNotes": {},
                "unresolved": [],
            },
        )
        renames = spec.get("rename_absorbed_vitolas") or {}
        for abs_id in spec.get("absorb") or []:
            other = cigars_by_id.get(abs_id)
            if not other:
                continue
            raw_line = other.get("line") or ""
            # absorbed line folds into canonical line; vitola name from rename map or other.vitola
            vname = other.get("vitola") or (other.get("vitolas") or [{}])[0].get("name")
            if vname in renames:
                new_v = renames[vname]
            else:
                new_v = renames.get(vname) if renames else None
                # sometimes map is old_name -> new
                new_v = renames.get(vname, vname)
            entry["lines"][raw_line] = {
                "line": canon.get("line"),
                "vitola": new_v or vname,
            }
        # keepSeparate from _keep_distinct handled below


def main() -> None:
    cigars = load_json(CIGARS_PATH, [])
    by_id = {c["id"]: c for c in cigars if c.get("id")}
    line_map = load_json(LINE_MAP_PATH, {}) or {}
    merges = load_json(LINE_MERGES_PATH, {}) or {}

    by_brand: dict[str, dict] = {}

    # line_map seeds
    mapped = parse_line_map(line_map)
    for brand, lines in mapped.items():
        entry = by_brand.setdefault(
            brand,
            {
                "brand": brand,
                "renameBrand": None,
                "status": "partial",
                "reviewedAt": None,
                "sources": ["seed-taxonomy-from-legacy.py / line_map.json"],
                "lines": {},
                "vitolaRenames": {},
                "shapes": {},
                "keepSeparate": [],
                "lineNotes": {},
                "unresolved": [],
            },
        )
        if "line_map.json" not in " ".join(entry.get("sources") or []):
            entry.setdefault("sources", []).append("seed-taxonomy-from-legacy.py / line_map.json")
        for raw, canon in lines.items():
            entry["lines"].setdefault(raw, {"line": canon})

    seed_from_merges(by_id, merges, by_brand)

    # keepSeparate from _keep_distinct
    for block in merges.get("_keep_distinct") or []:
        ids = block.get("ids") or []
        lines = block.get("lines") or []
        brands = set()
        for i in ids:
            c = by_id.get(i)
            if c:
                brands.add(c.get("brand"))
        # if lines listed, use those; else derive from ids
        if not lines:
            lines = []
            for i in ids:
                c = by_id.get(i)
                if c and c.get("line"):
                    lines.append(c["line"])
        for brand in brands:
            if not brand:
                continue
            entry = by_brand.setdefault(
                brand,
                {
                    "brand": brand,
                    "renameBrand": None,
                    "status": "partial",
                    "reviewedAt": None,
                    "sources": ["seed-taxonomy-from-legacy.py / line_merge_decisions.json"],
                    "lines": {},
                    "vitolaRenames": {},
                    "shapes": {},
                    "keepSeparate": [],
                    "lineNotes": {},
                    "unresolved": [],
                },
            )
            # pairwise keepSeparate for listed lines
            uniq = sorted(set(lines))
            for i, a in enumerate(uniq):
                for b in uniq[i + 1 :]:
                    pair = [a, b]
                    if pair not in entry["keepSeparate"] and [b, a] not in entry["keepSeparate"]:
                        entry["keepSeparate"].append(pair)

    TAXONOMY_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for brand, entry in sorted(by_brand.items(), key=lambda x: x[0].lower()):
        path = TAXONOMY_DIR / f"{brand_slug(brand)}.json"
        if path.exists():
            existing = load_json(path, {}) or {}
            if existing.get("status") in ("done", "brand-only"):
                skipped += 1
                continue
            # merge lines into existing partial/todo
            existing.setdefault("lines", {}).update(entry.get("lines") or {})
            for pair in entry.get("keepSeparate") or []:
                ks = existing.setdefault("keepSeparate", [])
                if pair not in ks and list(reversed(pair)) not in ks:
                    ks.append(pair)
            if existing.get("status") == "todo":
                existing["status"] = "partial"
            for src in entry.get("sources") or []:
                if src not in (existing.get("sources") or []):
                    existing.setdefault("sources", []).append(src)
            write_json(path, existing)
            written += 1
        else:
            write_json(path, entry)
            written += 1

    print({"written_or_updated": written, "skipped_done": skipped, "brands": len(by_brand)})


if __name__ == "__main__":
    main()
