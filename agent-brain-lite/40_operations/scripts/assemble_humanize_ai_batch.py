#!/usr/bin/env python3
"""Assemble NotebookLM grill batch from MCP response JSON files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
import sys

if str(WORKSPACE / "40_operations" / "python") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))
from common.cursor_paths import cursor_agent_tools_dir

AGENT_TOOLS = cursor_agent_tools_dir(WORKSPACE) or (WORKSPACE / "outputs" / "notebooklm" / "_agent_tools_stub")
OUT = WORKSPACE / "outputs" / "notebooklm" / "humanize_ai_query_batch.json"

# MCP tool output files in call order (question embedded in each file)
TOOL_FILES = [
    "eb88e1f6-9b99-4878-aa11-d89f60991c29.txt",
    "d4e2306a-e523-4e9e-8525-a5cb688ac43d.txt",
    "1d3877df-357a-4618-9e5e-23e5ae8d5454.txt",
    "49fa396d-4215-4cf0-b805-16bde48c0d9c.txt",
    "6a868681-0cf5-4256-a7b1-10a36281ce8f.txt",
    "6355dbbc-5ee7-49e4-a520-d30193d4c837.txt",
]

# Q6 tools/thresholds — inlined from successful MCP response
INLINE_TURN = {
    "question": (
        "What AI detection tools and score thresholds does this notebook discuss "
        "(GPTZero, Turnitin, Copyleaks, Originality)? What are typical false positive "
        "rates and limitations? What target AI score is reasonable for academic submission?"
    ),
    "answer": (
        "Institutions use 20-25% as investigation flags. GPTZero uses perplexity and "
        "burstiness; Turnitin allows ~15% cushion; Copyleaks and Originality.ai lead on "
        "raw AI text but struggle with edited/mixed content. False positive rates range "
        "3-17% depending on tool; ESL writers flagged up to 60% in some studies. "
        "Target under 20% for legitimate academic work; maintain draft trail. "
        "Detectors are probabilities, not ground truth."
    ),
    "source_refs": ["HumanizeThisAI", "aidetector.ac", "GPTZero Wikipedia", "OriginalityReport"],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_turn(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = raw.get("data", raw)
    sources = data.get("sources") or []
    return {
        "question": data.get("question", ""),
        "answer": data.get("answer", ""),
        "session_id": data.get("session_id"),
        "source_refs": [s.get("sourceName", "") for s in sources[:8]],
        "citations": sources,
    }


def main() -> None:
    turns: list[dict] = []
    for i, name in enumerate(TOOL_FILES):
        p = AGENT_TOOLS / name
        if not p.is_file():
            raise FileNotFoundError(p)
        turn = _load_turn(p)
        turn["turn_index"] = i
        turn["timestamp"] = _utc_now()
        turns.append(turn)

    turns.append({**INLINE_TURN, "turn_index": len(turns), "timestamp": _utc_now()})

    payload = {
        "notebook_id": "manual-techniques-for-humanizi",
        "notebook_url": "https://notebooklm.google.com/notebook/ac8b47a1-0063-48f2-8a03-29b5f529bbb2",
        "notebook_title": "Manual Techniques for Humanizing AI Content and Bypassing Detectors",
        "exported_at": _utc_now(),
        "session_id": "6f16d478",
        "chat_turns": turns,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(turns)} turns to {OUT}")


if __name__ == "__main__":
    main()
