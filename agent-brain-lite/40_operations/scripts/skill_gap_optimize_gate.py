#!/usr/bin/env python3
"""
Composite gate for enabling the autonomous skill optimization loop (skill gap path).

Computes a 0–100 score from fit, eval readiness, safety, and impact. Hard blockers
override the score. Intended for agents to call after ingest or on skill-gap events.

Usage:
  python 40_operations/scripts/skill_gap_optimize_gate.py \\
    --procedural \\
    --eval-exists --case-count 3 \\
    --severity high \\
    --category writing \\
    --phi-risk none \\
    --json

Environment:
  SKILL_GAP_OPTIMIZE_COMPOSITE_CUTOFF  default 72 (0–100 inclusive)
  SKILL_GAP_OPTIMIZE_AUTO            set to 1 to arm loop from composite alone
  SKILL_GAP_OPTIMIZE_LOOP            set to 1 to arm loop (strict mode with composite)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict


def _env_cutoff() -> int:
    raw = os.environ.get("SKILL_GAP_OPTIMIZE_COMPOSITE_CUTOFF", "72").strip()
    try:
        v = int(raw)
    except ValueError:
        return 72
    return max(0, min(100, v))


SEVERITY_IMPACT = {
    "low": 4,
    "medium": 8,
    "high": 12,
    "critical": 15,
}

PHI_PENALTY = {"none": 0, "possible": 10, "present": 25}

DEFAULT_EDIT_BUDGET_PER_SESSION = 5


def _edit_budget_exceeded(edits_this_session: int) -> bool:
    budget = int(os.environ.get("SKILL_OPT_EDIT_BUDGET", str(DEFAULT_EDIT_BUDGET_PER_SESSION)))
    return edits_this_session >= max(1, budget)


@dataclass
class GateResult:
    composite: int
    cutoff: int
    gate_passes: bool
    armed: bool
    run_optimization_loop: bool
    blockers: list[str]
    components: dict[str, int]
    notes: list[str]
    reminders: list[str]


def compute_gate(
    *,
    procedural: bool,
    eval_exists: bool,
    case_count: int,
    regression_appended: bool,
    severity: str,
    category: str,
    phi_risk: str,
    clinical_authoritative_gold: bool,
    subjective_assertion_count: int,
    edits_this_session: int = 0,
) -> GateResult:
    blockers: list[str] = []
    notes: list[str] = []

    if not eval_exists:
        blockers.append("eval_missing")

    phi = phi_risk.lower().strip()
    if phi not in PHI_PENALTY:
        phi = "possible"
        notes.append("phi_risk_invalid_defaulted_to_possible")
    if phi == "present":
        blockers.append("phi_present_in_fixture")

    cat = category.lower().strip()
    if cat == "clinical" and not clinical_authoritative_gold:
        blockers.append("clinical_correction_without_authoritative_gold")

    if subjective_assertion_count > 0:
        blockers.append("subjective_assertions_present_use_human_review")

    if _edit_budget_exceeded(edits_this_session):
        blockers.append("skillopt_edit_budget_exceeded")
        notes.append("SkillOpt edit budget exhausted for this session")

    sev = severity.lower().strip()
    if sev not in SEVERITY_IMPACT:
        sev = "medium"
        notes.append("severity_invalid_defaulted_to_medium")

    # Fit (0–30): repeatable / procedural workflow
    fit = 30 if procedural else 8
    if not procedural:
        notes.append("low_procedural_fit_penalized")

    # Eval readiness (0–30)
    eval_score = 0
    if eval_exists:
        eval_score += 14
        if case_count >= 3:
            eval_score += 10
        elif case_count >= 2:
            eval_score += 7
        elif case_count >= 1:
            eval_score += 4
        else:
            notes.append("eval_exists_but_zero_cases")
    if regression_appended:
        eval_score += 6
    eval_score = min(30, eval_score)

    # Safety (0–25)
    safety = 25 - PHI_PENALTY.get(phi, 10)
    safety = max(0, safety)

    # Impact (0–15)
    impact = SEVERITY_IMPACT[sev]

    raw_total = fit + eval_score + safety + impact
    composite = max(0, min(100, raw_total))

    cutoff = _env_cutoff()
    gate_passes = len(blockers) == 0 and composite >= cutoff
    auto = os.environ.get("SKILL_GAP_OPTIMIZE_AUTO", "").strip() == "1"
    loop = os.environ.get("SKILL_GAP_OPTIMIZE_LOOP", "").strip() == "1"
    armed = auto or loop
    run_loop = gate_passes and armed

    reminders: list[str] = []
    if gate_passes and not armed:
        reminders.append(
            "HR: Kompozitni prag je zadovoljen (gate_passes=true), ali petlja nece krenuti dok "
            "ne postavis arm: SKILL_GAP_OPTIMIZE_AUTO=1 ili SKILL_GAP_OPTIMIZE_LOOP=1. "
            "PowerShell: $env:SKILL_GAP_OPTIMIZE_AUTO='1'"
        )
        reminders.append(
            "EN: Composite gate passed but optimization loop stays OFF until armed. "
            "Set SKILL_GAP_OPTIMIZE_AUTO=1 or SKILL_GAP_OPTIMIZE_LOOP=1, then re-run this script."
        )

    return GateResult(
        composite=composite,
        cutoff=cutoff,
        gate_passes=gate_passes,
        armed=armed,
        run_optimization_loop=run_loop,
        blockers=blockers,
        components={
            "fit_procedural": fit,
            "eval_readiness": eval_score,
            "safety_phi_adjusted": safety,
            "impact_severity": impact,
        },
        notes=notes,
        reminders=reminders,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Composite gate for skill optimization loop")
    p.add_argument("--procedural", action="store_true", help="Task maps to repeatable / procedural workflow")
    p.add_argument("--eval-exists", action="store_true")
    p.add_argument("--case-count", type=int, default=0)
    p.add_argument("--regression-appended", action="store_true", help="New case just added via skill_gap_ingest")
    p.add_argument("--severity", default="medium", choices=sorted(SEVERITY_IMPACT.keys()))
    p.add_argument(
        "--category",
        default="writing",
        help="stats|code|writing|methodology|clinical",
    )
    p.add_argument(
        "--phi-risk",
        default="none",
        choices=sorted(PHI_PENALTY.keys()),
    )
    p.add_argument(
        "--clinical-authoritative-gold",
        action="store_true",
        help="User confirmed correction is authoritative (clinical domain)",
    )
    p.add_argument(
        "--subjective-assertion-count",
        type=int,
        default=0,
        help="If >0, auto loop is blocked (subjective eval)",
    )
    p.add_argument(
        "--edits-this-session",
        type=int,
        default=0,
        help="SkillOpt textual-gradient edits already applied this session",
    )
    p.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout")
    args = p.parse_args()

    r = compute_gate(
        procedural=args.procedural,
        eval_exists=args.eval_exists,
        case_count=max(0, args.case_count),
        regression_appended=args.regression_appended,
        severity=args.severity,
        category=args.category,
        phi_risk=args.phi_risk,
        clinical_authoritative_gold=args.clinical_authoritative_gold,
        subjective_assertion_count=max(0, args.subjective_assertion_count),
        edits_this_session=max(0, args.edits_this_session),
    )

    payload = asdict(r)
    payload["optimize_loop_on"] = r.run_optimization_loop
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(
        f"composite={r.composite}/{r.cutoff} gate_passes={r.gate_passes} "
        f"armed={r.armed} run_optimization_loop={r.run_optimization_loop}"
    )
    if r.reminders:
        print()
        print("*** REMINDER (gate passed, loop unarmed) ***")
        for line in r.reminders:
            print(line)
        print("*** end reminder ***")
        print()
    if r.blockers:
        print("blockers:", "; ".join(r.blockers))
    print("components:", r.components)
    if r.notes:
        print("notes:", "; ".join(r.notes))
    return 0 if r.run_optimization_loop else 1


if __name__ == "__main__":
    raise SystemExit(main())
