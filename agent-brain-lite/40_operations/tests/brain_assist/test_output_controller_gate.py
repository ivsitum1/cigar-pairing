"""Tests for zero-tolerance output_controller_gate."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "40_operations" / "python"))

from brain_assist.output_controller_gate import run_output_gate  # noqa: E402


def test_empty_text_fails() -> None:
    report = run_output_gate(text="", domain="writing")
    assert not report.pass_all
    assert report.checks[0].id == "L1-NONEMPTY"


def test_placeholder_fails() -> None:
    report = run_output_gate(text="Results were significant. [TODO] add CI.", domain="writing")
    assert not report.pass_all
    assert any(c.id == "L1-PLACEHOLDER" and not c.passed for c in report.checks)


def test_clean_writing_passes_rubric_layer() -> None:
    text = (
        "We conducted a retrospective cohort study with adequate sample size. "
        "Methods followed STROBE. Results are reported with confidence intervals."
    )
    report = run_output_gate(text=text, domain="writing")
    assert report.checks[0].passed
    assert not any(c.id == "L1-PLACEHOLDER" and not c.passed for c in report.checks)


def test_statistics_p_without_ci_fails() -> None:
    text = "The difference was significant (p = 0.03)."
    report = run_output_gate(text=text, domain="statistics")
    assert any(c.id == "L1-STATS-P-CI" and not c.passed for c in report.checks)


def test_statistics_p_with_ci_passes_hygiene() -> None:
    text = "Mean difference 2.1 (95% CI 0.4 to 3.8); p = 0.03; Cohen d = 0.5."
    report = run_output_gate(text=text, domain="statistics")
    stats = [c for c in report.checks if c.id == "L1-STATS-P-CI"]
    assert stats and stats[0].passed
