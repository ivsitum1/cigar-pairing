"""Canonical paths for QuillBot Playwright bridge (local only)."""
from __future__ import annotations

import os
from pathlib import Path

QUILLBOT_HOME = Path(
    os.environ.get("QUILLBOT_HOME", str(Path.home() / ".quillbot"))
).expanduser()
PROFILE_DIR = Path(
    os.environ.get(
        "QUILLBOT_PROFILE_DIR",
        str(QUILLBOT_HOME / "profiles" / "default" / "browser_profile"),
    )
).expanduser()
STORAGE_STATE = Path(
    os.environ.get(
        "QUILLBOT_STORAGE_STATE",
        str(QUILLBOT_HOME / "profiles" / "default" / "storage_state.json"),
    )
).expanduser()
DETECTOR_URL = os.environ.get(
    "QUILLBOT_DETECTOR_URL",
    "https://quillbot.com/ai-content-detector",
).strip()
SETTINGS_URL = os.environ.get(
    "QUILLBOT_SETTINGS_URL",
    "https://quillbot.com/settings?menu=profile",
).strip()
MIN_WORDS = int(os.environ.get("QUILLBOT_MIN_WORDS", "80"))
