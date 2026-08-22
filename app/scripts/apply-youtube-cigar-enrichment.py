#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply curated YouTube-corpus cigar enrichments to cigars.json (notes only).

Source: scripts/data/youtube/cigar_enrichments.json (original copy; not transcripts).

    python apply-youtube-cigar-enrichment.py          # write
    python apply-youtube-cigar-enrichment.py --check  # CI gate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
ENRICH = HERE / "data" / "youtube" / "cigar_enrichments.json"
CIGARS = DATA / "cigars.json"

ALLOWED_FIELDS = frozenset({"notes"})


def load_enrichments() -> dict[str, dict]:
    payload = json.loads(ENRICH.read_text(encoding="utf-8"))
    raw = payload.get("enrichments") or {}
    out: dict[str, dict] = {}
    for cigar_id, entry in raw.items():
        if not isinstance(entry, dict):
            raise ValueError(f"enrichment for {cigar_id} must be an object")
        fields = {k: v for k, v in entry.items() if k in ALLOWED_FIELDS}
        if not fields:
            raise ValueError(f"enrichment for {cigar_id} has no notes")
        for key in fields:
            if key not in ALLOWED_FIELDS:
                raise ValueError(f"forbidden field {key} on {cigar_id}")
        out[cigar_id] = fields
    return out


def apply(cigars: list[dict], enrichments: dict[str, dict]) -> tuple[list[dict], list[str]]:
    by_id = {c["id"]: c for c in cigars}
    missing: list[str] = []
    changed_ids: list[str] = []

    for cigar_id, fields in enrichments.items():
        row = by_id.get(cigar_id)
        if row is None:
            missing.append(cigar_id)
            continue
        touched = False
        for key, value in fields.items():
            if row.get(key) != value:
                row[key] = value
                touched = True
        if touched:
            changed_ids.append(cigar_id)

    return cigars, changed_ids + [f"missing:{m}" for m in missing]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="exit 1 if file would change")
    args = parser.parse_args()

    if not ENRICH.is_file():
        print(f"missing enrichments file: {ENRICH}", file=sys.stderr)
        return 1

    enrichments = load_enrichments()
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    updated, report = apply(cigars, enrichments)

    missing = [x for x in report if x.startswith("missing:")]
    changed = [x for x in report if not x.startswith("missing:")]

    if missing:
        for m in missing:
            print(f"WARN {m}", file=sys.stderr)

    would_change = len(changed) > 0
    if args.check:
        if would_change:
            print(f"apply-youtube-cigar-enrichment: would update {len(changed)} cigars")
            return 1
        print("apply-youtube-cigar-enrichment: ok (no pending writes)")
        return 0

    if would_change:
        CIGARS.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"updated {len(changed)} cigars: {', '.join(changed)}")
    else:
        print("no changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
