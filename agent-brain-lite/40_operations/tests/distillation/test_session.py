"""Distillation session buffer and skeleton flush tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "40_operations" / "python"))

from distillation.session import (  # noqa: E402
    append_action,
    build_skeleton_record,
    flush_skeleton,
    load_session,
    reset_session,
)


@pytest.mark.unit
def test_append_action_accumulates(tmp_path):
    reset_session(workspace=tmp_path)
    append_action("Grep", success=True, workspace=tmp_path)
    append_action("Shell", success=False, workspace=tmp_path)
    state = load_session(tmp_path)
    assert len(state["actions"]) == 2
    assert state["tool_failures"] == 1


@pytest.mark.unit
def test_build_skeleton_none_when_empty(tmp_path):
    reset_session(workspace=tmp_path)
    assert build_skeleton_record(load_session(tmp_path)) is None


@pytest.mark.unit
def test_flush_skeleton_writes_pending_record(tmp_path, monkeypatch):
    monkeypatch.delenv("DISTILLATION_CAPTURE_DISABLED", raising=False)
    reset_session(workspace=tmp_path)
    append_action("Grep", success=True, workspace=tmp_path)
    log_path = flush_skeleton(workspace=tmp_path)
    assert log_path is not None
    row = json.loads(log_path.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert row["skeleton"] is True
    assert row["enrichment_status"] == "pending"
    assert row["promotable"] is False
    assert row["reasoning"] == ""
    assert row["actions"][0]["tool"] == "Grep"
    assert load_session(tmp_path)["actions"] == []


@pytest.mark.unit
def test_flush_empty_session_returns_none(tmp_path):
    reset_session(workspace=tmp_path)
    assert flush_skeleton(workspace=tmp_path) is None
