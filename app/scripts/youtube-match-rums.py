#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Propose rum catalog matches from classified videos (does not write rums.json).

Usage:
  python scripts/youtube-match-rums.py --channel stevethebarmanuk
"""
from __future__ import annotations

import argparse
import io
import json
import sys

from youtube_common import (
    RUMS_PATH,
    append_log,
    get_channel,
    load_inventory,
    load_json,
    load_video,
    proposals_path,
    save_json,
    today_iso,
)
from youtube_match_lib import match_video_to_rums

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="Match YouTube rum videos to rums.json")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--min-confidence", type=float, default=0.65)
    parser.add_argument(
        "--all-videos",
        action="store_true",
        help="Match all videos, not only those tagged rum",
    )
    args = parser.parse_args()

    get_channel(args.channel)
    rums = load_json(RUMS_PATH, [])
    if not isinstance(rums, list) or not rums:
        raise SystemExit(f"No rums loaded from {RUMS_PATH}")

    inv = load_inventory(args.channel)
    proposals: list[dict] = []
    scanned = 0

    for row in inv.get("videos") or []:
        vid = row["videoId"]
        rec = load_video(args.channel, vid)
        if not rec:
            continue
        tags = rec.get("tags") or []
        if not args.all_videos and "rum" not in tags:
            # Still allow title-only rum brand hits when tagged skip but name matches
            title_l = (rec.get("title") or "").lower()
            if "rum" not in title_l and "rhum" not in title_l and "ron " not in title_l:
                continue
        scanned += 1
        proposals.extend(
            match_video_to_rums(
                video=rec,
                rums=rums,
                min_confidence=args.min_confidence,
            )
        )

    out = {
        "channelId": args.channel,
        "matchedAt": today_iso(),
        "scannedVideos": scanned,
        "proposalCount": len(proposals),
        "proposals": proposals,
        "note": "Review only — do not auto-merge into rums.json. Do not change additive* from YouTube alone.",
    }
    save_json(proposals_path(args.channel), out)
    append_log(args.channel, f"match scanned={scanned} proposals={len(proposals)}")
    print(json.dumps({"scannedVideos": scanned, "proposalCount": len(proposals)}, indent=2))


if __name__ == "__main__":
    main()
