"""
Mandatory self-assessment loop (former R self_assessment.R).
Use for agent output quality gates; statistics belong in R, not here.
"""

from __future__ import annotations

import warnings
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from quality_validation.rubrics import PASS_THRESHOLD, evaluate_rubric_domain

LegacyRubric = Dict[str, Dict[str, Union[int, str]]]


def default_rubric() -> LegacyRubric:
    return {
        "completeness": {
            "weight": 2,
            "description": "All required elements present?",
        },
        "accuracy": {
            "weight": 2,
            "description": "Information verified and correct?",
        },
        "clarity": {
            "weight": 2,
            "description": "Easily understandable?",
        },
        "reproducibility": {
            "weight": 2,
            "description": "Can someone replicate this?",
        },
        "clinical_relevance": {
            "weight": 2,
            "description": "Practical utility?",
        },
    }


def _has_content(output: Any) -> bool:
    if output is None:
        return False
    if isinstance(output, str):
        return len(output) > 0
    if isinstance(output, (list, tuple, dict)):
        return len(output) > 0
    return True


def evaluate_rubric(
    output: Any,
    rubric: Optional[LegacyRubric] = None,
    domain: Optional[str] = None,
) -> dict:
    """
    If domain is set, use domain rubric (statistics, writing, code, methodology).
    Otherwise use legacy rubric (stub: full score if non-empty output).
    """
    if domain is not None:
        return evaluate_rubric_domain(output, domain)
    rubric = rubric or default_rubric()
    scores: Dict[str, dict] = {}
    total = 0
    for nm, spec in rubric.items():
        w = int(spec["weight"])
        s = w if _has_content(output) else 0
        scores[nm] = {
            "score": s,
            "max": w,
            "description": spec["description"],
        }
        total += s
    return {"scores": scores, "total": total}


def generate_improvements(ev: dict, output: Any) -> List[str]:
    hints: List[str] = []
    if "scores" in ev and ev["scores"]:
        for nm, row in ev["scores"].items():
            if row["score"] < row["max"]:
                hints.append(f"Improve {nm}: {row['description']}")
    elif "details" in ev:
        for d in ev["details"]:
            if d["score"] < 7:
                hints.append(str(d["feedback"]))
    return hints


def apply_improvements(output: Any, improvements: List[str]) -> Any:
    if not improvements:
        return output
    if isinstance(output, dict):
        out = dict(output)
        out["_improvement_hints"] = improvements
        return out
    return {"_raw": output, "_improvement_hints": improvements}


def mandatory_self_assess(
    output: Any,
    rubric: Optional[LegacyRubric] = None,
    domain: Optional[str] = None,
    max_iterations: int = 5,
) -> dict:
    """
    Iterate until pass (legacy total or domain overall >= PASS_THRESHOLD) or max_iterations.
    Returns output, final_score, iterations, history.
    """
    iteration = 1
    current = output
    history: List[dict] = []
    ev: dict = {}
    total = 0.0
    pass_flag = False

    while True:
        ev = evaluate_rubric(current, rubric=rubric, domain=domain)
        is_domain = "overall" in ev
        total = float(ev["overall"]) if is_domain else float(ev["total"])
        pass_flag = bool(ev["pass"]) if is_domain else total >= PASS_THRESHOLD

        history.append(
            {
                "iteration": iteration,
                "scores": ev.get("scores") or ev.get("details"),
                "total": total,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        if pass_flag:
            print(
                f"Self-assessment passed: {total:.1f}/10 (iteration {iteration})"
            )
            break

        if iteration >= max_iterations:
            warnings.warn(
                f"Max iterations ({max_iterations}) reached. Best score: {total:.1f}/10. Flag for human review.",
                stacklevel=2,
            )
            if isinstance(current, dict):
                current = dict(current)
                current["_needs_human_review"] = True
            else:
                current = {"_raw": current, "_needs_human_review": True}
            break

        improvements = generate_improvements(ev, current)
        print(
            f"Score: {total:.1f}/10. Applying improvements (iteration {iteration}/{max_iterations})..."
        )
        current = apply_improvements(current, improvements)
        iteration += 1

    return {
        "output": current,
        "final_score": total,
        "iterations": iteration,
        "history": history,
    }


assess = mandatory_self_assess
