#!/usr/bin/env python3
"""Unified benchmark runner: trajectory + RAG + reliability."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import rag_eval_runner
import reliability_eval_runner
import trajectory_eval_runner


WORKSPACE = Path(__file__).resolve().parent.parent.parent


def _mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_events(trace_path: Path) -> list[dict[str, Any]]:
    return trajectory_eval_runner._load_events(trace_path)


def evaluate_run(trace_path: Path, judge_runs: int) -> dict[str, Any]:
    events = _load_events(trace_path)
    trajectory = trajectory_eval_runner.evaluate_trajectory(events)
    rag = rag_eval_runner.evaluate_rag(events)
    reliability = reliability_eval_runner.evaluate_reliability(events, judge_runs=judge_runs)
    return {
        "trace_path": str(trace_path),
        "run_id": trajectory.get("run_id") or rag.get("run_id") or reliability.get("run_id"),
        "trajectory": trajectory,
        "rag": rag,
        "reliability": reliability,
    }


def aggregate_results(per_run: list[dict[str, Any]]) -> dict[str, Any]:
    trajectory_scores = [r["trajectory"]["trajectory_score"] for r in per_run if isinstance(r["trajectory"].get("trajectory_score"), (int, float))]
    rag_scores = [r["rag"]["rag_score"] for r in per_run if isinstance(r["rag"].get("rag_score"), (int, float))]
    reliability_scores = []
    variance_scores = []
    consistency_scores = []
    golden_scores = []
    for run in per_run:
        rel_metrics = run["reliability"]["metrics"]
        human = rel_metrics.get("human_alignment_scoring")
        consistency = rel_metrics.get("judge_consistency_across_runs")
        variance = rel_metrics.get("judge_output_variance")
        golden = rel_metrics.get("golden_set_evaluation")
        if isinstance(human, (int, float)):
            reliability_scores.append(float(human))
        if isinstance(consistency, (int, float)):
            consistency_scores.append(float(consistency))
        if isinstance(variance, (int, float)):
            variance_scores.append(float(variance))
        if isinstance(golden, (int, float)):
            golden_scores.append(float(golden))

    return {
        "trajectory_score_mean": _mean([float(x) for x in trajectory_scores]),
        "rag_score_mean": _mean([float(x) for x in rag_scores]),
        "human_alignment_mean": _mean(reliability_scores),
        "judge_consistency_mean": _mean(consistency_scores),
        "judge_variance_mean": _mean(variance_scores),
        "golden_set_score_mean": _mean(golden_scores),
        "runs_total": len(per_run),
    }


def apply_gates(summary: dict[str, Any], gates: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []

    def _gate_min(metric_name: str, gate_name: str) -> None:
        gate = gates.get(gate_name)
        value = summary.get(metric_name)
        if gate is None:
            return
        if not isinstance(gate, (int, float)):
            return
        if not isinstance(value, (int, float)):
            return
        if float(value) < float(gate):
            failures.append(f"{metric_name}<{gate_name} ({value}<{gate})")

    def _gate_max(metric_name: str, gate_name: str) -> None:
        gate = gates.get(gate_name)
        value = summary.get(metric_name)
        if gate is None:
            return
        if not isinstance(gate, (int, float)):
            return
        if not isinstance(value, (int, float)):
            return
        if float(value) > float(gate):
            failures.append(f"{metric_name}>{gate_name} ({value}>{gate})")

    _gate_min("trajectory_score_mean", "min_trajectory_score")
    _gate_min("rag_score_mean", "min_rag_score")
    _gate_min("judge_consistency_mean", "min_judge_consistency")
    _gate_min("golden_set_score_mean", "min_golden_set_score")
    _gate_max("judge_variance_mean", "max_judge_variance")

    return len(failures) == 0, failures


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    gates = payload["gates"]
    lines = [
        "# Agent Benchmark Report",
        "",
        f"- benchmark_id: `{payload['benchmark_id']}`",
        f"- generated_at: `{payload['generated_at']}`",
        f"- pass: `{payload['pass']}`",
        "",
        "## Aggregate",
        f"- trajectory_score_mean: `{summary.get('trajectory_score_mean')}`",
        f"- rag_score_mean: `{summary.get('rag_score_mean')}`",
        f"- human_alignment_mean: `{summary.get('human_alignment_mean')}`",
        f"- judge_consistency_mean: `{summary.get('judge_consistency_mean')}`",
        f"- judge_variance_mean: `{summary.get('judge_variance_mean')}`",
        f"- golden_set_score_mean: `{summary.get('golden_set_score_mean')}`",
        "",
        "## Gate Thresholds",
        f"- min_trajectory_score: `{gates.get('min_trajectory_score')}`",
        f"- min_rag_score: `{gates.get('min_rag_score')}`",
        f"- min_judge_consistency: `{gates.get('min_judge_consistency')}`",
        f"- max_judge_variance: `{gates.get('max_judge_variance')}`",
        f"- min_golden_set_score: `{gates.get('min_golden_set_score')}`",
        "",
    ]
    if payload.get("gate_failures"):
        lines.append("## Gate Failures")
        for failure in payload["gate_failures"]:
            lines.append(f"- {failure}")
        lines.append("")
    lines.append("## Per Run")
    for run in payload["runs"]:
        lines.extend(
            [
                f"- `{run.get('run_id')}`",
                f"  - trace: `{run.get('trace_path')}`",
                f"  - trajectory: `{run['trajectory'].get('trajectory_score')}`",
                f"  - rag: `{run['rag'].get('rag_score')}`",
                f"  - reliability_human_alignment: `{run['reliability']['metrics'].get('human_alignment_scoring')}`",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_benchmark(manifest: dict[str, Any]) -> dict[str, Any]:
    benchmark_id = manifest.get("benchmark_id", "benchmark")
    judge_runs = int(manifest.get("judges", {}).get("judge_runs", 1))
    runs = manifest.get("runs", [])
    if not isinstance(runs, list) or not runs:
        raise ValueError("Manifest must include non-empty runs[]")

    per_run: list[dict[str, Any]] = []
    for run in runs:
        trace_path = Path(run["trajectory_path"])
        if not trace_path.is_absolute():
            trace_path = WORKSPACE / trace_path
        per_run.append(evaluate_run(trace_path, judge_runs=judge_runs))

    summary = aggregate_results(per_run)
    gates = manifest.get("gates", {})
    passed, gate_failures = apply_gates(summary, gates)

    payload = {
        "benchmark_id": benchmark_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pass": passed,
        "gate_failures": gate_failures,
        "gates": gates,
        "summary": summary,
        "runs": per_run,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run unified agent benchmark using manifest.")
    parser.add_argument("--manifest", required=True, help="Path to benchmark manifest JSON")
    parser.add_argument("--output-json", help="Override output JSON path")
    parser.add_argument("--output-md", help="Override output Markdown path")
    parser.add_argument("--trend-jsonl", help="Override trend JSONL path")
    parser.add_argument("--json", action="store_true", help="Print final JSON")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    manifest = _load_json(manifest_path)
    result = run_benchmark(manifest)

    output_cfg = manifest.get("output", {})
    out_json = Path(args.output_json or output_cfg.get("results_json", "90_archive/artifacts/bench/latest.json"))
    out_md = Path(args.output_md or output_cfg.get("results_md", "90_archive/artifacts/bench/latest.md"))
    trend = Path(args.trend_jsonl or output_cfg.get("trend_jsonl", "90_archive/artifacts/bench/trend.jsonl"))

    if not out_json.is_absolute():
        out_json = WORKSPACE / out_json
    if not out_md.is_absolute():
        out_md = WORKSPACE / out_md
    if not trend.is_absolute():
        trend = WORKSPACE / trend

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(out_md, result)

    trend.parent.mkdir(parents=True, exist_ok=True)
    with open(trend, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "ts": result["generated_at"],
            "benchmark_id": result["benchmark_id"],
            "pass": result["pass"],
            "summary": result["summary"],
            "gate_failures": result["gate_failures"],
        }, ensure_ascii=False) + "\n")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"benchmark_id={result['benchmark_id']} pass={result['pass']} runs={result['summary']['runs_total']}")
        if result["gate_failures"]:
            for failure in result["gate_failures"]:
                print(f"- gate_failure: {failure}")
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

