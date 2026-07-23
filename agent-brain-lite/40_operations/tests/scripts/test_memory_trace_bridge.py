"""Tests for memory_trace_bridge (AutoMem trajectory → solved_lemmas)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parents[3]
SCRIPTS = WORKSPACE / "40_operations" / "scripts"
sys_path = WORKSPACE / "40_operations" / "python"
import sys

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(sys_path) not in sys.path:
    sys.path.insert(0, str(sys_path))

import memory_trace_bridge as mtb  # noqa: E402


def test_is_successful_memory_event_memory_op() -> None:
    event = {"event_type": "tool_result", "payload": {"memory_op": "write", "success": True}}
    assert mtb._is_successful_memory_event(event) is True


def test_is_successful_memory_event_context_sync_tool() -> None:
    event = {
        "event_type": "tool_result",
        "payload": {"tool_name": "context_sync", "exit_code": 0},
    }
    assert mtb._is_successful_memory_event(event) is True


def test_lemma_from_event(tmp_path: Path) -> None:
    trace = tmp_path / "trajectory.jsonl"
    trace.write_text("", encoding="utf-8")
    event = {
        "ts": "2026-07-05T08:00:00Z",
        "event_type": "tool_result",
        "payload": {"memory_op": "fold", "subgoal": "Test subgoal", "summary": "Fold ok"},
    }
    lemma = mtb._lemma_from_event(event, trace)
    assert lemma is not None
    assert lemma["subgoal"] == "Test subgoal"
    assert "Fold ok" in lemma["summary"]


def test_scan_and_promote_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trace_dir = tmp_path / "run_demo"
    trace_dir.mkdir()
    trace = trace_dir / "trajectory.jsonl"
    event = {
        "ts": "2026-07-05T08:00:00Z",
        "event_type": "tool_result",
        "payload": {
            "memory_op": "write",
            "subgoal": "Unique promote test",
            "summary": "Memory write succeeded",
            "success": True,
        },
    }
    trace.write_text(json.dumps(event) + "\n", encoding="utf-8")

    solved = tmp_path / "solved_lemmas.jsonl"
    monkeypatch.setattr(mtb, "SOLVED_LEMMAS", solved)
    monkeypatch.setattr(mtb, "ARTIFACTS_DIR", tmp_path / "artifacts_missing")

    result = mtb.promote(dry_run=True, extra_paths=[trace])
    assert result["candidates"] >= 1
    assert result["promoted"] >= 1
    assert not solved.exists()
