#!/usr/bin/env python3
"""
SkillCoach-lite: process rubric scoring on trajectory JSONL.

Dimensions (arXiv:2607.01874):
  - skill_selection
  - skill_following
  - skill_composition
  - skill_grounded_reflection

Usage:
  python 40_operations/scripts/skill_process_rubric.py --trace 90_archive/artifacts/<run>/trajectory.jsonl --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[2]


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not path.is_file():
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def score_trace(events: list[dict[str, Any]]) -> dict[str, Any]:
    tool_events = [e for e in events if e.get("event_type") == "tool_selected"]
    atdp = [e for e in events if e.get("event_type") == "atdp_step"]
    plan_steps = [e for e in events if e.get("event_type") == "plan_step"]
    final = [e for e in events if e.get("event_type") == "final_answer"]
    gaps = [e for e in events if e.get("event_type") == "skill_gap"]

    tools = [
        (e.get("payload") or {}).get("selected_tool", "")
        for e in tool_events
    ]
    tools = [t for t in tools if t]

    # skill_selection: plan exists before first tool; no skill_gap on first tool
    has_plan = bool(plan_steps)
    early_gap = any(
        (e.get("payload") or {}).get("gap_type") == "tool_failure" for e in gaps[:2]
    )
    selection = 1.0 if has_plan and not early_gap else (0.5 if has_plan else 0.2)

    # skill_following: majority tool_correct
    correct = sum(1 for e in tool_events if (e.get("payload") or {}).get("tool_correct"))
    following = (correct / len(tool_events)) if tool_events else 0.0

    # skill_composition: multi-tool workflow without isolated failures
    composition = 0.0
    if len(tools) >= 2:
        composition = 0.7 if following >= 0.5 else 0.3
    elif len(tools) == 1:
        composition = 0.5

    # reflection: atdp after failure or final_answer present
    had_failure = any(not (e.get("payload") or {}).get("tool_correct", True) for e in tool_events)
    reflection = 0.0
    if atdp:
        reflection += 0.5
    if had_failure and atdp:
        reflection += 0.3
    if final:
        reflection += 0.2
    reflection = min(1.0, reflection)

    dims = {
        "skill_selection": round(selection, 3),
        "skill_following": round(following, 3),
        "skill_composition": round(composition, 3),
        "skill_grounded_reflection": round(reflection, 3),
    }
    process_score = round(sum(dims.values()) / len(dims) * 100, 1)

    outcome_success = all((e.get("payload") or {}).get("tool_correct", True) for e in tool_events) if tool_events else False

    return {
        "dimensions": dims,
        "process_score": process_score,
        "outcome_success": outcome_success,
        "process_outcome_gap": outcome_success and process_score < 60,
        "tool_count": len(tools),
        "atdp_steps": len(atdp),
        "note": "Heuristic SkillCoach-lite; not a substitute for evolved LLM rubrics (2607.01874).",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SkillCoach-lite process rubric")
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = args.trace if args.trace.is_file() else WORKSPACE / args.trace
    events = load_events(path)
    if not events:
        print(f"No events in {path}", file=sys.stderr)
        return 2

    report = {"trace": str(path.relative_to(WORKSPACE)).replace("\\", "/"), **score_trace(events)}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"process_score={report['process_score']} outcome={report['outcome_success']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
