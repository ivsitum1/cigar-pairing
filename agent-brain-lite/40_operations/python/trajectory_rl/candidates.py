"""Build learning candidates from low trajectory scores on benchmark traces."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
SKILLS_DIR = WORKSPACE / "30_system" / "SKILLS"
ARTIFACTS_ROOT = WORKSPACE / "90_archive" / "artifacts"
BENCH_RL_DEMO = WORKSPACE / "30_system" / "docs" / "AGENT_BENCHMARK_RL_DEMO.json"

# Substring match on selected_tool -> skill id when manifest omits skill_id
TOOL_SKILL_HINTS: list[tuple[str, str]] = [
    ("pubmed", "literature-synthesis"),
    ("books_rag", "literature-synthesis"),
    ("research-lookup", "research-lookup"),
    ("skill_eval", "validate-setup"),
]

TRAJECTORY_FAIL_THRESHOLD = 0.70


@dataclass
class TrajectoryFailure:
    run_id: str
    trace_path: Path
    skill_id: str
    trajectory_score: float
    weak_metrics: list[str]
    reasons: list[str]


def _import_trajectory_eval():
    scripts = WORKSPACE / "40_operations" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import trajectory_eval_runner  # noqa: WPS433

    return trajectory_eval_runner


def _skill_from_run(run: dict[str, Any], eval_payload: dict[str, Any]) -> str | None:
    sid = run.get("skill_id")
    if isinstance(sid, str) and sid.strip():
        return sid.strip()
    metrics = eval_payload.get("metrics") or {}
    weak = [k for k, v in metrics.items() if isinstance(v, (int, float)) and float(v) < TRAJECTORY_FAIL_THRESHOLD]
    for hint, skill in TOOL_SKILL_HINTS:
        blob = json.dumps(run, ensure_ascii=False).lower()
        if hint in blob:
            return skill
        for event_reason in weak:
            if hint in event_reason:
                return skill
    if "tool_correctness" in weak:
        return "literature-synthesis"
    if "plan_quality" in weak:
        return "research-lookup"
    return None


def _weak_metrics(metrics: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and float(value) < TRAJECTORY_FAIL_THRESHOLD:
            out.append(key)
    return out


def scan_manifest(manifest_path: Path | None = None) -> list[TrajectoryFailure]:
    path = manifest_path or BENCH_RL_DEMO
    if not path.is_file():
        return []
    manifest = json.loads(path.read_text(encoding="utf-8"))
    runner = _import_trajectory_eval()
    failures: list[TrajectoryFailure] = []
    for run in manifest.get("runs") or []:
        trace_rel = run.get("trajectory_path")
        if not trace_rel:
            continue
        trace_path = Path(trace_rel)
        if not trace_path.is_absolute():
            trace_path = WORKSPACE / trace_path
        if not trace_path.is_file():
            continue
        events = runner._load_events(trace_path)
        payload = runner.evaluate_trajectory(events)
        score = payload.get("trajectory_score")
        if not isinstance(score, (int, float)) or float(score) >= TRAJECTORY_FAIL_THRESHOLD:
            continue
        skill_id = _skill_from_run(run, payload)
        if not skill_id:
            continue
        skill_path = SKILLS_DIR / f"SKILL_{skill_id}.md"
        if not skill_path.is_file():
            continue
        weak = _weak_metrics(payload.get("metrics") or {})
        reasons = [f"trajectory:{m}<{TRAJECTORY_FAIL_THRESHOLD}" for m in weak] or [
            f"trajectory_score:{float(score):.2f}"
        ]
        failures.append(
            TrajectoryFailure(
                run_id=str(run.get("run_id") or trace_path.parent.name),
                trace_path=trace_path,
                skill_id=skill_id,
                trajectory_score=float(score),
                weak_metrics=weak,
                reasons=reasons,
            )
        )
    return failures


def scan_artifact_traces(
    *,
    artifacts_root: Path | None = None,
    threshold: float = TRAJECTORY_FAIL_THRESHOLD,
) -> list[TrajectoryFailure]:
    root = artifacts_root or ARTIFACTS_ROOT
    runner = _import_trajectory_eval()
    failures: list[TrajectoryFailure] = []
    for trace_path in root.glob("**/trajectory.jsonl"):
        events = runner._load_events(trace_path)
        payload = runner.evaluate_trajectory(events)
        score = payload.get("trajectory_score")
        if not isinstance(score, (int, float)) or float(score) >= threshold:
            continue
        skill_id = None
        for hint, sid in TOOL_SKILL_HINTS:
            text = trace_path.read_text(encoding="utf-8").lower()
            if hint in text:
                skill_id = sid
                break
        if not skill_id:
            continue
        skill_path = SKILLS_DIR / f"SKILL_{skill_id}.md"
        if not skill_path.is_file():
            continue
        weak = _weak_metrics(payload.get("metrics") or {})
        failures.append(
            TrajectoryFailure(
                run_id=trace_path.parent.name,
                trace_path=trace_path,
                skill_id=skill_id,
                trajectory_score=float(score),
                weak_metrics=weak,
                reasons=[f"artifact_trace:{trace_path.parent.name}"],
            )
        )
    return failures
