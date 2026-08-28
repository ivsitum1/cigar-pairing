#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply YouTube corpus-backed notes to drinks that have a dedicated review match.

Profile fields still come from *_shared heuristics when thin; notes/cigarHint prefer
corpus material when transcript around the bottle name is substantial.

  python scripts/enrich-drinks-from-corpus.py --dry-run
  python scripts/enrich-drinks-from-corpus.py --apply
  python scripts/enrich-drinks-from-corpus.py --apply --category rum
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import youtube_corpus_enrich_lib as yce  # noqa: E402

DATA = HERE.parent / "src" / "data"

FILES = {
    "rum": "rums.json",
    "whisky": "whiskies.json",
    "brandy": "brandies.json",
    "gin": "gins.json",
    "tequila": "tequilas.json",
    "digestif": "digestifs.json",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--category", default="", choices=[""] + list(FILES))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only-shop-ingest", action="store_true")
    args = ap.parse_args()
    if not args.apply:
        args.dry_run = True

    if not yce.CORPUS_BUNDLE.is_file():
        print(f"Missing corpus bundle: {yce.CORPUS_BUNDLE}", file=sys.stderr)
        print("Run: python scripts/youtube-distill-corpus.py", file=sys.stderr)
        return 1

    cats = [args.category] if args.category else list(FILES)
    matched = 0
    changed = 0
    for cat in cats:
        path = DATA / FILES[cat]
        rows = json.loads(path.read_text(encoding="utf-8"))
        file_changed = 0
        cat_matched = 0
        for d in rows:
            if args.only_shop_ingest and not d.get("shopIngest"):
                continue
            hit = yce.try_corpus_enrich(d, cat)
            if not hit:
                continue
            cat_matched += 1
            matched += 1
            before = json.dumps(d, sort_keys=True, ensure_ascii=False)
            yce.apply_corpus_patch(d, hit)
            after = json.dumps(d, sort_keys=True, ensure_ascii=False)
            if before != after:
                file_changed += 1
                changed += 1
            if args.limit and changed >= args.limit:
                break
        print(f"{FILES[cat]}: corpus matches={cat_matched} updated={file_changed}")
        if args.apply and file_changed:
            path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.limit and changed >= args.limit:
            break

    print(f"total corpus_matched={matched} changed={changed}")
    if args.dry_run:
        print("dry-run: not writing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
