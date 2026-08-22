#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch EN captions for inventoried videos (no media download).

Usage:
  python scripts/youtube-fetch-captions.py --channel stevethebarmanuk --limit 5
  python scripts/youtube-fetch-captions.py --channel stevethebarmanuk
  python scripts/youtube-fetch-captions.py --channel stevethebarmanuk --force
  python scripts/youtube-fetch-captions.py --channel stevethebarmanuk --resolve-pending
"""
from __future__ import annotations

import argparse
import io
import sys
import tempfile
import time
from pathlib import Path

from youtube_common import (
    append_log,
    empty_video_record,
    ensure_yt_dlp,
    get_channel,
    is_access_denied_error,
    load_inventory,
    load_video,
    run_yt_dlp,
    save_inventory,
    save_video,
    today_iso,
    vtt_to_plain,
)

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PAUSE_S = 1.5
MAX_BACKOFF_S = 60


def _pick_vtt(tmpdir: Path) -> tuple[Path | None, str]:
    """Return (path, source) where source is manual|auto."""
    manuals = list(tmpdir.glob("*.en.vtt")) + list(tmpdir.glob("*.en-*.vtt"))
    manuals = [p for p in manuals if ".auto." not in p.name and "auto" not in p.stem.split(".")]
    auto_named = [p for p in tmpdir.glob("*.vtt") if "auto" in p.name.lower()]
    if manuals:
        return manuals[0], "manual"
    if auto_named:
        return auto_named[0], "auto"
    all_vtt = list(tmpdir.glob("*.vtt"))
    if all_vtt:
        return all_vtt[0], "auto"
    return None, "none"


def fetch_captions_for_video(
    video_id: str,
    *,
    cookies_from_browser: str | None = None,
) -> tuple[str, str, str | None]:
    """Returns (status, source, text_or_error). status: ok|missing|error|unavailable."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory(prefix="ytcap_") as td:
        outtmpl = str(Path(td) / "%(id)s")
        args = [
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "en.*,en",
            "--sub-format",
            "vtt",
            "--no-warnings",
            "-o",
            outtmpl,
        ]
        if cookies_from_browser:
            args.extend(["--cookies-from-browser", cookies_from_browser])
        args.append(url)
        proc = run_yt_dlp(args, timeout=180)
        path, source = _pick_vtt(Path(td))
        if path and path.exists():
            plain = vtt_to_plain(path.read_text(encoding="utf-8", errors="replace"))
            if plain:
                return "ok", source, plain
        err = (proc.stderr or proc.stdout or "").strip()[:400]
        if is_access_denied_error(err):
            return "unavailable", "none", err or "access denied"
        if proc.returncode != 0:
            if "There are no subtitles" in err or "no subtitles" in err.lower():
                return "missing", "none", None
            return "error", "none", err or "yt-dlp failed"
        return "missing", "none", None


def mark_unavailable(rec: dict, reason: str | None) -> None:
    rec["captionStatus"] = "unavailable"
    rec["captionSource"] = "none"
    rec["captionLang"] = None
    rec["text"] = ""
    rec["fetchedAt"] = today_iso()
    rec["error"] = reason


def should_process(rec: dict, *, force: bool, resolve_pending: bool) -> bool:
    status = rec.get("captionStatus") or "missing"
    if force:
        return True
    if status == "ok" or status == "unavailable":
        return False
    if resolve_pending:
        return status in ("missing", "error")
    # Default resume: skip ok/unavailable; retry missing/error
    return status in ("missing", "error", None, "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch YouTube EN captions")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Re-fetch even if ok")
    parser.add_argument(
        "--resolve-pending",
        action="store_true",
        help="Only missing/error: members-only→unavailable offline; else re-fetch",
    )
    parser.add_argument("--pause", type=float, default=PAUSE_S)
    parser.add_argument(
        "--cookies-from-browser",
        default=None,
        help="Pass through to yt-dlp (e.g. chrome, edge) for age-gated videos",
    )
    args = parser.parse_args()

    ensure_yt_dlp()
    get_channel(args.channel)
    inv = load_inventory(args.channel)
    videos = list(inv.get("videos") or [])
    if not videos:
        raise SystemExit("Empty inventory — run youtube-inventory.py first")

    done = 0
    ok = missing = errors = skipped = unavailable = offline_unavail = 0
    backoff = args.pause

    for row in videos:
        if args.limit is not None and done >= args.limit:
            break
        vid = row["videoId"]
        rec = load_video(args.channel, vid) or empty_video_record(
            video_id=vid,
            channel_id=args.channel,
            title=row.get("title") or "",
            uploaded_at=row.get("uploadedAt"),
            duration_sec=row.get("durationSec"),
        )
        if not should_process(rec, force=args.force, resolve_pending=args.resolve_pending):
            skipped += 1
            continue

        # Offline close-out for known members-only / private errors
        if rec.get("captionStatus") == "error" and is_access_denied_error(rec.get("error")):
            mark_unavailable(rec, rec.get("error"))
            save_video(rec)
            row["captionStatus"] = "unavailable"
            row["captionSource"] = "none"
            offline_unavail += 1
            unavailable += 1
            done += 1
            print(f"  unavailable (offline) {vid}: {(rec.get('title') or '')[:50]}")
            continue

        print(f"  captions {vid}: {rec.get('title', '')[:60]}", flush=True)
        try:
            status, source, payload = fetch_captions_for_video(
                vid,
                cookies_from_browser=args.cookies_from_browser,
            )
        except Exception as e:  # noqa: BLE001 — persist and continue
            status, source, payload = "error", "none", str(e)

        if status == "ok":
            rec["captionStatus"] = "ok"
            rec["captionSource"] = source
            rec["captionLang"] = "en"
            rec["text"] = payload or ""
            rec["fetchedAt"] = today_iso()
            rec["error"] = None
            ok += 1
            backoff = args.pause
        elif status == "missing":
            rec["captionStatus"] = "missing"
            rec["captionSource"] = "none"
            rec["captionLang"] = None
            rec["text"] = ""
            rec["fetchedAt"] = today_iso()
            rec["error"] = None
            missing += 1
            backoff = args.pause
        elif status == "unavailable":
            mark_unavailable(rec, payload)
            unavailable += 1
            backoff = args.pause
            print(f"    UNAVAILABLE: {(payload or '')[:120]}", flush=True)
        else:
            if is_access_denied_error(payload):
                mark_unavailable(rec, payload)
                unavailable += 1
                backoff = args.pause
                print(f"    UNAVAILABLE: {(payload or '')[:120]}", flush=True)
            else:
                rec["captionStatus"] = "error"
                rec["captionSource"] = "none"
                rec["error"] = payload
                errors += 1
                backoff = min(MAX_BACKOFF_S, backoff * 2)
                print(f"    ERROR: {payload}", flush=True)

        if row.get("title") and not rec.get("title"):
            rec["title"] = row["title"]
        save_video(rec)
        row["captionStatus"] = rec["captionStatus"]
        row["captionSource"] = rec["captionSource"]
        done += 1
        time.sleep(backoff)

    save_inventory(args.channel, inv)
    msg = (
        f"captions done={done} ok={ok} missing={missing} errors={errors} "
        f"unavailable={unavailable} offline_unavail={offline_unavail} skipped={skipped}"
    )
    append_log(args.channel, msg)
    print(msg, flush=True)


if __name__ == "__main__":
    main()
