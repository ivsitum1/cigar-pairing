"""Tests for LOOP-4 wiki_nested_loop.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "40_operations" / "scripts"))

import wiki_nested_loop as wnl  # noqa: E402


def test_human_gate_every_third_cycle() -> None:
    assert wnl.human_gate_needed(3) is True
    assert wnl.human_gate_needed(6) is True
    assert wnl.human_gate_needed(2) is False
    assert wnl.human_gate_needed(1) is False


def test_stage_rotation() -> None:
    assert wnl.next_stage_index("") == 0
    assert wnl.STAGES[wnl.next_stage_index("ingest")] == "daily-update"
    assert wnl.STAGES[wnl.next_stage_index("wiki-lint")] == "ingest"


def test_advance_cycle_stops_on_lint(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    slug = "testloop"
    monkeypatch.setattr(wnl, "TASK_DIR", tmp_path)
    state = wnl.LoopState(cycle=0, last_stage="wiki-synthesize")
    wnl.advance_cycle(state, "wiki-lint", lint_errors=99, lint_threshold=50)
    assert state.stopped is True
    assert "lint_errors" in state.stop_reason


def test_plan_step_dry_run(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    slug = "dry"
    monkeypatch.setattr(wnl, "TASK_DIR", tmp_path)
    result = wnl.plan_step(slug, dry_run=True, reset=True)
    assert result["status"] == "ok"
    assert result["stage"] == "ingest"
    assert not (tmp_path / f"loop_{slug}_state.json").exists()


def test_state_roundtrip(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    slug = "round"
    monkeypatch.setattr(wnl, "TASK_DIR", tmp_path)
    wnl.save_state(slug, wnl.LoopState(cycle=2, last_stage="wiki-lint"))
    loaded = wnl.load_state(slug)
    assert loaded.cycle == 2
    assert loaded.last_stage == "wiki-lint"
