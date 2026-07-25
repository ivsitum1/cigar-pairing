#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build flavor-enrichment worklist.

  python scripts/build-flavor-worklist.py           # batch 1: thin notes/tags
  python scripts/build-flavor-worklist.py --batch 2 # profileEstimated + CigarWorld URL
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output" / "flavor_enrich_worklist.json"


def cw_url(c: dict) -> str | None:
    eu = (c.get("regionLinks") or {}).get("EU") or {}
    u = eu.get("url") or ""
    if "cigarworld.de" in u:
        return u
    for v in c.get("vitolas") or []:
        vu = ((v.get("regionLinks") or {}).get("EU") or {}).get("url") or ""
        if "cigarworld.de" in vu:
            return vu
        if "cigarworld.de" in (v.get("url") or ""):
            return v["url"]
    return None


def row(c: dict) -> dict:
    hr = ((c.get("notes") or {}).get("hr") or "").strip()
    tags = c.get("flavorTags") or []
    return {
        "id": c["id"],
        "brand": c.get("brand"),
        "line": c.get("line"),
        "notes_len": len(hr),
        "tag_count": len(tags),
        "wrapper": c.get("wrapper"),
        "profileEstimated": c.get("profileEstimated"),
        "cw_url": cw_url(c),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, choices=(1, 2), default=1)
    args = ap.parse_args()

    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    items: list[dict] = []
    for c in cigars:
        if args.batch == 1:
            hr = ((c.get("notes") or {}).get("hr") or "").strip()
            tags = c.get("flavorTags") or []
            if len(hr) >= 40 and len(tags) >= 2:
                continue
            items.append(row(c))
        else:
            if c.get("profileEstimated") is not True:
                continue
            if not cw_url(c):
                continue
            items.append(row(c))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with_cw = sum(1 for t in items if t["cw_url"])
    print(f"batch={args.batch} count={len(items)} with_cw={with_cw} -> {OUT}")


if __name__ == "__main__":
    main()
