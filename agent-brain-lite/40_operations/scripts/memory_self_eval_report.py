#!/usr/bin/env python3
"""Mine memory self-evaluation logs into an actionable workspace report.

The memory engine appends one JSON object per evaluation to
``.agent/memory/self_eval.jsonl`` (see ``memory_engine/self_eval.py``). That log
grows without bound and is mostly homogeneous, so before pruning it we extract
the signal it carries:

* per-layer coverage (are retrieval/injection/runtime evals actually firing?)
* score distribution and low-score outliers
* failure-mode distribution (storage / retrieval / summary / unknown)
* privacy-scrub and summary-presence failures (data-quality red flags)
* whether entries carry a ``ts`` (time-pruning / windowing depend on it)

Run it standalone for an ad-hoc report, or before pruning so value is captured
before lines are capped.

Usage:
    python 40_operations/scripts/memory_self_eval_report.py
    python 40_operations/scripts/memory_self_eval_report.py --output path.md
    python 40_operations/scripts/memory_self_eval_report.py --input some.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from memory_engine.config import load_config


def _bucket(score: float) -> str:
    if score < 0.5:
        return "<0.5"
    if score < 0.7:
        return "0.5-0.7"
    if score < 0.85:
        return "0.7-0.85"
    if score < 0.95:
        return "0.85-0.95"
    return ">=0.95"


def analyze(path: Path) -> dict:
    layers: Counter = Counter()
    failure_modes: Counter = Counter()
    score_buckets: Counter = Counter()
    layer_scores: dict[str, list[float]] = {}
    private_detected = 0
    summary_fail = 0
    has_failure_mode = 0
    has_ts = 0
    malformed = 0
    total = 0
    low_score_samples: list[dict] = []

    if not path.exists():
        return {"exists": False, "path": str(path)}

    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            layer = obj.get("layer", "?")
            layers[layer] += 1
            if obj.get("ts"):
                has_ts += 1
            score = obj.get("score")
            if isinstance(score, (int, float)):
                score_buckets[_bucket(float(score))] += 1
                layer_scores.setdefault(layer, []).append(float(score))
                if float(score) < 0.7 and len(low_score_samples) < 25:
                    low_score_samples.append(obj)
            checks = obj.get("checks") or {}
            if checks.get("private_content_detected") is True:
                private_detected += 1
            elif checks.get("privacy_scrubbed") is False:
                # Legacy field: False meant private markers were present.
                private_detected += 1
            if checks.get("has_summary") is False:
                summary_fail += 1
            if "failure_mode" in obj:
                has_failure_mode += 1
                failure_modes[obj["failure_mode"]] += 1

    layer_avg = {
        layer: round(sum(scores) / len(scores), 4)
        for layer, scores in layer_scores.items()
        if scores
    }
    return {
        "exists": True,
        "path": str(path),
        "total": total,
        "malformed": malformed,
        "layers": dict(layers.most_common()),
        "layer_avg_score": layer_avg,
        "score_buckets": dict(score_buckets.most_common()),
        "failure_modes": dict(failure_modes.most_common()),
        "entries_with_failure_mode": has_failure_mode,
        "entries_with_ts": has_ts,
        "private_content_detected": private_detected,
        "summary_missing_failures": summary_fail,
        "low_score_samples": low_score_samples,
    }


# Layers the engine is capable of evaluating (memory_engine/self_eval.py).
KNOWN_LAYERS = {"ingest", "retrieval", "injection", "runtime"}


def derive_insights(report: dict) -> list[str]:
    """Turn raw aggregates into concrete, workspace-improving observations."""
    out: list[str] = []
    if not report.get("exists"):
        return ["self_eval.jsonl not found — nothing to analyze."]

    total = report["total"]
    seen = set(report["layers"])
    missing = sorted(KNOWN_LAYERS - seen)
    hook_only_layers = {"retrieval", "injection"}
    worker_only = sorted(set(missing) & {"runtime"})
    hook_missing = sorted(set(missing) & hook_only_layers)
    if hook_missing:
        out.append(
            f"Coverage gap: layers {hook_missing} never logged. The live hook should "
            "emit retrieval/injection via hook_retrieval_injection_eval after each "
            "ingest — verify memory_lifecycle.py is active."
        )
    if worker_only:
        out.append(
            f"Worker-only layers {worker_only} not in log (expected unless the HTTP "
            "memory worker is exercised)."
        )

    if total and report["entries_with_ts"] == 0:
        out.append(
            "No entry carries a `ts` field — this silently breaks time-window "
            "filtering in self_eval_learning_loop.py (all rows look 'in window') "
            "and blocks time-based pruning. Stamp `ts` in MemorySelfEvaluator.log()."
        )
    elif total and report["entries_with_ts"] < total:
        out.append(
            f"Only {report['entries_with_ts']}/{total} entries carry `ts` — "
            "older rows predate timestamping; windowing/pruning are partial."
        )

    if report["malformed"]:
        out.append(
            f"{report['malformed']} malformed line(s) — a writer is emitting "
            "non-JSON; check for crashes mid-append."
        )

    if total and report["entries_with_failure_mode"] / total < 0.05:
        out.append(
            f"Only {report['entries_with_failure_mode']}/{total} entries carry "
            "a failure_mode tag — most rows predate that field and add little "
            "signal, so capping old lines is safe."
        )

    pd = report["private_content_detected"]
    if pd:
        out.append(
            f"{pd} ingest entries flagged private_content_detected=True (markers "
            "present in payload). This indicates the redaction path engaged, not a "
            "leak. Confirm no raw '<private>' survives in raw_events.jsonl / memory.db."
        )
    else:
        out.append("Privacy: no private-content markers seen across entries.")

    sf = report["summary_missing_failures"]
    if sf:
        out.append(f"{sf} ingest entries had an empty summary — composer may be dropping content.")

    fm = report["failure_modes"]
    if fm:
        worst = [k for k in ("storage", "retrieval", "summary") if fm.get(k)]
        if worst:
            detail = ", ".join(f"{k}={fm[k]}" for k in worst)
            out.append(f"Real failure modes observed: {detail}. These are the rows worth keeping/reviewing.")

    low = report["score_buckets"].get("<0.5", 0) + report["score_buckets"].get("0.5-0.7", 0)
    if low:
        out.append(f"{low} evaluations scored <0.7 — sampled in the report for inspection.")

    return out


def render_markdown(report: dict, insights: list[str]) -> str:
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Memory Self-Eval Report",
        "",
        f"- Generated: {now}",
        f"- Source: `{report.get('path')}`",
    ]
    if not report.get("exists"):
        lines.append("\n**Log not found.**")
        return "\n".join(lines) + "\n"

    lines += [
        f"- Total entries: {report['total']}",
        f"- Malformed lines: {report['malformed']}",
        f"- Entries with failure_mode: {report['entries_with_failure_mode']}",
        f"- Entries with ts: {report['entries_with_ts']}",
        "",
        "## Insights",
        "",
    ]
    lines += [f"- {item}" for item in insights]

    lines += ["", "## Layer coverage", "", "| Layer | Count | Avg score |", "|---|---|---|"]
    for layer, count in report["layers"].items():
        avg = report["layer_avg_score"].get(layer, "—")
        lines.append(f"| {layer} | {count} | {avg} |")

    lines += ["", "## Score distribution", "", "| Bucket | Count |", "|---|---|"]
    for bucket in ["<0.5", "0.5-0.7", "0.7-0.85", "0.85-0.95", ">=0.95"]:
        lines.append(f"| {bucket} | {report['score_buckets'].get(bucket, 0)} |")

    lines += ["", "## Failure modes", "", "| Mode | Count |", "|---|---|"]
    if report["failure_modes"]:
        for mode, count in report["failure_modes"].items():
            lines.append(f"| {mode} | {count} |")
    else:
        lines.append("| (none tagged) | 0 |")

    lines += [
        "",
        "## Data-quality checks",
        "",
        f"- Private content detected (ingest): {report['private_content_detected']}",
        f"- Summary-missing failures: {report['summary_missing_failures']}",
    ]

    if report["low_score_samples"]:
        lines += ["", "## Low-score samples (<0.7)", "", "```json"]
        for sample in report["low_score_samples"][:10]:
            lines.append(json.dumps(sample, ensure_ascii=False))
        lines.append("```")

    return "\n".join(lines) + "\n"


def main() -> None:
    cfg = load_config()
    parser = argparse.ArgumentParser(description="Memory self-eval report")
    parser.add_argument("--input", default=str(cfg.self_eval_log_path))
    parser.add_argument(
        "--output",
        default=str(cfg.workspace_root / "40_operations" / "logs" / "self_eval_report.md"),
    )
    args = parser.parse_args()

    report = analyze(Path(args.input))
    insights = derive_insights(report)
    markdown = render_markdown(report, insights)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")

    print(f"Analyzed {report.get('total', 0)} entries from {args.input}")
    print(f"Report written to {out_path}")
    print("\n".join(f"- {i}" for i in insights))


if __name__ == "__main__":
    main()
