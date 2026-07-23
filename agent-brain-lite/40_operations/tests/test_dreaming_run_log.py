"""Tests for dreaming run log."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_OPS = Path(__file__).resolve().parents[1] / "python"
if str(_OPS) not in sys.path:
    sys.path.insert(0, str(_OPS))

from common.dreaming_run_log import append_dream_event, iso_week_file_label, run_logs_dir  # noqa: E402


def test_append_dream_event(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_DREAMING_RUN_LOG", "1")
    path = append_dream_event(tmp_path, tool="Shell", outcome="pytest ok")
    assert path is not None
    assert path.is_file()
    line = json.loads(path.read_text(encoding="utf-8").strip().splitlines()[0])
    assert line["tool"] == "Shell"
    assert line["outcome"] == "pytest ok"


def test_run_logs_dir_week_label() -> None:
    assert iso_week_file_label().startswith("20")
