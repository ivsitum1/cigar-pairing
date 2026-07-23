"""Tests for episodic-first MEMORY.md consolidation gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from trajectory_rl.emit import (  # noqa: E402
    MILESTONE_FLAG,
    approve_consolidate_eval,
    consolidation_allowed,
    request_milestone_consolidate,
)


def test_consolidation_deferred_by_default():
    if MILESTONE_FLAG.is_file():
        MILESTONE_FLAG.unlink()
    allowed, reason = consolidation_allowed()
    assert allowed is False
    assert "episodic" in reason


def test_milestone_flag_allows_once(tmp_path, monkeypatch):
    monkeypatch.setattr("trajectory_rl.emit.MILESTONE_FLAG", tmp_path / "milestone.flag")
    request_milestone_consolidate(note="test")
    allowed, reason = consolidation_allowed()
    assert allowed is True
    assert reason == "milestone_flag"
    allowed2, _ = consolidation_allowed()
    assert allowed2 is False


def test_eval_approve_allows_once(tmp_path, monkeypatch):
    approve_path = tmp_path / "approve.json"
    monkeypatch.setattr("trajectory_rl.emit.EVAL_APPROVE_FILE", approve_path)
    approve_consolidate_eval(approved_by="test")
    allowed, reason = consolidation_allowed()
    assert allowed is True
    assert reason == "eval_gate_approved"
