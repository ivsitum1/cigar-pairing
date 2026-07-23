#!/usr/bin/env python3
"""Print brand → line → vitola tree for eyeballing.

Usage:  python scripts/taxonomy-report.py --brand "La Galera"
"""
from __future__ import annotations

import argparse
import sys

from taxonomy_lib import BRANDS_PATH, CIGARS_PATH, load_json


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    args = ap.parse_args()

    cigars = load_json(CIGARS_PATH, [])
    brands = load_json(BRANDS_PATH, {}) or {}
    rows = [c for c in cigars if (c.get("brand") or "") == args.brand]
    if not rows:
        # case-insensitive fallback
        rows = [c for c in cigars if (c.get("brand") or "").lower() == args.brand.lower()]
    if not rows:
        print(f"No records for brand {args.brand!r}", file=sys.stderr)
        sys.exit(1)

    brand = rows[0]["brand"]
    info = brands.get(brand) or {}
    country = info.get("country") or "?"
    founded = info.get("founded") or "?"
    print(f"{brand}  ({country}, {founded})")

    rows = sorted(rows, key=lambda c: (c.get("line") or "").lower())
    for i, c in enumerate(rows):
        vitolas = c.get("vitolas") or []
        names = [v.get("name") or "?" for v in vitolas]
        preview = " · ".join(names[:6])
        if len(names) > 6:
            preview += " · …"
        branch = "`--" if i == len(rows) - 1 else "|--"
        line = c.get("line") or "?"
        msg = f"{branch} {line:<24} {len(vitolas):>2} vitolas   {preview}"
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
