#!/usr/bin/env python3
"""Assemble NotebookLM grill batch for Harness Memory v2 notebook."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
if str(WORKSPACE / "40_operations" / "python") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

NOTEBOOK_URL = "https://notebooklm.google.com/notebook/f9554fae-424f-434a-ab64-bbd873804627"
NOTEBOOK_ID = "f9554fae-424f-434a-ab64-bbd873804627"
SLUG = "harness-memory-v2"
QUESTIONS_CFG = WORKSPACE / "30_system/docs/reference/notebooklm_harness_v2_questions.json"
PLAYWRIGHT_OUT = WORKSPACE / "outputs/notebooklm/harness_v2_query_batch.json"
PASS2_OUT = WORKSPACE / "outputs/notebooklm/harness_v2_query_batch_pass2.json"
MERGED_OUT = WORKSPACE / "outputs/notebooklm/harness_v2_query_batch_merged.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_cfg() -> dict:
    return json.loads(QUESTIONS_CFG.read_text(encoding="utf-8"))


def _playwright_to_turns(payload: dict) -> list[dict]:
    turns: list[dict] = []
    for i, item in enumerate(payload.get("results") or []):
        if not item:
            continue
        result = item.get("result") or {}
        turns.append(
            {
                "turn_index": i,
                "question": item.get("question", ""),
                "answer": result.get("answer", ""),
                "success": result.get("success", False),
                "source_refs": [],
                "timestamp": payload.get("exported_at"),
            }
        )
    return turns


def merge_batches() -> dict:
    cfg = _load_cfg()
    pass1_turns = _playwright_to_turns(
        json.loads(PLAYWRIGHT_OUT.read_text(encoding="utf-8"))
    ) if PLAYWRIGHT_OUT.is_file() else []
    pass2_turns: list[dict] = []
    if PASS2_OUT.is_file():
        pass2_turns = _playwright_to_turns(json.loads(PASS2_OUT.read_text(encoding="utf-8")))
        for j, t in enumerate(pass2_turns):
            t["turn_index"] = len(pass1_turns) + j

    title = "Harness Memory v2"
    if PLAYWRIGHT_OUT.is_file():
        title = json.loads(PLAYWRIGHT_OUT.read_text(encoding="utf-8")).get("notebook_title") or title

    return {
        "notebook_id": SLUG,
        "notebook_uuid": NOTEBOOK_ID,
        "notebook_url": NOTEBOOK_URL,
        "notebook_title": title,
        "exported_at": _utc_now(),
        "grill_turns": len(pass1_turns) + len(pass2_turns),
        "chat_turns": pass1_turns + pass2_turns,
        "pass1_count": len(pass1_turns),
        "pass2_count": len(pass2_turns),
        "external_verification": {},
        "questions_config": str(QUESTIONS_CFG.relative_to(WORKSPACE)),
    }


def main() -> None:
    merged = merge_batches()
    MERGED_OUT.parent.mkdir(parents=True, exist_ok=True)
    MERGED_OUT.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {MERGED_OUT} ({merged['grill_turns']} turns)")


if __name__ == "__main__":
    main()
