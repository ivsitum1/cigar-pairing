"""Tests for 40_operations/python/quality_validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PY = Path(__file__).resolve().parents[2] / "python"
sys.path.insert(0, str(_PY))

from quality_validation import (  # noqa: E402
    PASS_THRESHOLD,
    apply_improvements,
    evaluate_rubric,
    evaluate_rubric_domain,
    generate_improvements,
    mandatory_self_assess,
    validate_with_swiss_cheese,
)

PERFECT_STATS = (
    "set.seed(42); library(here); here::here(); dplyr::filter; "
    "shapiro.test(x); leveneTest; assumption normality homoscedasticity independence residual; "
    "cohen d = 0.5, 95% CI [0.1,0.9]; p=0.01; p=0.02; bonferroni correction; sessionInfo()"
)
PERFECT_CODE = "set.seed(42); dplyr::filter(df, x > 0); library(here); sessionInfo()"
PERFECT_METHOD = (
    "Primary outcome pre-specified in protocol. Sample size 80% power n=200. "
    "Bias assessment and confounding addressed."
)
NEAR_PERFECT_WRITING = "CONSORT flow enrolled 100 participants analyzed 95. " * 10


def test_pass_threshold_is_ten():
    assert PASS_THRESHOLD == 10.0


def test_evaluate_rubric_domain_statistics():
    txt = "shapiro.test(x); cohen's d = 0.5, 95% CI [0.1, 0.9]; set.seed(42)"
    result = evaluate_rubric_domain(txt, "statistics")
    assert set(result) == {"overall", "details", "pass", "domain"}
    assert 0 <= result["overall"] <= 10
    assert result["domain"] == "statistics"
    assert isinstance(result["pass"], bool)
    assert result["pass"] == (result["overall"] >= PASS_THRESHOLD)


def test_evaluate_rubric_legacy():
    result = evaluate_rubric({"a": 1}, rubric=None, domain=None)
    assert "scores" in result and "total" in result
    assert result["total"] == 10


def test_evaluate_rubric_legacy_empty_fails():
    result = evaluate_rubric("", rubric=None, domain=None)
    assert result["total"] == 0


@pytest.mark.parametrize(
    ("domain", "text"),
    [
        ("statistics", PERFECT_STATS),
        ("code", PERFECT_CODE),
        ("methodology", PERFECT_METHOD),
    ],
)
def test_domain_pass_only_at_perfect_ten(domain: str, text: str):
    result = evaluate_rubric_domain(text, domain)
    assert result["overall"] == PASS_THRESHOLD
    assert result["pass"] is True


def test_domain_near_perfect_nine_point_seven_does_not_pass():
    result = evaluate_rubric_domain(NEAR_PERFECT_WRITING, "writing")
    assert result["overall"] == pytest.approx(9.7)
    assert result["overall"] < PASS_THRESHOLD
    assert result["pass"] is False


def test_domain_empty_output_never_passes():
    for domain in ("statistics", "writing", "code", "methodology"):
        result = evaluate_rubric_domain("", domain)
        assert result["pass"] is False
        assert result["overall"] < PASS_THRESHOLD


def test_mandatory_self_assess_domain_perfect_passes_first_iteration():
    result = mandatory_self_assess(PERFECT_CODE, domain="code", max_iterations=3)
    assert result["iterations"] == 1
    assert result["final_score"] == PASS_THRESHOLD


def test_mandatory_self_assess_domain_below_threshold_flags_human_review():
    txt = "shapiro.test(x); p=0.01; p=0.02"
    result = mandatory_self_assess(txt, domain="statistics", max_iterations=2)
    assert result["iterations"] == 2
    assert result["final_score"] < PASS_THRESHOLD
    assert result["output"].get("_needs_human_review") is True


def test_improvement_hints_do_not_inflate_domain_score():
    weak = "p=0.01; p=0.02"
    wrapped = apply_improvements(
        weak,
        [
            "Improve assumptions_checked: Add Shapiro-Wilk/residual plots.",
            "Improve multiple_testing: Multiple comparisons detected without correction.",
        ],
    )
    before = evaluate_rubric_domain(weak, "statistics")["overall"]
    after = evaluate_rubric_domain(wrapped, "statistics")["overall"]
    assert after == before


def test_mandatory_self_assess_legacy():
    result = mandatory_self_assess({"a": 1}, max_iterations=2)
    assert result["iterations"] == 1
    assert result["final_score"] == PASS_THRESHOLD


def test_generate_improvements_for_failing_domain():
    ev = evaluate_rubric_domain("p=0.01; p=0.02", "statistics")
    hints = generate_improvements(ev, "p=0.01; p=0.02")
    assert hints
    assert any("correction" in h.lower() or "assumption" in h.lower() for h in hints)


def test_apply_improvements_wraps_string_output():
    improved = apply_improvements("raw", ["fix reproducibility"])
    assert improved["_raw"] == "raw"
    assert improved["_improvement_hints"] == ["fix reproducibility"]


def test_swiss_cheese_success():
    task = {"task_type": "t", "inputs": {"x": 1}}

    def executor(t):
        return "done"

    res = validate_with_swiss_cheese(task, executor)
    assert res["success"] is True
    assert res["assessment"]["score"] >= PASS_THRESHOLD


def test_swiss_cheese_pre_fails():
    task = {"task_type": None, "inputs": {}}
    res = validate_with_swiss_cheese(task, lambda t: t)
    assert res["success"] is False
    assert res["layer"] == "pre_execution"
