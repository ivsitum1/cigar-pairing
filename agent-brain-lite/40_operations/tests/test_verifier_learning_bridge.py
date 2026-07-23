"""Tests for verifier learning bridge."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "40_operations" / "scripts" / "verifier_learning_bridge.py"
EVAL_PATH = REPO / "30_system" / "SKILLS" / "evals" / "skill-verifier-gate.json"
STATE_PATH = REPO / ".agent" / "memory" / "verifier_bridge_state.json"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )


def test_from_correction_dry_run():
    proc = _run(
        [
            "from-correction",
            "--prompt",
            "meta-analysis forest plot pooled effect",
            "--skill-id",
            "meta-analysis",
            "--expected-action",
            "ACCEPT",
            "--dry-run",
        ]
    )
    assert proc.returncode == 0
    assert "meta-analysis" in proc.stdout


def test_from_correction_appends_case(tmp_path, monkeypatch):
    backup = EVAL_PATH.read_text(encoding="utf-8")
    state_backup = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.is_file() else None
    try:
        if STATE_PATH.is_file():
            STATE_PATH.unlink()
        proc = _run(
            [
                "from-correction",
                "--prompt",
                "meta-analysis sensitivity analysis",
                "--skill-id",
                "meta-analysis",
                "--expected-action",
                "ACCEPT",
                "--case-id",
                "case_test_bridge_tmp",
                "--no-wiki-log",
                "--no-evolve-verifier",
            ]
        )
        assert proc.returncode == 0, proc.stderr
        data = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
        ids = [c.get("id") for c in data.get("cases") or []]
        assert "case_test_bridge_tmp" in ids
    finally:
        EVAL_PATH.write_text(backup, encoding="utf-8")
        if state_backup:
            STATE_PATH.write_text(state_backup, encoding="utf-8")
        elif STATE_PATH.is_file():
            STATE_PATH.unlink()
