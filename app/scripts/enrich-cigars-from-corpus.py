#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply YouTube corpus-backed notes to cigars with dedicated review matches.

  python scripts/enrich-cigars-from-corpus.py --dry-run
  python scripts/enrich-cigars-from-corpus.py --apply
  python scripts/enrich-cigars-from-corpus.py --apply --only-stubs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import youtube_corpus_enrich_lib as yce  # noqa: E402

CIGARS = HERE.parent / "src" / "data" / "cigars.json"


def needs_notes(cigar: dict) -> bool:
    notes = cigar.get("notes") or {}
    hr = (notes.get("hr") if isinstance(notes, dict) else "") or ""
    en = (notes.get("en") if isinstance(notes, dict) else "") or ""
    if len(hr) < 40 or len(en) < 40:
        return True
    if cigar.get("youtubeCorpusEnriched"):
        return False
    return len(hr) < 80


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only-stubs", action="store_true", help="Only cigars with thin/missing notes")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if not args.apply:
        args.dry_run = True

    if not yce.CORPUS_BUNDLE.is_file():
        print(f"Missing corpus bundle: {yce.CORPUS_BUNDLE}", file=sys.stderr)
        return 1

    rows = json.loads(CIGARS.read_text(encoding="utf-8"))
    matched = 0
    changed = 0
    for c in rows:
        if args.only_stubs and not needs_notes(c):
            continue
        hit = yce.find_corpus_match_cigar(c)
        if not hit:
            continue
        matched += 1
        before = json.dumps(c, sort_keys=True, ensure_ascii=False)
        yce.apply_corpus_patch_cigar(c, hit)
        after = json.dumps(c, sort_keys=True, ensure_ascii=False)
        if before != after:
            changed += 1
        if args.limit and changed >= args.limit:
            break

    print(f"cigars.json: corpus matches={matched} updated={changed}")
    if args.apply and changed:
        CIGARS.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {CIGARS}")
    elif args.dry_run:
        print("dry-run: not writing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
