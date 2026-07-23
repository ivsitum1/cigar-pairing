#!/usr/bin/env python3
"""Self-eval driven learning loop for skills and rules."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))
SELF_EVAL_LOG = WORKSPACE / ".agent" / "memory" / "self_eval.jsonl"
BENCH_RL_MANIFEST = WORKSPACE / "30_system" / "docs" / "AGENT_BENCHMARK_RL_DEMO.json"
MEMORY_EVENTS_LOG = WORKSPACE / ".agent" / "memory" / "raw_events.jsonl"
EVAL_EVENTS_LOG = WORKSPACE / ".agent" / "memory" / "eval_events.jsonl"
ERROR_LOG = WORKSPACE / ".cursor" / "errors" / "error_log.jsonl"
BENCHMARK_TREND_JSONL = WORKSPACE / "90_archive" / "artifacts" / "bench" / "trend.jsonl"
LEDGER_JSONL = WORKSPACE / "30_system/docs" / "LEARNING_UPDATES.jsonl"
DIGEST_PROPOSAL_LEDGER = WORKSPACE / ".agent" / "memory" / "digest_proposal_ledger.jsonl"
LEDGER_MD = WORKSPACE / "30_system/docs" / "LEARNING_UPDATES.md"
TASK_DIR = WORKSPACE / ".agent" / "task"
SKILLS_DIR = WORKSPACE / "30_system/SKILLS"
RULES_DIR = WORKSPACE / ".cursor" / "rules"
ARTIFACTS_DIR = WORKSPACE / "90_archive/artifacts"
HIGH_RISK_RULES = {
    RULES_DIR / "core-principles.mdc",
    RULES_DIR / "00_orchestrator_agent.mdc",
}


@dataclass
class Candidate:
    candidate_id: str
    target_type: str
    target_path: Path
    frequency: int
    avg_score: float
    signal_score: float
    reasons: list[str]
    signal_window_days: int
    trajectory_trace: str | None = None
    trajectory_score: float | None = None


@dataclass
class GateConfig:
    accept_threshold: float = 0.10
    rollback_threshold: float = 0.00
    tie_breaker: str = "revert"


@dataclass
class ScoreWeights:
    eval_weight: float = 0.55
    tests_weight: float = 0.25
    lint_weight: float = 0.10
    stability_weight: float = 0.10
    trajectory_weight: float = 0.30

    def normalized(self, *, use_trajectory: bool) -> ScoreWeights:
        if not use_trajectory or self.trajectory_weight <= 0:
            total = self.eval_weight + self.tests_weight + self.lint_weight + self.stability_weight
            if total <= 0:
                return ScoreWeights(trajectory_weight=0.0)
            scale = 1.0 / total
            return ScoreWeights(
                eval_weight=self.eval_weight * scale,
                tests_weight=self.tests_weight * scale,
                lint_weight=self.lint_weight * scale,
                stability_weight=self.stability_weight * scale,
                trajectory_weight=0.0,
            )
        remaining = 1.0 - self.trajectory_weight
        base = self.eval_weight + self.tests_weight + self.lint_weight + self.stability_weight
        if base <= 0:
            return ScoreWeights(
                eval_weight=0.0,
                tests_weight=0.0,
                lint_weight=0.0,
                stability_weight=0.0,
                trajectory_weight=1.0,
            )
        scale = remaining / base
        return ScoreWeights(
            eval_weight=self.eval_weight * scale,
            tests_weight=self.tests_weight * scale,
            lint_weight=self.lint_weight * scale,
            stability_weight=self.stability_weight * scale,
            trajectory_weight=self.trajectory_weight,
        )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    items: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return items


def _parse_ts(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _in_window(entry: dict[str, Any], threshold: datetime) -> bool:
    """Return True when entry falls inside the window; legacy rows without ts are excluded."""
    ts = _parse_ts(str(entry.get("ts", "")))
    if ts is None:
        return False
    return ts >= threshold


def _skill_ids() -> set[str]:
    ids = set()
    for path in SKILLS_DIR.glob("SKILL_*.md"):
        ids.add(path.stem.replace("SKILL_", ""))
    return ids


def _target_from_memory(entry: dict[str, Any], known_skills: set[str]) -> tuple[str, Path] | None:
    blob = json.dumps(entry, ensure_ascii=False).lower()
    for tag in [blob]:
        for skill_id in known_skills:
            if skill_id in tag:
                return "skill", SKILLS_DIR / f"SKILL_{skill_id}.md"
    if "rule" in blob or "mdc" in blob:
        m = re.search(r"([a-z0-9\-_]+)\.mdc", blob)
        if m:
            return "rule", RULES_DIR / f"{m.group(1)}.mdc"
    return None


def _benchmark_failure_multiplier(window_days: int) -> float:
    events = _read_jsonl(BENCHMARK_TREND_JSONL)
    if not events:
        return 1.0
    threshold = datetime.now(timezone.utc) - timedelta(days=window_days)
    recent = []
    for row in events:
        ts = _parse_ts(str(row.get("ts", "")))
        if ts is None or ts < threshold:
            continue
        recent.append(row)
    if not recent:
        return 1.0
    fail_count = sum(1 for row in recent if row.get("pass") is False)
    fail_ratio = fail_count / len(recent)
    # Increase learning pressure when benchmark repeatedly fails.
    return round(1.0 + (0.5 * fail_ratio), 3)


def _trajectory_score_for_skill(skill_id: str) -> tuple[float | None, str | None]:
    try:
        from trajectory_rl.candidates import scan_manifest

        for failure in scan_manifest(BENCH_RL_MANIFEST):
            if failure.skill_id == skill_id:
                rel = str(failure.trace_path.relative_to(WORKSPACE)).replace("\\", "/")
                return failure.trajectory_score, rel
    except Exception:
        pass
    return None, None


def build_trajectory_candidates() -> list[Candidate]:
    try:
        from trajectory_rl.candidates import scan_manifest
    except ImportError:
        return []

    out: list[Candidate] = []
    for index, failure in enumerate(scan_manifest(BENCH_RL_MANIFEST), start=1):
        target_path = SKILLS_DIR / f"SKILL_{failure.skill_id}.md"
        if not target_path.is_file():
            continue
        trace_rel = str(failure.trace_path.relative_to(WORKSPACE)).replace("\\", "/")
        out.append(
            Candidate(
                candidate_id=f"cand_traj_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{index:03d}",
                target_type="skill",
                target_path=target_path,
                frequency=3,
                avg_score=0.55,
                signal_score=round(3 * (1 - failure.trajectory_score), 3),
                reasons=failure.reasons + [f"trace:{trace_rel}"],
                signal_window_days=7,
                trajectory_trace=trace_rel,
                trajectory_score=failure.trajectory_score,
            )
        )
    return out


def build_candidates(window_days: int) -> list[Candidate]:
    known_skills = _skill_ids()
    threshold = datetime.now(timezone.utc) - timedelta(days=window_days)
    self_evals = [x for x in _read_jsonl(SELF_EVAL_LOG) if _in_window(x, threshold)]
    memory_events = [x for x in _read_jsonl(MEMORY_EVENTS_LOG) if _in_window(x, threshold)]
    error_events = [x for x in _read_jsonl(ERROR_LOG) if _in_window(x, threshold)]

    grouped: dict[Path, dict[str, Any]] = {}
    for event in memory_events:
        target = _target_from_memory(event, known_skills)
        if not target:
            continue
        target_type, target_path = target
        bucket = grouped.setdefault(target_path, {"target_type": target_type, "count": 0, "reasons": []})
        bucket["count"] += 1
        bucket["reasons"].append(f"memory:{event.get('lifecycle', 'unknown')}")

    for event in error_events:
        target = _target_from_memory(event, known_skills)
        if not target:
            continue
        target_type, target_path = target
        bucket = grouped.setdefault(target_path, {"target_type": target_type, "count": 0, "reasons": []})
        bucket["count"] += 1
        bucket["reasons"].append(f"error:{event.get('sev', 'unknown')}")

    if not grouped:
        # fallback: generic candidate from low self-eval, targeting skills with eval files
        avg = sum(float(x.get("score", 0.0)) for x in self_evals) / max(1, len(self_evals))
        if avg < 0.8:
            for skill in sorted(known_skills):
                skill_eval = SKILLS_DIR / "evals" / f"{skill}.json"
                if skill_eval.exists():
                    target_path = SKILLS_DIR / f"SKILL_{skill}.md"
                    grouped[target_path] = {
                        "target_type": "skill",
                        "count": 3,
                        "reasons": ["low_global_self_eval"],
                    }
                    break

    scores = [float(x.get("score", 0.0)) for x in self_evals]
    avg_score = sum(scores) / max(1, len(scores))
    candidates: list[Candidate] = []
    index = 0
    benchmark_multiplier = _benchmark_failure_multiplier(window_days)
    for target_path, data in grouped.items():
        frequency = int(data["count"])
        signal_score = frequency * (1 - avg_score) * benchmark_multiplier
        if frequency < 3 or avg_score > 0.8 or signal_score < 0.6:
            continue
        index += 1
        candidates.append(
            Candidate(
                candidate_id=f"cand_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{index:03d}",
                target_type=data["target_type"],
                target_path=target_path,
                frequency=frequency,
                avg_score=round(avg_score, 3),
                signal_score=round(signal_score, 3),
                reasons=sorted(set(data["reasons"])),
                signal_window_days=window_days,
            )
        )
    merged: dict[Path, Candidate] = {c.target_path: c for c in candidates}
    for traj_cand in build_trajectory_candidates():
        existing = merged.get(traj_cand.target_path)
        if existing is None or traj_cand.signal_score > existing.signal_score:
            merged[traj_cand.target_path] = traj_cand
        elif existing is not None and traj_cand.trajectory_trace:
            existing.reasons = sorted(set(existing.reasons + traj_cand.reasons))
            existing.trajectory_trace = traj_cand.trajectory_trace
            existing.trajectory_score = traj_cand.trajectory_score
    return sorted(merged.values(), key=lambda c: c.signal_score, reverse=True)


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_patch(candidate: Candidate) -> tuple[str, str]:
    original = _load_text(candidate.target_path)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    marker = f"<!-- auto-learn:{candidate.candidate_id} -->"
    if marker in original:
        return original, "already-patched"
    trajectory_reasons = [r for r in candidate.reasons if r.startswith("trajectory:")]
    if trajectory_reasons or candidate.trajectory_trace:
        enforcement = (
            "- Before citing literature, call the PubMed MCP search tool (not generic web fetch) "
            "unless the user explicitly requests open-web-only search.\n"
            "- On benchmark runs, set `expected_tool` on `tool_selected` trajectory events per "
            "`30_system/docs/TRAJECTORY_EMIT_PROTOCOL.md`.\n"
        )
        if any("tool_correctness" in r for r in trajectory_reasons):
            enforcement = (
                "- Match the declared plan step to the correct MCP tool; do not substitute "
                "web fetch when PubMed is required.\n" + enforcement
            )
        block = (
            f"\n\n{marker}\n"
            f"## Trajectory RL Guardrail ({stamp})\n"
            f"- Trigger reasons: {', '.join(candidate.reasons[:5])}\n"
            f"- Trace reference: `{candidate.trajectory_trace or 'n/a'}`\n"
            f"{enforcement}"
            f"- Rollback: remove this block if skill evals or trajectory benchmark regress.\n"
        )
        return original + block, "append-trajectory-guardrail"
    block = (
        f"\n\n{marker}\n"
        f"## Auto-Learned Guardrail ({stamp})\n"
        f"- Trigger reasons: {', '.join(candidate.reasons[:4])}\n"
        f"- Enforcement: verify assumptions explicitly and add a short self-check before final output.\n"
        f"- Rollback: remove this block if evals regress.\n"
    )
    return original + block, "append-guardrail-block"


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def evaluate_trajectory_trace(trace_rel: str | None) -> tuple[float | None, bool, str]:
    if not trace_rel:
        return None, True, "no_trajectory_trace"
    trace_path = WORKSPACE / trace_rel.replace("/", os.sep)
    if not trace_path.is_file():
        return None, True, "trajectory_trace_missing"
    scripts = WORKSPACE / "40_operations" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import trajectory_eval_runner

    events = trajectory_eval_runner._load_events(trace_path)
    payload = trajectory_eval_runner.evaluate_trajectory(events)
    score = payload.get("trajectory_score")
    if not isinstance(score, (int, float)):
        return None, True, "trajectory_score_missing"
    return float(score) * 100.0, True, _safe_rel(trace_path)


def _score_composite(
    eval_metric: float | None,
    eval_ok: bool,
    trajectory_metric_100: float | None,
    weights: ScoreWeights,
) -> float | None:
    use_traj = trajectory_metric_100 is not None
    w = weights.normalized(use_trajectory=use_traj)
    if eval_metric is None and not use_traj:
        return None
    eval_score = max(0.0, min(100.0, eval_metric if eval_metric is not None else 0.0))
    tests_score = 100.0 if eval_ok else 0.0
    lint_score = 100.0
    stability_score = 100.0
    traj_score = max(0.0, min(100.0, trajectory_metric_100 if trajectory_metric_100 is not None else 0.0))
    score = (
        w.eval_weight * eval_score
        + w.tests_weight * tests_score
        + w.lint_weight * lint_score
        + w.stability_weight * stability_score
        + w.trajectory_weight * traj_score
    )
    return round(score, 4)


def _decide(
    before_score: float | None,
    after_score: float | None,
    after_ok: bool,
    gate: GateConfig,
) -> tuple[str, str, float | None]:
    if not after_ok:
        return "revert", "evaluation_failed", None if before_score is None or after_score is None else round(after_score - before_score, 4)
    if before_score is None or after_score is None:
        return "revert", "missing_scores", None
    delta = round(after_score - before_score, 4)
    if delta >= gate.accept_threshold:
        return "accept", "improved_metric", delta
    if delta <= gate.rollback_threshold:
        return "revert", "no_metric_improvement", delta
    if gate.tie_breaker == "accept":
        return "accept", "tie_breaker_accept", delta
    return "revert", "tie_breaker_revert", delta


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"processed_candidate_ids": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload.setdefault("processed_candidate_ids", [])
            return payload
    except json.JSONDecodeError:
        pass
    return {"processed_candidate_ids": []}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _log_memory_signal(record: dict[str, Any]) -> None:
    event = {
        "event_hash": None,
        "lifecycle": "AutoLearningSignal",
        "session_id": record.get("run_id", "unknown"),
        "project_scope": WORKSPACE.name,
        "payload": record,
        "ts": record.get("ts", datetime.now(timezone.utc).isoformat()),
    }
    # Keep learning telemetry, but do not pollute primary runtime memory stream.
    _append_jsonl(EVAL_EVENTS_LOG, event)


def _log_changelog_change(target_path: str, action: str, reason: str, run_id: str, candidate_id: str) -> None:
    cmd = [
        sys.executable,
        str(WORKSPACE / "40_operations/scripts" / "changelog_auto.py"),
        "--manual-message",
        f"auto-learn {action}: {candidate_id} ({reason})",
        "--manual-file",
        target_path,
        "--manual-source",
        f"self_eval_learning_loop:{run_id}",
    ]
    _run(cmd)


def evaluate_skill(candidate: Candidate) -> tuple[float | None, bool, str]:
    skill_id = candidate.target_path.stem.replace("SKILL_", "")
    outputs = SKILLS_DIR / "evals" / f"{skill_id}_outputs.json"
    if not outputs.exists():
        return None, False, "missing_outputs_file"
    cmd = [
        sys.executable,
        str(WORKSPACE / "40_operations/scripts" / "skill_eval_runner.py"),
        "--skill-id",
        skill_id,
        "--outputs",
        str(outputs),
        "--json",
    ]
    code, out, err = _run(cmd)
    if code != 0:
        return None, False, f"eval_failed:{err.strip() or out.strip()}"
    try:
        payload = json.loads(out)
        return float(payload.get("pass_rate_pct", 0.0)), True, cmd[0] + " " + " ".join(cmd[1:])
    except json.JSONDecodeError:
        return None, False, "invalid_eval_json"


def append_ledger(record: dict[str, Any]) -> None:
    LEDGER_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_JSONL, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    LEDGER_MD.parent.mkdir(parents=True, exist_ok=True)
    if not LEDGER_MD.exists():
        LEDGER_MD.write_text("# Learning Updates\n\n", encoding="utf-8")
    with open(LEDGER_MD, "a", encoding="utf-8") as handle:
        handle.write(
            f"\n## {record['ts']} `{record['candidate_id']}`\n"
            f"- target: `{record['target_path']}`\n"
            f"- action: `{record['action']}`\n"
            f"- before: `{record.get('before_metric')}` after: `{record.get('after_metric')}`\n"
            f"- reason: {record['decision_reason']}\n"
        )


def persist_proposals(run_id: str, proposals: list[Candidate]) -> Path:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    path = TASK_DIR / f"learning_{run_id}.json"
    payload = [
        {
            "candidate_id": c.candidate_id,
            "target_type": c.target_type,
            "target_path": str(c.target_path.relative_to(WORKSPACE)),
            "frequency": c.frequency,
            "avg_score": c.avg_score,
            "signal_score": c.signal_score,
            "reasons": c.reasons,
            "signal_window_days": c.signal_window_days,
        }
        for c in proposals
    ]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_learning_loop(
    mode: str,
    window_days: int,
    max_candidates: int,
    allow_rule_apply: bool,
    dry_run: bool,
    gate: GateConfig,
    weights: ScoreWeights,
    seed: int,
    resume_run_id: str | None,
) -> dict[str, Any]:
    run_id = resume_run_id or f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    run_dir = ARTIFACTS_DIR / run_id
    manifest_path = run_dir / "manifest.json"
    metrics_path = run_dir / "metrics.json"
    decision_path = run_dir / "decision.md"
    state_path = run_dir / "state.json"
    metrics_jsonl_path = run_dir / "metrics.jsonl"

    state = _load_state(state_path)
    processed_ids = set(state.get("processed_candidate_ids", []))
    candidates = build_candidates(window_days)[:max_candidates]
    proposal_path = persist_proposals(run_id, candidates)
    _write_json(
        manifest_path,
        {
            "run_id": run_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "seed": seed,
            "window_days": window_days,
            "max_candidates": max_candidates,
            "allow_rule_apply": allow_rule_apply,
            "dry_run": dry_run,
            "signal_source": "memory_only",
            "thresholds": {
                "accept_threshold": gate.accept_threshold,
                "rollback_threshold": gate.rollback_threshold,
                "tie_breaker": gate.tie_breaker,
            },
            "weights": {
                "eval_weight": weights.eval_weight,
                "tests_weight": weights.tests_weight,
                "lint_weight": weights.lint_weight,
                "stability_weight": weights.stability_weight,
                "trajectory_weight": weights.trajectory_weight,
            },
            "proposal_file": _safe_rel(proposal_path),
        },
    )

    summary: dict[str, Any] = {
        "run_id": run_id,
        "mode": mode,
        "proposal_file": _safe_rel(proposal_path),
        "artifact_paths": {
            "manifest": _safe_rel(manifest_path),
            "metrics": _safe_rel(metrics_path),
            "decision": _safe_rel(decision_path),
            "state": _safe_rel(state_path),
        },
        "candidates": len(candidates),
        "results": [],
    }
    metrics_rows: list[dict[str, Any]] = []
    decisions_md: list[str] = [f"# Experiment Decisions ({run_id})", ""]

    for candidate in candidates:
        if candidate.candidate_id in processed_ids:
            continue
        rel_target = _safe_rel(candidate.target_path)
        base_record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            "candidate_id": candidate.candidate_id,
            "target_path": rel_target,
            "signal_score": candidate.signal_score,
            "before_metric": None,
            "after_metric": None,
            "baseline_score": None,
            "candidate_score": None,
            "delta": None,
            "40_operations/tests": {"command": "", "ok": False},
            "patch_summary": "append-guardrail-block",
        }
        if mode == "propose":
            record = {
                **base_record,
                "action": "proposed",
                "decision_reason": "proposal_only_mode",
                "decision": "propose",
                "evaluation_ok": True,
            }
            append_ledger(record)
            _log_memory_signal(record)
            metrics_rows.append(record)
            _append_jsonl(metrics_jsonl_path, record)
            summary["results"].append(record)
            processed_ids.add(candidate.candidate_id)
            continue

        if candidate.target_type == "rule":
            if candidate.target_path in HIGH_RISK_RULES:
                record = {
                    **base_record,
                    "action": "skipped",
                    "decision": "skip",
                    "decision_reason": "high_risk_rule_no_auto_apply",
                    "evaluation_ok": False,
                }
                append_ledger(record)
                _log_memory_signal(record)
                metrics_rows.append(record)
                _append_jsonl(metrics_jsonl_path, record)
                summary["results"].append(record)
                processed_ids.add(candidate.candidate_id)
                continue
            if not allow_rule_apply:
                record = {
                    **base_record,
                    "action": "skipped",
                    "decision": "skip",
                    "decision_reason": "rule_apply_disabled",
                    "evaluation_ok": False,
                }
                append_ledger(record)
                _log_memory_signal(record)
                metrics_rows.append(record)
                _append_jsonl(metrics_jsonl_path, record)
                summary["results"].append(record)
                processed_ids.add(candidate.candidate_id)
                continue

        before_metric, before_ok, before_reason = evaluate_skill(candidate) if candidate.target_type == "skill" else (None, True, "rule_no_eval")
        traj_rel = candidate.trajectory_trace
        if candidate.target_type == "skill" and not traj_rel:
            skill_id = candidate.target_path.stem.replace("SKILL_", "")
            _, traj_rel = _trajectory_score_for_skill(skill_id)
        before_traj_100, traj_ok, traj_cmd = evaluate_trajectory_trace(traj_rel)
        before_score = (
            _score_composite(before_metric, before_ok, before_traj_100, weights)
            if candidate.target_type == "skill"
            else (100.0 if before_ok else 0.0)
        )
        new_text, patch_summary = build_patch(candidate)
        old_text = _load_text(candidate.target_path)
        if not candidate.target_path.exists():
            record = {
                **base_record,
                "action": "skipped",
                "decision": "skip",
                "decision_reason": "target_missing",
                "evaluation_ok": False,
            }
            append_ledger(record)
            _log_memory_signal(record)
            metrics_rows.append(record)
            _append_jsonl(metrics_jsonl_path, record)
            summary["results"].append(record)
            processed_ids.add(candidate.candidate_id)
            continue

        if dry_run:
            record = {
                **base_record,
                "action": "proposed",
                "decision": "propose",
                "decision_reason": "dry_run",
                "before_metric": before_metric,
                "baseline_score": before_score,
                "patch_summary": patch_summary,
                "40_operations/tests": {"command": before_reason, "ok": before_ok},
                "evaluation_ok": before_ok,
            }
            append_ledger(record)
            _log_memory_signal(record)
            metrics_rows.append(record)
            _append_jsonl(metrics_jsonl_path, record)
            summary["results"].append(record)
            processed_ids.add(candidate.candidate_id)
            continue

        candidate.target_path.write_text(new_text, encoding="utf-8")
        after_metric, after_ok, after_reason = evaluate_skill(candidate) if candidate.target_type == "skill" else (None, True, "rule_no_eval")
        after_traj_100, _, _ = evaluate_trajectory_trace(traj_rel)
        after_score = (
            _score_composite(after_metric, after_ok, after_traj_100, weights)
            if candidate.target_type == "skill"
            else (100.0 if after_ok else 0.0)
        )
        decision, decision_reason, delta = _decide(before_score, after_score, after_ok, gate) if candidate.target_type == "skill" else ("accept" if after_ok else "revert", "rule_applied_guarded" if after_ok else "rule_validation_failed", None)
        new_hash = _sha256_text(new_text)
        old_hash = _sha256_text(old_text)

        if decision == "accept":
            record = {
                **base_record,
                "action": "applied",
                "decision": "accept",
                "decision_reason": decision_reason,
                "before_metric": before_metric,
                "after_metric": after_metric,
                "baseline_score": before_score,
                "candidate_score": after_score,
                "delta": delta,
                "diff_hash": new_hash,
                "patch_summary": patch_summary,
                "40_operations/tests": {"command": after_reason, "ok": after_ok},
                "evaluation_ok": after_ok,
                "thresholds": {
                    "accept_threshold": gate.accept_threshold,
                    "rollback_threshold": gate.rollback_threshold,
                    "tie_breaker": gate.tie_breaker,
                },
            }
            append_ledger(record)
            _log_memory_signal(record)
            _log_changelog_change(rel_target, record["action"], record["decision_reason"], run_id, candidate.candidate_id)
            metrics_rows.append(record)
            _append_jsonl(metrics_jsonl_path, record)
            summary["results"].append(record)
        else:
            candidate.target_path.write_text(old_text, encoding="utf-8")
            record = {
                **base_record,
                "action": "reverted",
                "decision": "revert",
                "decision_reason": decision_reason,
                "before_metric": before_metric,
                "after_metric": after_metric,
                "baseline_score": before_score,
                "candidate_score": after_score,
                "delta": delta,
                "diff_hash": old_hash,
                "patch_summary": patch_summary,
                "40_operations/tests": {"command": after_reason, "ok": after_ok},
                "evaluation_ok": after_ok,
                "thresholds": {
                    "accept_threshold": gate.accept_threshold,
                    "rollback_threshold": gate.rollback_threshold,
                    "tie_breaker": gate.tie_breaker,
                },
            }
            append_ledger(record)
            _log_memory_signal(record)
            _log_changelog_change(rel_target, record["action"], record["decision_reason"], run_id, candidate.candidate_id)
            metrics_rows.append(record)
            _append_jsonl(metrics_jsonl_path, record)
            summary["results"].append(record)
        decisions_md.extend(
            [
                f"## {candidate.candidate_id}",
                f"- target: `{rel_target}`",
                f"- action: `{record['action']}`",
                f"- decision: `{record['decision']}`",
                f"- reason: {record['decision_reason']}",
                f"- baseline_score: `{record.get('baseline_score')}`",
                f"- candidate_score: `{record.get('candidate_score')}`",
                f"- delta: `{record.get('delta')}`",
                "",
            ]
        )
        processed_ids.add(candidate.candidate_id)
        _write_json(state_path, {"processed_candidate_ids": sorted(processed_ids)})

    _write_json(
        metrics_path,
        {
            "run_id": run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(metrics_rows),
            "results": metrics_rows,
        },
    )
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text("\n".join(decisions_md) + "\n", encoding="utf-8")
    _write_json(state_path, {"processed_candidate_ids": sorted(processed_ids)})
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-eval driven rules/skills learning loop")
    parser.add_argument("--mode", choices=["propose", "apply"], default="propose")
    parser.add_argument("--window-days", type=int, default=7)
    parser.add_argument("--max-candidates", type=int, default=3)
    parser.add_argument("--accept-threshold", type=float, default=0.10)
    parser.add_argument("--rollback-threshold", type=float, default=0.00)
    parser.add_argument("--tie-breaker", choices=["accept", "revert"], default="revert")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume-run-id", default=None)
    parser.add_argument("--allow-rule-apply", action="store_true", help="Allow medium-risk .mdc rule auto-apply")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--trajectory-weight", type=float, default=0.30)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--ingest-machine-digest",
        metavar="WEEK",
        help="Ingest machine_digest_decisions_WEEK.json into digest proposal ledger",
    )
    args = parser.parse_args()

    if args.ingest_machine_digest:
        scripts_dir = WORKSPACE / "40_operations" / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from machine_digest_learning import ingest_decisions

        path = TASK_DIR / f"machine_digest_decisions_{args.ingest_machine_digest}.json"
        if not path.is_file():
            print(f"ERROR: {path} not found", file=sys.stderr)
            return 1
        n = ingest_decisions(path)
        print(json.dumps({"ingested": n, "ledger": str(DIGEST_PROPOSAL_LEDGER)}, indent=2) if args.json else f"Ingested {n} digest decisions")
        return 0

    summary = run_learning_loop(
        mode=args.mode,
        window_days=args.window_days,
        max_candidates=args.max_candidates,
        allow_rule_apply=args.allow_rule_apply,
        dry_run=args.dry_run,
        gate=GateConfig(
            accept_threshold=args.accept_threshold,
            rollback_threshold=args.rollback_threshold,
            tie_breaker=args.tie_breaker,
        ),
        weights=ScoreWeights(trajectory_weight=args.trajectory_weight),
        seed=args.seed,
        resume_run_id=args.resume_run_id,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Run: {summary['run_id']} | mode={summary['mode']} | candidates={summary['candidates']}")
        for item in summary["results"]:
            print(f"- {item['candidate_id']} {item['action']} ({item['decision_reason']}) -> {item['target_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

