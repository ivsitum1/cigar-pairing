"""Smoke tests for .cursor/scripts/error_ops.py."""
import json
from pathlib import Path

import error_ops


def test_log_error_creates_entry(tmp_path, monkeypatch):
    log_path = tmp_path / "error_log.jsonl"
    monkeypatch.setattr(error_ops, "ERROR_LOG", log_path)

    eid = error_ops.log_error(
        cat="statistics", sev="medium", ctx="test",
        err="Wrong prior", fix="Use cauchy", agent="STATS", project="TEST", tags=["prior"]
    )
    assert eid == "E001"
    assert log_path.exists()
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["cat"] == "statistics"
    assert entry["promoted"] is False


def test_log_error_increments_id(tmp_path, monkeypatch):
    log_path = tmp_path / "error_log.jsonl"
    monkeypatch.setattr(error_ops, "ERROR_LOG", log_path)

    error_ops.log_error("statistics", "low", "ctx", "e1", "f1", "a", "p", [])
    eid2 = error_ops.log_error("writing", "low", "ctx", "e2", "f2", "a", "p", [])
    assert eid2 == "E002"


def test_audit_empty_log(tmp_path, monkeypatch):
    monkeypatch.setattr(error_ops, "ERROR_LOG", tmp_path / "nonexistent.jsonl")
    result = error_ops.audit()
    assert result["total"] == 0


def test_audit_with_entries(tmp_path, monkeypatch):
    log_path = tmp_path / "error_log.jsonl"
    monkeypatch.setattr(error_ops, "ERROR_LOG", log_path)

    error_ops.log_error("statistics", "high", "ctx", "err", "fix", "a", "p", ["t1"])
    error_ops.log_error("writing", "low", "ctx", "err", "fix", "a", "p", ["t2"])
    result = error_ops.audit()
    assert result["total"] == 2
    assert result["by_category"]["statistics"] == 1
    assert len(result["unpromoted_high"]) == 1


def test_set_promoted(tmp_path, monkeypatch):
    log_path = tmp_path / "error_log.jsonl"
    monkeypatch.setattr(error_ops, "ERROR_LOG", log_path)

    error_ops.log_error("statistics", "high", "ctx", "err", "fix", "a", "p", [])
    error_ops.set_promoted_in_log("E001", True)

    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["promoted"] is True


def test_check_patterns_below_threshold(tmp_path, monkeypatch):
    log_path = tmp_path / "error_log.jsonl"
    monkeypatch.setattr(error_ops, "ERROR_LOG", log_path)

    error_ops.log_error("statistics", "low", "ctx", "err", "fix", "a", "p", ["prior"])
    matches = error_ops.check_patterns("statistics", ["prior"])
    assert matches == []


def test_check_patterns_above_threshold(tmp_path, monkeypatch):
    log_path = tmp_path / "error_log.jsonl"
    monkeypatch.setattr(error_ops, "ERROR_LOG", log_path)

    error_ops.log_error("statistics", "low", "ctx", "err1", "fix1", "a", "p", ["prior"])
    error_ops.log_error("statistics", "low", "ctx", "err2", "fix2", "a", "p", ["prior"])
    matches = error_ops.check_patterns("statistics", ["prior"])
    assert len(matches) == 2
