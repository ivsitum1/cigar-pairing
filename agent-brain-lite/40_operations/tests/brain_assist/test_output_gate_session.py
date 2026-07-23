"""Tests for output_gate_session (hook deliverable tracking)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from brain_assist.output_gate_session import (  # noqa: E402
    extract_path_from_tool_payload,
    flag_deliverable,
    flush_gates,
    infer_domain,
    is_deliverable_path,
    load_session,
    reset_session,
)


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    (tmp_path / "03_output").mkdir()
    return tmp_path


def test_is_deliverable_path_output_folder(ws: Path) -> None:
    assert is_deliverable_path("03_output/manuscript_draft.md", ws)
    assert not is_deliverable_path(".agent/MEMORY.md", ws)
    assert not is_deliverable_path("40_operations/tests/foo.md", ws)


def test_extract_path_from_nested_arguments() -> None:
    payload = {
        "toolName": "Write",
        "arguments": {"path": "03_output/results.md", "contents": "x"},
    }
    assert extract_path_from_tool_payload(payload) == "03_output/results.md"


def test_flag_and_flush_writes_report(ws: Path) -> None:
    reset_session(workspace=ws)
    out = ws / "03_output" / "results.md"
    out.write_text(
        "Mean difference 2.1 (95% CI 0.4 to 3.8); p = 0.03; Cohen d = 0.5. "
        "We used Welch t-test after checking assumptions with Shapiro and Levene. "
        "set.seed(42); library(here); sessionInfo recorded.",
        encoding="utf-8",
    )
    flag_deliverable("03_output/results.md", domain="statistics", workspace=ws)
    state = load_session(ws)
    assert "03_output/results.md" in state["flagged"]

    summary = flush_gates(workspace=ws)
    assert summary["total"] == 1
    assert (ws / ".agent" / "output_gate" / "last_report.json").is_file()
    assert load_session(ws)["flagged"] == {}


def test_flush_fails_placeholder(ws: Path) -> None:
    reset_session(workspace=ws)
    bad = ws / "03_output" / "bad.md"
    bad.write_text("Significant finding. [TODO] add numbers.", encoding="utf-8")
    flag_deliverable("03_output/bad.md", domain="writing", workspace=ws)
    summary = flush_gates(workspace=ws)
    assert summary["failed"] == 1


def test_infer_domain_statistics() -> None:
    assert infer_domain("02_analysis/model.R") == "statistics"
