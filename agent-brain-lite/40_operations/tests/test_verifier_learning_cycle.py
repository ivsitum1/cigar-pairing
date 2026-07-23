"""Tests for automatic verifier learning cycle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

pytest.importorskip("sklearn")

from brain_assist.verifier_learning_cycle import (  # noqa: E402
    labeled_row_count,
    load_state,
    run_learning_cycle,
    should_run_cycle,
)
from brain_assist.verifier_ml import maybe_incremental_train, ml_blend_active  # noqa: E402


def test_should_run_on_session_end():
    ok, reason = should_run_cycle(trigger="sessionEnd")
    assert ok is True
    assert "sessionEnd" in reason


def test_throttled_on_prompt_without_delta(tmp_path, monkeypatch):
    state_path = tmp_path / "state.json"
    monkeypatch.setattr("brain_assist.verifier_learning_cycle.STATE_PATH", state_path)
    state_path.write_text(
        json.dumps(
            {
                "last_cycle_at": "2099-01-01T00:00:00Z",
                "last_cycle_ledger_count": 100,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("brain_assist.verifier_learning_cycle.ledger_event_count", lambda: 101)
    ok, reason = should_run_cycle(trigger="prompt")
    assert ok is False
    assert reason == "throttled"


def test_maybe_incremental_train_accumulating():
    result = maybe_incremental_train()
    assert result.get("reason") in {"accumulating", None} or result.get("ok") is True
    if not result.get("ok"):
        assert "count" in result


def test_run_learning_cycle_skipped_when_throttled(tmp_path, monkeypatch):
    state_path = tmp_path / "state.json"
    progress_path = tmp_path / "progress.json"
    monkeypatch.setattr("brain_assist.verifier_learning_cycle.STATE_PATH", state_path)
    monkeypatch.setattr("brain_assist.verifier_learning_cycle.PROGRESS_PATH", progress_path)
    state_path.write_text(
        json.dumps({"last_cycle_at": "2099-01-01T00:00:00Z", "last_cycle_ledger_count": 9999}),
        encoding="utf-8",
    )
    result = run_learning_cycle(trigger="prompt")
    assert result.get("skipped") is True


def test_labeled_row_count_positive():
    assert labeled_row_count() >= 0


def test_ml_blend_active_without_model_unless_forced(monkeypatch):
    monkeypatch.delenv("VERIFIER_ML_BLEND", raising=False)
    monkeypatch.setattr(
        "brain_assist.verifier_ml.load_model",
        lambda path=None: None,
    )
    assert ml_blend_active() is False
