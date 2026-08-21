#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build / refresh YouTube channel inventory (metadata only).

Usage:
  python scripts/youtube-inventory.py --channel stevethebarmanuk
  python scripts/youtube-inventory.py --channel stevethebarmanuk --limit 5
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from typing import Any

from youtube_common import (
    append_log,
    empty_video_record,
    ensure_yt_dlp,
    get_channel,
    load_inventory,
    load_video,
    run_yt_dlp,
    save_inventory,
    save_video,
    today_iso,
)

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _parse_upload_date(raw: Any) -> str | None:
    if not raw:
        return None
    s = str(raw)
    if len(s) == 8 and s.isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return s[:10] if len(s) >= 10 else s


def fetch_flat_entries(channel_url: str, limit: int | None) -> list[dict[str, Any]]:
    url = channel_url.rstrip("/") + "/videos"
    args = [
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        "--ignore-errors",
    ]
    if limit is not None:
        args.extend(["--playlist-end", str(limit)])
    args.append(url)
    proc = run_yt_dlp(args, timeout=600)
    if proc.returncode not in (0, 1):
        # yt-dlp may return 1 with partial playlist; still try to parse stdout
        sys.stderr.write(proc.stderr or "")
    entries: list[dict[str, Any]] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not entries and proc.returncode != 0:
        raise SystemExit(
            f"yt-dlp inventory failed (code {proc.returncode}):\n{proc.stderr}"
        )
    return entries


def merge_inventory(
    channel_id: str,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    inv = load_inventory(channel_id)
    by_id: dict[str, dict[str, Any]] = {
        v["videoId"]: v for v in inv.get("videos") or [] if v.get("videoId")
    }

    for entry in entries:
        vid = entry.get("id") or entry.get("url")
        if not vid:
            continue
        vid = str(vid)
        if vid.startswith("http"):
            # rare flat form
            continue
        title = entry.get("title") or entry.get("fulltitle") or ""
        duration = entry.get("duration")
        duration_sec = int(duration) if isinstance(duration, (int, float)) else None
        uploaded = _parse_upload_date(entry.get("upload_date") or entry.get("release_date"))

        prev = by_id.get(vid) or {}
        row = {
            "videoId": vid,
            "title": title or prev.get("title") or "",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "uploadedAt": uploaded or prev.get("uploadedAt"),
            "durationSec": duration_sec if duration_sec is not None else prev.get("durationSec"),
            "captionStatus": prev.get("captionStatus", "missing"),
            "captionSource": prev.get("captionSource", "none"),
        }
        by_id[vid] = row

        existing = load_video(channel_id, vid)
        if existing is None:
            save_video(
                empty_video_record(
                    video_id=vid,
                    channel_id=channel_id,
                    title=row["title"],
                    uploaded_at=row.get("uploadedAt"),
                    duration_sec=row.get("durationSec"),
                )
            )
        else:
            existing["title"] = row["title"] or existing.get("title")
            if row.get("uploadedAt"):
                existing["uploadedAt"] = row["uploadedAt"]
            if row.get("durationSec") is not None:
                existing["durationSec"] = row["durationSec"]
            save_video(existing)

    inv["channelId"] = channel_id
    inv["fetchedAt"] = today_iso()
    inv["videos"] = sorted(by_id.values(), key=lambda v: v.get("videoId") or "")
    return inv


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube channel inventory (metadata)")
    parser.add_argument("--channel", required=True, help="Registry channel id")
    parser.add_argument("--limit", type=int, default=None, help="Max videos (smoke)")
    args = parser.parse_args()

    ensure_yt_dlp()
    ch = get_channel(args.channel)
    if not ch.get("enabled", True):
        raise SystemExit(f"Channel {args.channel} is disabled in registry")

    print(f"Inventory: {ch.get('handle') or ch['id']} …")
    entries = fetch_flat_entries(ch["url"], args.limit)
    print(f"  flat entries: {len(entries)}")
    inv = merge_inventory(args.channel, entries)
    save_inventory(args.channel, inv)
    append_log(args.channel, f"inventory videos={len(inv['videos'])} limit={args.limit}")
    print(f"Saved {len(inv['videos'])} videos → output/youtube/{args.channel}/inventory.json")


if __name__ == "__main__":
    main()
