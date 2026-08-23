#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export etiquette-tagged videos for Writer / bonton research (no caption text).

Writes gitignored: scripts/output/youtube/etiquette_corpus_index.json

Usage: python scripts/youtube-export-etiquette-index.py
"""
from __future__ import annotations

import json
from pathlib import Path

from youtube_common import load_channels, OUTPUT_ROOT, today_iso

TAG = "etiquette"
OUT = OUTPUT_ROOT / "etiquette_corpus_index.json"


def main() -> None:
    entries: list[dict] = []
    for ch in load_channels():
        cid = ch["id"]
        videos_dir = OUTPUT_ROOT / cid / "videos"
        if not videos_dir.is_dir():
            continue
        for vf in sorted(videos_dir.glob("*.json")):
            rec = json.loads(vf.read_text(encoding="utf-8"))
            tags = rec.get("tags") or []
            if TAG not in tags:
                continue
            if rec.get("captionStatus") != "ok":
                continue
            entries.append(
                {
                    "videoId": rec.get("videoId"),
                    "channelId": cid,
                    "channelHandle": ch.get("handle"),
                    "title": rec.get("title"),
                    "url": rec.get("url") or f"https://www.youtube.com/watch?v={rec.get('videoId')}",
                    "uploadedAt": rec.get("uploadedAt"),
                    "durationSec": rec.get("durationSec"),
                }
            )

    payload = {
        "exportedAt": today_iso(),
        "tag": TAG,
        "count": len(entries),
        "videos": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written {OUT} count={len(entries)}")


if __name__ == "__main__":
    main()
