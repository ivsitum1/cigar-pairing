#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify inventoried videos (heuristic tags).

Usage:
  python scripts/youtube-classify.py --channel stevethebarmanuk
"""
from __future__ import annotations

import argparse
import io
import sys

from youtube_classify_lib import classify_video, summarize_tags
from youtube_common import (
    append_log,
    classify_path,
    get_channel,
    load_inventory,
    load_video,
    save_json,
    save_video,
    today_iso,
)

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify YouTube corpus videos")
    parser.add_argument("--channel", required=True)
    args = parser.parse_args()

    get_channel(args.channel)
    inv = load_inventory(args.channel)
    tag_lists: list[list[str]] = []
    rum_ids: list[str] = []
    cigar_ids: list[str] = []
    etiquette_ids: list[str] = []

    for row in inv.get("videos") or []:
        vid = row["videoId"]
        rec = load_video(args.channel, vid)
        if not rec:
            continue
        tags = classify_video(rec.get("title") or "", rec.get("text") or "")
        rec["tags"] = tags
        save_video(rec)
        tag_lists.append(tags)
        if "rum" in tags:
            rum_ids.append(vid)
        if "cigar" in tags:
            cigar_ids.append(vid)
        if "etiquette" in tags:
            etiquette_ids.append(vid)

    summary = {
        "channelId": args.channel,
        "classifiedAt": today_iso(),
        "videoCount": len(tag_lists),
        "tagCounts": summarize_tags(tag_lists),
        "rumVideoIds": rum_ids,
        "cigarVideoIds": cigar_ids,
        "etiquetteVideoIds": etiquette_ids,
    }
    save_json(classify_path(args.channel), summary)
    append_log(
        args.channel,
        f"classify videos={summary['videoCount']} rum={len(rum_ids)} cigar={len(cigar_ids)}",
    )
    print(json_dumps(summary))


def json_dumps(obj: object) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
