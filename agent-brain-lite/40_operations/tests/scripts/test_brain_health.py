"""Smoke tests for 40_operations/scripts/brain_health.py."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import brain_health


def test_check_structure_ok(tmp_project, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_project)
    monkeypatch.setattr(brain_health, "AGENT_RULES", tmp_project)
    (tmp_project / "40_operations/scripts").mkdir(parents=True, exist_ok=True)
    report = {"ok": True, "structure": {}}
    brain_health.check_structure(report)
    assert report["structure"][".agent"] == "ok"


def test_check_structure_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(brain_health, "AGENT_RULES", tmp_path)
    report = {"ok": True, "structure": {}}
    brain_health.check_structure(report)
    assert report["ok"] is False


def test_check_context_ok(tmp_project, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_project)
    monkeypatch.setattr(brain_health, "AGENT_RULES", tmp_project)
    report = {
        "ok": True,
        "30_system/context": {},
        "04_documentation/context (project, warn-only)": {},
    }
    brain_health.check_context(report)
    for name in ["user.md", "soul.md", "memory.md"]:
        assert report["30_system/context"][name] == "ok"
    for name in ["main.md", "commit.md", "log.md"]:
        assert report["04_documentation/context (project, warn-only)"][name] == "ok"


def test_check_memory_ok(tmp_project, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_project)
    report = {"ok": True}
    brain_health.check_memory(report)
    assert "ok" in report["memory"]


def test_check_handoff_ok(tmp_project, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_project)
    report = {"ok": True}
    brain_health.check_handoff(report)
    assert "ok" in report["handoff"]


def test_check_handoff_invalid(tmp_project, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_project)
    (tmp_project / ".agent" / "handoff_log.jsonl").write_text("not json\n", encoding="utf-8")
    report = {"ok": True}
    brain_health.check_handoff(report)
    assert "warn" in report["handoff"]


def test_check_errors_empty(tmp_project, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_project)
    report = {"ok": True}
    brain_health.check_errors(report)
    assert "ok" in report["errors"]


def test_check_errors_promoted_high_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_path)
    err_dir = tmp_path / ".cursor" / "errors"
    err_dir.mkdir(parents=True)
    entry = {
        "id": "E1",
        "sev": "high",
        "promoted": True,
        "err": "test",
        "fix": "test",
    }
    (err_dir / "error_log.jsonl").write_text(
        json.dumps(entry) + "\n", encoding="utf-8"
    )
    report = {"ok": True}
    brain_health.check_errors(report)
    assert report["ok"] is True
    assert "promoted learning" in report["errors"]


def test_check_errors_unpromoted_high_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_path)
    err_dir = tmp_path / ".cursor" / "errors"
    err_dir.mkdir(parents=True)
    entry = {"id": "E1", "sev": "high", "promoted": False, "err": "x", "fix": "y"}
    (err_dir / "error_log.jsonl").write_text(
        json.dumps(entry) + "\n", encoding="utf-8"
    )
    report = {"ok": True}
    brain_health.check_errors(report)
    assert report["ok"] is False
    assert "unpromoted" in report["errors"]


def test_check_errors_strict_fails_on_promoted(tmp_path, monkeypatch):
    monkeypatch.setattr(brain_health, "PROJECT_ROOT", tmp_path)
    err_dir = tmp_path / ".cursor" / "errors"
    err_dir.mkdir(parents=True)
    entry = {"id": "E1", "sev": "high", "promoted": True}
    (err_dir / "error_log.jsonl").write_text(
        json.dumps(entry) + "\n", encoding="utf-8"
    )
    report = {"ok": True}
    brain_health.check_errors(report, strict=True)
    assert report["ok"] is False


def test_check_python(monkeypatch):
    report = {"ok": True}
    brain_health.check_python(report)
    assert "ok" in report["python"]


def test_check_mcp_deps():
    report = {"ok": True}
    brain_health.check_mcp_deps(report)
    assert "mcp_deps" in report
