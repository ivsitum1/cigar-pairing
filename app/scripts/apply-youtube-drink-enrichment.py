#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply curated YouTube/drink enrichments to rum/whisky/gin/tequila JSON.

    python apply-youtube-drink-enrichment.py
    python apply-youtube-drink-enrichment.py --check
    python apply-youtube-drink-enrichment.py --category whisky
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "src" / "data"
DATA = HERE / "data" / "youtube"

CATEGORIES = {
    "rum": (DATA / "rum_enrichments.json", APP / "rums.json"),
    "whisky": (DATA / "whisky_enrichments.json", APP / "whiskies.json"),
    "gin": (DATA / "gin_enrichments.json", APP / "gins.json"),
    "tequila": (DATA / "tequila_enrichments.json", APP / "tequilas.json"),
}

ALLOWED = frozenset({"notes", "cigarHint"})


def apply_one(enrich_path: Path, catalog_path: Path, *, check: bool) -> tuple[int, list[str]]:
    if not enrich_path.is_file():
        return 0, [f"missing:{enrich_path.name}"]
    payload = json.loads(enrich_path.read_text(encoding="utf-8"))
    enrichments = payload.get("enrichments") or {}
    rows = json.loads(catalog_path.read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in rows}
    changed: list[str] = []
    missing: list[str] = []
    for drink_id, entry in enrichments.items():
        row = by_id.get(drink_id)
        if row is None:
            missing.append(drink_id)
            continue
        touched = False
        for key, value in entry.items():
            if key not in ALLOWED:
                continue
            if row.get(key) != value:
                row[key] = value
                touched = True
        if touched:
            changed.append(drink_id)
    if check:
        return len(changed), missing
    if changed:
        catalog_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(changed), missing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--category",
        choices=["all", *CATEGORIES.keys()],
        default="all",
    )
    args = parser.parse_args()

    cats = list(CATEGORIES.keys()) if args.category == "all" else [args.category]
    total = 0
    any_pending = False
    for cat in cats:
        enrich_path, catalog_path = CATEGORIES[cat]
        n, missing = apply_one(enrich_path, catalog_path, check=args.check)
        for m in missing:
            print(f"WARN {cat} missing:{m}", file=sys.stderr)
        total += n
        if args.check:
            if n:
                print(f"apply-youtube-drink-enrichment[{cat}]: would update {n}")
                any_pending = True
            else:
                print(f"apply-youtube-drink-enrichment[{cat}]: ok (no pending writes)")
        else:
            print(f"{cat}: updated {n}")
    if args.check and any_pending:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
