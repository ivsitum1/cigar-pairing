#!/usr/bin/env python3
"""Normalize user notebook grill results for notebooklm_bridge gate-report."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
IN_PATH = WORKSPACE / "outputs" / "notebooklm" / "user_notebook_91614142_query_batch.json"
OUT_PATH = WORKSPACE / "outputs" / "notebooklm" / "user_notebook_91614142_normalized.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize(data: dict) -> dict:
    turns: list[dict] = []
    if "chat_turns" in data:
        turns = data["chat_turns"]
    elif "results" in data:
        for i, item in enumerate(data["results"]):
            if not item:
                continue
            r = item.get("result") or {}
            if not r.get("success"):
                continue
            turns.append(
                {
                    "turn_index": i,
                    "question": item.get("question", ""),
                    "answer": r.get("answer", ""),
                    "source_refs": r.get("source_refs"),
                    "citations": r.get("citations"),
                }
            )
    return {
        "notebook_id": "user-notebook-91614142",
        "notebook_uuid": "91614142-303b-45b8-ad5c-91ee60b66e06",
        "notebook_title": data.get("notebook_title", ""),
        "notebook_url": data.get(
            "notebook_url",
            "https://notebooklm.google.com/notebook/91614142-303b-45b8-ad5c-91ee60b66e06",
        ),
        "exported_at": data.get("exported_at") or _utc_now(),
        "chat_turns": turns,
    }


def main() -> int:
    if not IN_PATH.is_file():
        payload = normalize({"results": []})
        payload["auth_pending"] = True
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"No grill batch at {IN_PATH}; wrote empty normalized stub", file=sys.stderr)
        print(OUT_PATH)
        return 0
    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    payload = normalize(data)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(payload['chat_turns'])} turns)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
