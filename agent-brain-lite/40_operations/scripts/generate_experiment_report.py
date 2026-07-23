#!/usr/bin/env python3
"""Generate a markdown summary report for an experiment run."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = WORKSPACE / "90_archive/artifacts"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(round(statistics.mean(values), 4))


def generate_report(run_id: str, output_path: Path | None) -> Path:
    run_dir = ARTIFACTS_DIR / run_id
    manifest = _load_json(run_dir / "manifest.json")
    metrics = _load_json(run_dir / "metrics.json")
    rows = list(metrics.get("results", []))

    actions_count: dict[str, int] = {"applied": 0, "reverted": 0, "skipped": 0, "proposed": 0}
    baseline_scores: list[float] = []
    candidate_scores: list[float] = []
    deltas: list[float] = []

    for row in rows:
        action = str(row.get("action", ""))
        if action in actions_count:
            actions_count[action] += 1
        baseline = row.get("baseline_score")
        candidate = row.get("candidate_score")
        delta = row.get("delta")
        if isinstance(baseline, (int, float)):
            baseline_scores.append(float(baseline))
        if isinstance(candidate, (int, float)):
            candidate_scores.append(float(candidate))
        if isinstance(delta, (int, float)):
            deltas.append(float(delta))

    positive_delta_rate = 0.0
    if deltas:
        positive_delta_rate = round(sum(1 for d in deltas if d > 0) / len(deltas), 4)

    lines = [
        f"# Experiment Report ({run_id})",
        "",
        "## Run Summary",
        f"- run_id: `{run_id}`",
        f"- mode: `{manifest.get('mode')}`",
        f"- generated_at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- candidates_total: `{len(rows)}`",
        f"- accepted: `{actions_count['applied']}`",
        f"- reverted: `{actions_count['reverted']}`",
        f"- skipped: `{actions_count['skipped']}`",
        f"- proposed: `{actions_count['proposed']}`",
        "",
        "## Quality Snapshot",
        f"- avg_baseline_score: `{_avg(baseline_scores)}`",
        f"- avg_candidate_score: `{_avg(candidate_scores)}`",
        f"- avg_delta: `{_avg(deltas)}`",
        f"- positive_delta_rate: `{positive_delta_rate}`",
        "",
        "## Decisions",
        "| candidate_id | target_path | action | decision | delta | reason |",
        "|---|---|---|---|---:|---|",
    ]

    for row in rows:
        lines.append(
            "| {candidate_id} | {target_path} | {action} | {decision} | {delta} | {reason} |".format(
                candidate_id=row.get("candidate_id", ""),
                target_path=row.get("target_path", ""),
                action=row.get("action", ""),
                decision=row.get("decision", ""),
                delta=row.get("delta", ""),
                reason=row.get("decision_reason", ""),
            )
        )

    lines.extend(
        [
            "",
            "## Risk Notes",
            "- policy_boundary_violations: `manual review required`",
            "- repeated_eval_failures: `manual review required`",
            "- suspicious_metric_jumps: `manual review required`",
            "",
            "## Recommended Next Action",
            "- Continue with one additional single-change iteration focused on the highest-value remaining candidate.",
            "",
        ]
    )

    destination = output_path or (run_dir / "report.md")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate markdown report from experiment 90_archive/artifacts")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", default=None, help="Optional custom report output path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else None
    generated = generate_report(args.run_id, output_path)
    payload = {"run_id": args.run_id, "report_path": str(generated)}

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Generated report: {generated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
