#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reset age-gate unavailable caption rows to error for cookie retry.

Usage:
  python scripts/youtube-reset-age-gate.py --channel holtscigars
  python scripts/youtube-reset-age-gate.py --all-enabled
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from youtube_common import load_channels, OUTPUT_ROOT

MARKERS = (
    "age-restricted",
    "sign in to confirm your age",
    "confirm your age",
    "cookies-from-browser",
    "login required",
)


def reset_channel(channel_id: str) -> tuple[int, int]:
    root = OUTPUT_ROOT / channel_id
    invp = root / "inventory.json"
    if not invp.is_file():
        return 0, 0

    n = 0
    for vf in (root / "videos").glob("*.json"):
        rec = json.loads(vf.read_text(encoding="utf-8"))
        if rec.get("captionStatus") != "unavailable":
            continue
        err = (rec.get("error") or "").lower()
        if not any(m in err for m in MARKERS):
            continue
        rec["captionStatus"] = "error"
        vf.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        n += 1

    inv = json.loads(invp.read_text(encoding="utf-8"))
    changed = 0
    for row in inv.get("videos") or []:
        vf = root / "videos" / f"{row['videoId']}.json"
        if not vf.is_file():
            continue
        rec = json.loads(vf.read_text(encoding="utf-8"))
        st = rec.get("captionStatus")
        if row.get("captionStatus") != st:
            row["captionStatus"] = st
            row["captionSource"] = rec.get("captionSource") or "none"
            changed += 1
    invp.write_text(json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return n, changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset age-gate unavailable → error")
    parser.add_argument("--channel")
    parser.add_argument("--all-enabled", action="store_true")
    args = parser.parse_args()

    if args.channel:
        channels = [args.channel]
    elif args.all_enabled:
        channels = [
            ch["id"]
            for ch in sorted(load_channels(), key=lambda c: (c.get("priority", 99), c["id"]))
            if ch.get("enabled", True)
        ]
    else:
        raise SystemExit("Pass --channel <id> or --all-enabled")

    total_v = total_i = 0
    for cid in channels:
        v, i = reset_channel(cid)
        if v or i:
            print(f"{cid}: reset_videos={v} inventory_sync={i}")
        total_v += v
        total_i += i
    print(f"done reset_videos={total_v} inventory_sync={total_i}")


if __name__ == "__main__":
    main()
