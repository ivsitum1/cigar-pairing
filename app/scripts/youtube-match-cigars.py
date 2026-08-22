#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Propose cigar catalog matches from classified videos (does not write cigars.json).

Usage:
  python scripts/youtube-match-cigars.py --channel cigarsdaily
  python scripts/youtube-match-cigars.py --channel cigarsdaily --all-videos
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys

from youtube_common import (
    CIGARS_PATH,
    append_log,
    cigar_proposals_path,
    get_channel,
    load_inventory,
    load_json,
    load_video,
    save_json,
    today_iso,
)
from youtube_match_cigar_lib import match_video_to_cigars

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_CIGAR_TITLE_HINT = re.compile(
    r"\b(cigar|cigars|habano|puro|vitola|robusto|toro|corona|maduro|"
    r"connecticut|cohiba|padron|davidoff|oliva|montecristo|partagas|"
    r"rocky\s+patel|my\s+father|tatuaje|drew\s+estate)\b",
    re.I,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Match YouTube cigar videos to cigars.json")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--min-confidence", type=float, default=0.65)
    parser.add_argument(
        "--all-videos",
        action="store_true",
        help="Match all videos, not only those tagged cigar",
    )
    args = parser.parse_args()

    get_channel(args.channel)
    cigars = load_json(CIGARS_PATH, [])
    if not isinstance(cigars, list) or not cigars:
        raise SystemExit(f"No cigars loaded from {CIGARS_PATH}")

    inv = load_inventory(args.channel)
    proposals: list[dict] = []
    scanned = 0

    for row in inv.get("videos") or []:
        vid = row["videoId"]
        rec = load_video(args.channel, vid)
        if not rec:
            continue
        tags = rec.get("tags") or []
        title = rec.get("title") or ""
        if not args.all_videos and "cigar" not in tags:
            if not _CIGAR_TITLE_HINT.search(title):
                continue
        scanned += 1
        proposals.extend(
            match_video_to_cigars(
                video=rec,
                cigars=cigars,
                min_confidence=args.min_confidence,
            )
        )

    out = {
        "channelId": args.channel,
        "matchedAt": today_iso(),
        "scannedVideos": scanned,
        "proposalCount": len(proposals),
        "proposals": proposals,
        "note": "Review only — do not auto-merge into cigars.json. Ship original HR/EN notes, not transcript paste.",
    }
    save_json(cigar_proposals_path(args.channel), out)
    append_log(args.channel, f"cigar-match scanned={scanned} proposals={len(proposals)}")
    print(json.dumps({"scannedVideos": scanned, "proposalCount": len(proposals)}, indent=2))


if __name__ == "__main__":
    main()
