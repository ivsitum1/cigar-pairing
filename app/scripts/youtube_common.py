# -*- coding: utf-8 -*-
"""Shared helpers for YouTube inventory / captions pipeline."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CHANNELS_PATH = HERE / "data" / "youtube" / "channels.json"
OUTPUT_ROOT = HERE / "output" / "youtube"
RUMS_PATH = HERE.parent / "src" / "data" / "rums.json"
CIGARS_PATH = HERE.parent / "src" / "data" / "cigars.json"

CaptionStatus = str  # ok | missing | error | unavailable
CaptionSource = str  # manual | auto | none

# Permanent access failures — do not keep retrying without auth/cookies.
_ACCESS_DENIED_MARKERS = (
    "members-only",
    "available to this channel's members",
    "join this channel to get access",
    "private video",
    "this video is private",
    "video unavailable",
    "has been removed",
    "account associated with this video has been terminated",
    # Age-gate / cookie wall — needs --cookies-from-browser to retry
    "sign in to confirm your age",
    "confirm your age",
    "age-restricted",
    "login required",
)


def is_access_denied_error(message: str | None) -> bool:
    text = (message or "").lower()
    return any(m in text for m in _ACCESS_DENIED_MARKERS)


def today_iso() -> str:
    return date.today().isoformat()


def load_channels() -> list[dict[str, Any]]:
    data = json.loads(CHANNELS_PATH.read_text(encoding="utf-8"))
    return list(data.get("channels") or [])


def get_channel(channel_id: str) -> dict[str, Any]:
    for ch in load_channels():
        if ch.get("id") == channel_id:
            return ch
    raise SystemExit(f"Unknown channel id: {channel_id!r} (see {CHANNELS_PATH})")


def channel_dir(channel_id: str) -> Path:
    d = OUTPUT_ROOT / channel_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "videos").mkdir(exist_ok=True)
    return d


def inventory_path(channel_id: str) -> Path:
    return channel_dir(channel_id) / "inventory.json"


def video_path(channel_id: str, video_id: str) -> Path:
    return channel_dir(channel_id) / "videos" / f"{video_id}.json"


def classify_path(channel_id: str) -> Path:
    return channel_dir(channel_id) / "classify.json"


def proposals_path(channel_id: str) -> Path:
    return channel_dir(channel_id) / "rum_match_proposals.json"


def cigar_proposals_path(channel_id: str) -> Path:
    return channel_dir(channel_id) / "cigar_match_proposals.json"


def log_path(channel_id: str) -> Path:
    return channel_dir(channel_id) / "run.log"


def append_log(channel_id: str, message: str) -> None:
    line = f"{today_iso()} {message}\n"
    with log_path(channel_id).open("a", encoding="utf-8") as f:
        f.write(line)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def empty_video_record(
    *,
    video_id: str,
    channel_id: str,
    title: str = "",
    uploaded_at: str | None = None,
    duration_sec: int | None = None,
) -> dict[str, Any]:
    return {
        "videoId": video_id,
        "channelId": channel_id,
        "title": title,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "uploadedAt": uploaded_at,
        "durationSec": duration_sec,
        "captionStatus": "missing",
        "captionSource": "none",
        "captionLang": None,
        "text": "",
        "fetchedAt": None,
        "tags": [],
        "error": None,
    }


def load_video(channel_id: str, video_id: str) -> dict[str, Any] | None:
    path = video_path(channel_id, video_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_video(record: dict[str, Any]) -> None:
    cid = record["channelId"]
    vid = record["videoId"]
    save_json(video_path(cid, vid), record)


def load_inventory(channel_id: str) -> dict[str, Any]:
    return load_json(
        inventory_path(channel_id),
        {"channelId": channel_id, "fetchedAt": None, "videos": []},
    )


def save_inventory(channel_id: str, inventory: dict[str, Any]) -> None:
    save_json(inventory_path(channel_id), inventory)


def vtt_to_plain(vtt: str) -> str:
    """Strip WebVTT timing/meta into plain transcript text."""
    lines: list[str] = []
    seen: set[str] = set()
    for raw in vtt.splitlines():
        line = raw.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        if "-->" in line:
            continue
        if re.match(r"^\d+$", line):
            continue
        # Drop simple cue settings / timestamps leftovers
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"&\w+;", " ", line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line or line in seen:
            continue
        seen.add(line)
        lines.append(line)
    return " ".join(lines).strip()


def run_yt_dlp(args: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "yt_dlp", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def ensure_yt_dlp() -> None:
    try:
        import yt_dlp  # noqa: F401
    except ImportError as e:
        raise SystemExit(
            "yt-dlp is required. Install with: pip install yt-dlp\n"
            f"({e})"
        ) from e
