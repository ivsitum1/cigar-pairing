#!/usr/bin/env python3
"""Trajectory-level evaluator for live agent run traces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


def _event_type(event: dict[str, Any]) -> str:
    return str(event.get("event_type", "")).strip()


def evaluate_trajectory(events: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[str] = []
    coverage: dict[str, int] = {}
    missing_signals: list[str] = []

    tool_correct_scores: list[float] = []
    arg_valid_scores: list[float] = []
    plan_quality_scores: list[float] = []
    adherence_scores: list[float] = []
    state_scores: list[float] = []

    planned_steps: set[str] = set()
    executed_steps_total = 0
    executed_steps_adherent = 0
    total_step_events = 0
    unnecessary_events = 0

    for event in events:
        etype = _event_type(event)
        p = _payload(event)

        if etype == "plan_step":
            step_id = p.get("step_id")
            if step_id:
                planned_steps.add(str(step_id))
            if isinstance(p.get("quality_score"), (int, float)):
                plan_quality_scores.append(float(p["quality_score"]))
            else:
                structural = [
                    bool(p.get("has_goal")),
                    bool(p.get("has_rationale")),
                    bool(p.get("has_acceptance_criteria")),
                ]
                plan_quality_scores.append(sum(1.0 for v in structural if v) / 3.0)

        if etype == "tool_selected":
            total_step_events += 1
            selected = p.get("selected_tool")
            expected = p.get("expected_tool")
            if expected is not None and selected is not None:
                tool_correct_scores.append(1.0 if str(selected) == str(expected) else 0.0)
            elif isinstance(p.get("tool_correct"), bool):
                tool_correct_scores.append(1.0 if p.get("tool_correct") else 0.0)

            executed_steps_total += 1
            if not bool(p.get("unplanned", False)):
                plan_step_id = p.get("plan_step_id")
                if plan_step_id and str(plan_step_id) in planned_steps:
                    executed_steps_adherent += 1
                elif plan_step_id is None and planned_steps:
                    pass
                elif not planned_steps:
                    executed_steps_adherent += 1
            if bool(p.get("unnecessary", False)):
                unnecessary_events += 1

        if etype == "tool_args":
            if isinstance(p.get("schema_valid"), bool):
                arg_valid_scores.append(1.0 if p.get("schema_valid") else 0.0)
            elif isinstance(p.get("args_valid"), bool):
                arg_valid_scores.append(1.0 if p.get("args_valid") else 0.0)

        if etype == "state_snapshot":
            total_step_events += 1
            if isinstance(p.get("context_ok"), bool):
                state_scores.append(1.0 if p.get("context_ok") else 0.0)
            else:
                required = p.get("required_keys")
                state = p.get("state")
                if isinstance(required, list) and isinstance(state, dict) and required:
                    ok = sum(1 for k in required if k in state)
                    state_scores.append(ok / len(required))
            if bool(p.get("unnecessary", False)):
                unnecessary_events += 1

    if executed_steps_total > 0:
        adherence_scores.append(executed_steps_adherent / executed_steps_total)

    if not tool_correct_scores:
        missing_signals.append("tool_correctness")
    if not arg_valid_scores:
        missing_signals.append("argument_correctness")
    if not plan_quality_scores:
        missing_signals.append("plan_quality")
    if not adherence_scores:
        missing_signals.append("plan_adherence")
    if not state_scores:
        missing_signals.append("state_tracking")

    metrics: dict[str, float | None] = {
        "tool_correctness": _mean(tool_correct_scores),
        "argument_correctness": _mean(arg_valid_scores),
        "plan_quality": _mean(plan_quality_scores),
        "plan_adherence": _mean(adherence_scores),
        "state_tracking": _mean(state_scores),
        "step_efficiency": None,
    }

    ideal_step_count = None
    for event in events:
        if _event_type(event) == "run_metadata":
            p = _payload(event)
            if isinstance(p.get("ideal_step_count"), int):
                ideal_step_count = int(p["ideal_step_count"])
                break

    if ideal_step_count is not None:
        actual = max(total_step_events, 1)
        metrics["step_efficiency"] = max(0.0, 1.0 - ((actual - ideal_step_count) / max(ideal_step_count, 1)))
    elif total_step_events > 0:
        metrics["step_efficiency"] = max(0.0, 1.0 - (unnecessary_events / total_step_events))
    else:
        missing_signals.append("step_efficiency")

    numeric = [v for v in metrics.values() if isinstance(v, (int, float))]
    trajectory_score = _mean([float(x) for x in numeric])

    coverage["events_total"] = len(events)
    coverage["tool_selected"] = sum(1 for e in events if _event_type(e) == "tool_selected")
    coverage["tool_args"] = sum(1 for e in events if _event_type(e) == "tool_args")
    coverage["plan_step"] = sum(1 for e in events if _event_type(e) == "plan_step")
    coverage["state_snapshot"] = sum(1 for e in events if _event_type(e) == "state_snapshot")

    if len(events) == 0:
        issues.append("empty_trace")

    run_id = ""
    if events:
        run_id = str(events[0].get("run_id", ""))

    return {
        "run_id": run_id,
        "metrics": metrics,
        "coverage": coverage,
        "missing_signals": sorted(set(missing_signals)),
        "trajectory_score": trajectory_score,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate trajectory-level metrics from a run trace JSONL.")
    parser.add_argument("--trace", required=True, help="Path to run trace JSONL")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    args = parser.parse_args()

    trace_path = Path(args.trace)
    if not trace_path.exists():
        raise FileNotFoundError(f"Trace not found: {trace_path}")

    result = evaluate_trajectory(_load_events(trace_path))
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

