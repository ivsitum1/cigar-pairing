#!/usr/bin/env python3
"""RAG-layer evaluator for agent run traces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def _load_events(path: Path) -> list[dict[str, Any]]:
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def evaluate_rag(events: list[dict[str, Any]]) -> dict[str, Any]:
    final_answer_payload: dict[str, Any] = {}
    for event in reversed(events):
        if event.get("event_type") == "final_answer" and isinstance(event.get("payload"), dict):
            final_answer_payload = event["payload"]
            break

    rag = final_answer_payload.get("rag_metrics", {})
    metrics = {
        "context_precision": None,
        "faithfulness": None,
        "answer_relevancy": None,
        "context_recall": None,
    }
    missing: list[str] = []
    for key in metrics:
        value = rag.get(key)
        if isinstance(value, (int, float)):
            metrics[key] = float(value)
        else:
            missing.append(key)

    rag_score = _mean([v for v in metrics.values() if isinstance(v, (int, float))])

    issues: list[str] = []
    if not final_answer_payload:
        issues.append("missing_final_answer_event")
    if all(v is None for v in metrics.values()):
        issues.append("missing_rag_metrics")

    run_id = str(events[0].get("run_id", "")) if events else ""
    return {
        "run_id": run_id,
        "metrics": metrics,
        "rag_score": rag_score,
        "missing_signals": missing,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate RAG metrics from a run trace JSONL.")
    parser.add_argument("--trace", required=True, help="Path to run trace JSONL")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    trace = Path(args.trace)
    if not trace.exists():
        raise FileNotFoundError(f"Trace not found: {trace}")
    result = evaluate_rag(_load_events(trace))
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

