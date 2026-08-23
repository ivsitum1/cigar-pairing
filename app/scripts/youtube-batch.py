#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run YouTube pipeline steps for one or all enabled channels (local ops).

Usage:
  python scripts/youtube-batch.py inventory --all-enabled
  python scripts/youtube-batch.py captions --all-enabled
  python scripts/youtube-batch.py classify --all-enabled
  python scripts/youtube-batch.py match-cigars --all-enabled
  python scripts/youtube-batch.py summarize-cigars
  python scripts/youtube-batch.py all --all-enabled
  python scripts/youtube-batch.py inventory --channel cigarsdaily
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path

from youtube_common import load_channels

HERE = Path(__file__).resolve().parent

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

STEPS = {
    "inventory": "youtube-inventory.py",
    "captions": "youtube-fetch-captions.py",
    "classify": "youtube-classify.py",
    "match-rums": "youtube-match-rums.py",
    "match-cigars": "youtube-match-cigars.py",
    "summarize-cigars": "summarize-youtube-cigar-proposals.py",
}

# Steps that take --channel; summarize is global across all proposal files.
CHANNEL_STEPS = frozenset(
    {"inventory", "captions", "classify", "match-rums", "match-cigars"}
)


def resolve_channels(args: argparse.Namespace) -> list[str]:
    if args.channel:
        return [args.channel]
    if args.all_enabled:
        return [
            ch["id"]
            for ch in sorted(load_channels(), key=lambda c: (c.get("priority", 99), c["id"]))
            if ch.get("enabled", True)
        ]
    raise SystemExit("Pass --channel <id> or --all-enabled")


def run_channel_step(step: str, channel_id: str, extra: list[str]) -> int:
    script = HERE / STEPS[step]
    cmd = [sys.executable, str(script), "--channel", channel_id, *extra]
    print(f"\n=== {step} / {channel_id} ===", flush=True)
    return subprocess.run(cmd, cwd=HERE).returncode


def run_global_step(step: str, extra: list[str]) -> int:
    script = HERE / STEPS[step]
    cmd = [sys.executable, str(script), *extra]
    print(f"\n=== {step} (global) ===", flush=True)
    return subprocess.run(cmd, cwd=HERE).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch YouTube corpus pipeline")
    parser.add_argument(
        "step",
        choices=[
            "inventory",
            "captions",
            "classify",
            "match-rums",
            "match-cigars",
            "summarize-cigars",
            "all",
        ],
    )
    parser.add_argument("--channel", help="Single registry channel id")
    parser.add_argument("--all-enabled", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="Per-channel video limit")
    parser.add_argument("--force", action="store_true", help="Captions: re-fetch ok")
    parser.add_argument(
        "--cookies-from-browser",
        default=None,
        help="Captions: yt-dlp --cookies-from-browser (e.g. chrome) — often broken on Chrome 127+",
    )
    parser.add_argument(
        "--cookies",
        default=None,
        help="Captions: Netscape cookies.txt (export from browser extension)",
    )
    parser.add_argument("--prefer-stubs", action="store_true", help="Summarize: stubs only")
    args = parser.parse_args()

    caption_extra: list[str] = []
    if args.limit is not None:
        caption_extra.extend(["--limit", str(args.limit)])
    if args.force:
        caption_extra.append("--force")
    if args.cookies:
        cookies_path = Path(args.cookies)
        if not cookies_path.is_file():
            for candidate in (Path.cwd() / args.cookies, HERE / args.cookies, HERE.parent / args.cookies):
                if candidate.is_file():
                    cookies_path = candidate
                    break
        if not cookies_path.is_file():
            raise SystemExit(f"cookies file not found: {args.cookies}")
        try:
            cookie_arg = cookies_path.resolve().relative_to(HERE.resolve()).as_posix()
        except ValueError:
            cookie_arg = cookies_path.resolve().as_posix()
        caption_extra.extend(["--cookies", cookie_arg])
    elif args.cookies_from_browser:
        caption_extra.extend(["--cookies-from-browser", args.cookies_from_browser])

    summarize_extra: list[str] = []
    if args.prefer_stubs:
        summarize_extra.append("--prefer-stubs")

    steps = (
        [
            "inventory",
            "captions",
            "classify",
            "match-rums",
            "match-cigars",
            "summarize-cigars",
        ]
        if args.step == "all"
        else [args.step]
    )

    # summarize-cigars alone does not need a channel list
    needs_channels = any(s in CHANNEL_STEPS for s in steps)
    channels = resolve_channels(args) if needs_channels else []

    failures = 0
    for step in steps:
        if step == "summarize-cigars":
            code = run_global_step(step, summarize_extra)
            if code != 0:
                failures += 1
                print(f"FAILED {step} (exit {code})", flush=True)
            continue
        for channel_id in channels:
            extra = caption_extra if step == "captions" else []
            code = run_channel_step(step, channel_id, extra)
            if code != 0:
                failures += 1
                print(f"FAILED {step} {channel_id} (exit {code})", flush=True)

    n = len(channels) if channels else 1
    print(f"\nBatch done: {n} channel pass(es), {failures} failure(s)", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
