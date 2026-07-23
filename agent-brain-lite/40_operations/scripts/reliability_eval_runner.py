#!/usr/bin/env python3
"""Reliability-layer evaluator (human alignment, consistency, variance, golden-set)."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def _stdev(values: list[float]) -> float | None:
    if len(values) < 2:
        return 0.0 if values else None
    m = sum(values) / len(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / len(values))


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


def evaluate_reliability(events: list[dict[str, Any]], judge_runs: int = 1) -> dict[str, Any]:
    final_payload: dict[str, Any] = {}
    for event in reversed(events):
        if event.get("event_type") == "final_answer" and isinstance(event.get("payload"), dict):
            final_payload = event["payload"]
            break

    human_alignment: list[float] = []
    judge_scores: list[float] = []
    golden_scores: list[float] = []
    judge_labels: list[str] = []

    if isinstance(final_payload.get("human_alignment_score"), (int, float)):
        human_alignment.append(float(final_payload["human_alignment_score"]))

    if isinstance(final_payload.get("golden_set_score"), (int, float)):
        golden_scores.append(float(final_payload["golden_set_score"]))
    elif isinstance(final_payload.get("golden_set_match"), bool):
        golden_scores.append(1.0 if final_payload["golden_set_match"] else 0.0)

    judges = final_payload.get("judge_runs")
    if isinstance(judges, list):
        for row in judges:
            if not isinstance(row, dict):
                continue
            if isinstance(row.get("score"), (int, float)):
                judge_scores.append(float(row["score"]))
            if row.get("label") is not None:
                judge_labels.append(str(row["label"]))

    if not judge_scores and isinstance(final_payload.get("judge_score"), (int, float)):
        judge_scores.append(float(final_payload["judge_score"]))

    mean_judge = _mean(judge_scores)
    var_judge = _stdev(judge_scores)
    consistency = None
    if judge_labels:
        mode = max(set(judge_labels), key=judge_labels.count)
        consistency = judge_labels.count(mode) / len(judge_labels)
    elif judge_scores:
        # score-band agreement fallback
        if len(judge_scores) == 1:
            consistency = 1.0
        else:
            span = max(judge_scores) - min(judge_scores)
            consistency = max(0.0, 1.0 - span)

    expected_judges = max(1, judge_runs)
    judge_coverage = min(1.0, len(judge_scores) / expected_judges)

    metrics = {
        "human_alignment_scoring": _mean(human_alignment),
        "judge_consistency_across_runs": consistency,
        "judge_output_variance": var_judge,
        "golden_set_evaluation": _mean(golden_scores),
        "judge_coverage": judge_coverage,
        "judge_mean_score": mean_judge,
    }

    issues: list[str] = []
    missing: list[str] = []
    for k in ("human_alignment_scoring", "judge_consistency_across_runs", "judge_output_variance", "golden_set_evaluation"):
        if metrics[k] is None:
            missing.append(k)
    if len(judge_scores) < expected_judges:
        issues.append("insufficient_judge_runs")
    if not final_payload:
        issues.append("missing_final_answer_event")

    run_id = str(events[0].get("run_id", "")) if events else ""
    return {
        "run_id": run_id,
        "metrics": metrics,
        "missing_signals": missing,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate reliability metrics from a run trace JSONL.")
    parser.add_argument("--trace", required=True, help="Path to run trace JSONL")
    parser.add_argument("--judge-runs", type=int, default=1, help="Expected number of judge runs")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    trace = Path(args.trace)
    if not trace.exists():
        raise FileNotFoundError(f"Trace not found: {trace}")
    result = evaluate_reliability(_load_events(trace), judge_runs=args.judge_runs)
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

