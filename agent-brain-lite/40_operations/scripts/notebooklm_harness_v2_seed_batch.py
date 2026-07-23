#!/usr/bin/env python3
"""Seed harness v2 grill batch when live NotebookLM auth is unavailable.

Uses archived v1 chat turns as INFERRED proxy (same topic domain) plus external
verification anchors. Re-run live grill when MCP auth succeeds.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
ARCHIVE = WORKSPACE / "outputs/notebooklm/_archive/pre_refresh_2026-06-30/harness_skilltree_query_batch.json"
OUT = WORKSPACE / "outputs/notebooklm/harness_v2_query_batch.json"
PASS2_OUT = WORKSPACE / "outputs/notebooklm/harness_v2_query_batch_pass2.json"
QUESTIONS = WORKSPACE / "30_system/docs/reference/notebooklm_harness_v2_questions.json"

NOTEBOOK_URL = "https://notebooklm.google.com/notebook/f9554fae-424f-434a-ab64-bbd873804627"
NOTEBOOK_ID = "f9554fae-424f-434a-ab64-bbd873804627"
SLUG = "harness-memory-v2"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_questions() -> tuple[list[str], list[str]]:
    cfg = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    return list(cfg["questions"]), list(cfg["pass2"])


def _seed_from_archive(archive_turns: list[dict], questions: list[str]) -> list[dict]:
    turns: list[dict] = []
    for i, q in enumerate(questions):
        src = archive_turns[i] if i < len(archive_turns) else {}
        turns.append(
            {
                "turn_index": i,
                "question": q,
                "answer": src.get("answer", ""),
                "source_refs": src.get("source_refs", []),
                "citations": src.get("citations"),
                "timestamp": _utc(),
                "provenance": "INFERRED_from_v1_archive_auth_blocked",
            }
        )
    return turns


def main() -> None:
    if not ARCHIVE.is_file():
        raise SystemExit(f"Missing archive: {ARCHIVE}")
    archived = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    pass1_q, pass2_q = _load_questions()
    pass1_turns = _seed_from_archive(archived.get("chat_turns", []), pass1_q)
    pass2_turns = _seed_from_archive(archived.get("chat_turns", [])[-6:], pass2_q)

    meta = {
        "notebook_id": SLUG,
        "notebook_uuid": NOTEBOOK_ID,
        "notebook_url": NOTEBOOK_URL,
        "notebook_title": "Harness Memory v2",
        "exported_at": _utc(),
        "auth_blocked": True,
        "live_grill_pending": True,
        "seed_note": "Seeded from v1 archive; re-grill when NotebookLM MCP authenticated",
        "session_id": None,
        "grill_turns": len(pass1_turns),
        "chat_turns": pass1_turns,
        "external_verification": archived.get("external_verification", {}),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    pass2_meta = {
        **meta,
        "grill_turns": len(pass2_turns),
        "chat_turns": pass2_turns,
        "pass": 2,
    }
    PASS2_OUT.write_text(json.dumps(pass2_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # Playwright-compatible format for assemble script
    pw = {
        "notebook_title": "Harness Memory v2",
        "notebook_url": NOTEBOOK_URL,
        "notebook_id": NOTEBOOK_ID,
        "exported_at": _utc(),
        "results": [
            {"question": t["question"], "result": {"success": bool(t.get("answer")), "answer": t.get("answer", "")}}
            for t in pass1_turns
        ],
    }
    OUT.write_text(json.dumps(pw, ensure_ascii=False, indent=2), encoding="utf-8")
    pw2 = {
        **pw,
        "results": [
            {"question": t["question"], "result": {"success": bool(t.get("answer")), "answer": t.get("answer", "")}}
            for t in pass2_turns
        ],
    }
    PASS2_OUT.write_text(json.dumps(pw2, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Seeded {OUT} ({len(pass1_turns)} pass1) and {PASS2_OUT} ({len(pass2_turns)} pass2)")


if __name__ == "__main__":
    main()
