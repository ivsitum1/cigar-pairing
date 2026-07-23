#!/usr/bin/env python3
"""Lite learning hook — append session markers to .agent/learning.jsonl."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
LOG_PATH = WORKSPACE / ".agent" / "learning.jsonl"
SCRIPT = WORKSPACE / "scripts" / "learning_log.py"


def _read_stdin_json() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_input": raw}


def _event_name(payload: dict) -> str:
    for key in ("event", "hook_event_name", "hookEventName", "type"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def _append(event: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event.setdefault("timestamp", datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    event.setdefault("source", "learning_lifecycle.py")
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    payload = _read_stdin_json()
    hook_event = _event_name(payload)
    if hook_event not in {"sessionEnd", "stop"}:
        print(json.dumps({"ok": True, "skipped": hook_event}))
        return 0

    conversation_id = payload.get("conversation_id") or payload.get("conversationId")
    _append(
        {
            "event": "session_marker",
            "hook": hook_event,
            "conversation_id": conversation_id,
            "workspace": WORKSPACE.name,
            "note": "Lite auto layer — pair with LEARNING_BLOCK for rich capture",
        }
    )
    print(json.dumps({"ok": True, "logged": str(LOG_PATH)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
