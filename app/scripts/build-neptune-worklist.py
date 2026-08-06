#!/usr/bin/env python3
"""Build a worklist of Neptune Cigar URLs for cigars needing shop profiles.

Output: scripts/output/neptune_worklist.json
  [{
    "id":       "cig-aging-room-quattro-f55",
    "brand":    "Aging Room",
    "line":     "Quattro F55",
    "url":      "https://www.neptunecigar.com/cigars/aging-room-quattro-f55-concerto",
    "vitola":   "Concerto"
  }, ...]

Selection rules:
  - No flavorTags, OR profileEstimated==True (heuristic stubs — shop text
    should overwrite them via merge-neptune-profiles.py)
  - At least one vitola has a neptune URL
  - Pick the first neptune URL found (any vitola)

For multi-vitola records folded by fold-market-vitolas.py, the first vitola's
URL is the one actually scraped; merge-neptune-profiles.py applies the result
to the whole line.

Usage (run from app/):
  python scripts/build-neptune-worklist.py
  python scripts/build-neptune-worklist.py --check   # exit 1 if worklist stale
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taxonomy_lib import CIGARS_PATH, OUT_DIR, load_json, write_json  # noqa: E402

OUT = OUT_DIR / "neptune_worklist.json"
NEPTUNE_HOST = "neptunecigar.com"


def _neptune_url(c: dict) -> tuple[str | None, str | None]:
    """Return (first neptune URL, vitola name) for the record, or (None, None)."""
    for vit in c.get("vitolas") or []:
        u = vit.get("url") or ""
        if NEPTUNE_HOST in u:
            return u, vit.get("name")
    return None, None


def _needs_shop_profile(c: dict) -> bool:
    """True when the record has no tags or only a heuristic estimated profile."""
    if not c.get("flavorTags"):
        return True
    return c.get("profileEstimated") is True


def build(cigars: list) -> list:
    items = []
    for c in cigars:
        if not _needs_shop_profile(c):
            continue
        url, vname = _neptune_url(c)
        if not url:
            continue
        items.append(
            {
                "id": c["id"],
                "brand": c.get("brand") or "",
                "line": c.get("line") or "",
                "vitola": vname or "",
                "url": url,
            }
        )
    return items


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="Exit 1 if worklist is stale")
    args = ap.parse_args()

    cigars = json.loads(CIGARS_PATH.read_text(encoding="utf-8"))
    items = build(cigars)

    if args.check:
        existing = load_json(OUT, None)
        if existing is None:
            print("neptune_worklist.json missing — run without --check", file=sys.stderr)
            sys.exit(1)
        if json.dumps(items, ensure_ascii=False) != json.dumps(existing, ensure_ascii=False):
            print("neptune_worklist.json stale — run without --check to regenerate", file=sys.stderr)
            sys.exit(1)
        print(f"neptune_worklist.json up to date ({len(items)} items)")
        return 0

    write_json(OUT, items)
    print(f"Wrote {OUT} ({len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
