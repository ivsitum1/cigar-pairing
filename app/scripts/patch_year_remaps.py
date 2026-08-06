#!/usr/bin/env python3
"""Patch taxonomy files with year-stripping remaps.

For slug line names that have a trailing year (e.g. "Chef's Edition 2017" or
"Year of the Dragon 2024"), strip the year to produce a digit-free canonical
line name. Writes patches into the relevant taxonomy JSON files.

Usage: python scripts/patch_year_remaps.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
APP = SCRIPTS.parent
CIGARS_PATH = APP / "src" / "data" / "cigars.json"
TAXONOMY_DIR = SCRIPTS / "data" / "taxonomy"

SLUG = re.compile(r"\d")

YEAR_SUFFIX = re.compile(
    r"\s*,?\s*(Limited Edition|LE)\s+20\d{2}$"
    r"|\s+20\d{2}$",
    re.IGNORECASE,
)

# taxonomy filename overrides (brands with non-standard slug filenames)
FILE_FOR: dict[str, str] = {
    "Black Label Trading Company": "black-label.json",
    "RoMa Craft Tobac": "roma.json",
    "Cavalier Genève": "cavalier.json",
    "Laura Chavin": "laura.json",
    "Gran Habano": "gh.json",
    "Padrón": "padron.json",
    "Asylum 13": "asylum-13.json",
}

# Parent names that are too generic / meaningless as line names
SKIP_PARENTS = {
    "Limited Edition",
    "LE",
    "",
    # "Vintage" is also too generic when year is the only distinguisher
    # We keep Vintage if there are multiple records → merge is fine
}


def brand_to_slug(brand: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", brand.lower()).strip("-")


def junk_line(line: str) -> bool:
    return bool(SLUG.search(line)) or (bool(line) and line == line.lower())


def strip_year(line: str) -> str | None:
    """Return line with trailing year stripped, or None if not applicable."""
    stripped = YEAR_SUFFIX.sub("", line).strip()
    if stripped == line:
        return None
    if SLUG.search(stripped):
        return None
    if stripped in SKIP_PARENTS or len(stripped) < 2:
        return None
    return stripped


def taxonomy_file(brand: str) -> Path:
    fname = FILE_FOR.get(brand, brand_to_slug(brand) + ".json")
    return TAXONOMY_DIR / fname


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cigars = json.loads(CIGARS_PATH.read_text(encoding="utf-8"))

    # Collect remaps per brand
    brand_remaps: dict[str, dict[str, str]] = defaultdict(dict)
    for c in cigars:
        line = c.get("line", "")
        brand = c.get("brand", "")
        if not junk_line(line):
            continue
        clean = strip_year(line)
        if clean is None:
            continue
        brand_remaps[brand][line] = clean

    total_remaps = sum(len(v) for v in brand_remaps.values())
    print(f"Brands affected: {len(brand_remaps)}")
    print(f"Line remaps: {total_remaps}")

    # Count how many distinct cigars will lose slug status
    # (multiple cigars per line → they share one slug)
    raw_to_count: dict[tuple[str, str], int] = defaultdict(int)
    for c in cigars:
        line = c.get("line", "")
        brand = c.get("brand", "")
        if brand in brand_remaps and line in brand_remaps[brand]:
            raw_to_count[(brand, line)] += 1

    slug_cigars_affected = sum(raw_to_count.values())
    print(f"Slug cigars affected: {slug_cigars_affected}")

    if args.dry_run:
        print("\n--- DRY RUN ---")
        for brand, remaps in sorted(brand_remaps.items()):
            fpath = taxonomy_file(brand)
            print(f"\n{brand} -> {fpath.name}:")
            for raw, clean in sorted(remaps.items()):
                count = raw_to_count[(brand, raw)]
                print(f"  [{count}x] {repr(raw)} -> {repr(clean)}")
        return 0

    # Apply remaps to taxonomy files
    files_written = 0
    for brand, remaps in sorted(brand_remaps.items()):
        fpath = taxonomy_file(brand)
        data = load_json(fpath)

        # Ensure required fields
        if "brand" not in data:
            data["brand"] = brand
        if "status" not in data:
            data["status"] = "done"
        if "lines" not in data:
            data["lines"] = {}

        # Add remaps (only if not already defined)
        changed = False
        for raw, clean in remaps.items():
            existing = data["lines"].get(raw)
            if existing is not None:
                # Already has a spec — update only if the line value is still the raw (identity map)
                current_line = existing.get("line", raw) if isinstance(existing, dict) else raw
                if current_line == raw or current_line == clean:
                    if isinstance(existing, dict):
                        existing["line"] = clean
                    else:
                        data["lines"][raw] = {"line": clean}
                    changed = True
            else:
                data["lines"][raw] = {"line": clean}
                changed = True

        if changed:
            if not args.dry_run:
                write_json(fpath, data)
            files_written += 1
            print(f"  Patched {fpath.name} ({len(remaps)} remaps)")

    print(f"\nFiles written: {files_written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
