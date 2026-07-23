"""Smoke tests for .cursor/scripts/handoff_log.py."""
import json
from pathlib import Path

import handoff_log


def test_append_creates_entry(tmp_path, monkeypatch):
    log_path = tmp_path / "handoff_log.jsonl"
    monkeypatch.setattr(handoff_log, "LOG_PATH", log_path)

    handoff_log.append(
        from_agent="STATISTICS",
        to_agent="WRITING",
        done="Completed analysis",
        next_step="Draft results section",
        context="primary outcome"
    )

    assert log_path.exists()
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["from"] == "STATISTICS"
    assert entry["to"] == "WRITING"
    assert entry["done"] == "Completed analysis"
    assert "ts" in entry


def test_append_multiple(tmp_path, monkeypatch):
    log_path = tmp_path / "handoff_log.jsonl"
    monkeypatch.setattr(handoff_log, "LOG_PATH", log_path)

    handoff_log.append("STATS", "WRITING", "done1", "next1", "ctx1")
    handoff_log.append("WRITING", "CODE_QA", "done2", "next2", "ctx2")

    lines = [l for l in log_path.read_text(encoding="utf-8").strip().split("\n") if l.strip()]
    assert len(lines) == 2

    entry1 = json.loads(lines[0])
    entry2 = json.loads(lines[1])
    assert entry1["from"] == "STATS"
    assert entry2["from"] == "WRITING"


def test_append_truncates_long_fields(tmp_path, monkeypatch):
    log_path = tmp_path / "handoff_log.jsonl"
    monkeypatch.setattr(handoff_log, "LOG_PATH", log_path)

    handoff_log.append("A", "B", done="x" * 1000, context="y" * 500)

    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert len(entry["done"]) == 500
    assert len(entry["context"]) == 200
