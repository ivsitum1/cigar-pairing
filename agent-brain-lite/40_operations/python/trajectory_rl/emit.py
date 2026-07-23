"""Append trajectory JSONL events (no PHI in payloads). See TRAJECTORY_EMIT_PROTOCOL.md."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
SESSION_STATE = WORKSPACE / ".agent" / "memory" / "trajectory_session.json"
MILESTONE_FLAG = WORKSPACE / ".agent" / "memory" / "milestone_consolidate.flag"
EVAL_APPROVE_FILE = WORKSPACE / ".agent" / "memory" / "consolidate_eval_approved.json"
ARTIFACTS_ROOT = WORKSPACE / "90_archive" / "artifacts"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _enabled() -> bool:
    return os.environ.get("TRAJECTORY_RL_DISABLED", "").strip() not in {"1", "true", "TRUE"}


def _consolidate_threshold() -> int:
    raw = os.environ.get("TRAJECTORY_CONSOLIDATE_THRESHOLD", "25").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 25


def _load_session() -> dict[str, Any]:
    default: dict[str, Any] = {
        "run_id": f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "trace_path": None,
        "event_count": 0,
        "buffer_events": [],
    }
    if not SESSION_STATE.exists():
        return default
    try:
        data = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("run_id", "trace_path", "event_count", "buffer_events"):
                if key in data:
                    default[key] = data[key]
    except json.JSONDecodeError:
        pass
    return default


def _save_session(state: dict[str, Any]) -> None:
    SESSION_STATE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_run_artifact_dir(run_id: str) -> Path:
    run_dir = ARTIFACTS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def resolve_trace_path(run_id: str | None = None) -> Path:
    state = _load_session()
    rid = run_id or str(state.get("run_id") or f"run_{uuid.uuid4().hex[:12]}")
    run_dir = ensure_run_artifact_dir(rid)
    return run_dir / "trajectory.jsonl"


def init_session(*, run_id: str | None = None, reset: bool = False) -> Path:
    if not _enabled():
        return resolve_trace_path(run_id)
    if reset or run_id:
        rid = run_id or f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        trace = ensure_run_artifact_dir(rid) / "trajectory.jsonl"
        _save_session({"run_id": rid, "trace_path": str(trace.relative_to(WORKSPACE)).replace("\\", "/")})
        return trace
    state = _load_session()
    if state.get("trace_path"):
        path = WORKSPACE / str(state["trace_path"])
        if path.is_file():
            return path
    rid = str(state.get("run_id") or f"run_{uuid.uuid4().hex[:12]}")
    trace = ensure_run_artifact_dir(rid) / "trajectory.jsonl"
    _save_session({"run_id": rid, "trace_path": str(trace.relative_to(WORKSPACE)).replace("\\", "/")})
    return trace


def get_active_trace_path() -> Path | None:
    state = _load_session()
    rel = state.get("trace_path")
    if not rel:
        return None
    path = WORKSPACE / str(rel)
    return path if path.exists() else None


def append_event(
    event_type: str,
    payload: dict[str, Any],
    *,
    run_id: str | None = None,
    trace_path: Path | None = None,
    ts: str | None = None,
) -> Path:
    if not _enabled():
        path = trace_path or resolve_trace_path(run_id)
        return path
    path = trace_path or init_session(run_id=run_id)
    state = _load_session()
    rid = run_id or str(state.get("run_id") or path.parent.name)
    record = {
        "run_id": rid,
        "ts": ts or _utc_now(),
        "event_type": event_type,
        "payload": payload,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    event_count = int(state.get("event_count") or 0) + 1
    buffer = list(state.get("buffer_events") or [])
    buffer.append({"event_type": event_type, "ts": record["ts"], "payload_keys": list(payload.keys())})
    if len(buffer) > 100:
        buffer = buffer[-100:]
    session_update: dict[str, Any] = {
        "run_id": rid,
        "trace_path": str(path.relative_to(WORKSPACE)).replace("\\", "/"),
        "event_count": event_count,
        "buffer_events": buffer,
    }
    if not state.get("trace_path"):
        _save_session(session_update)
    else:
        _save_session({**state, **session_update})

    threshold = _consolidate_threshold()
    if event_count >= threshold and event_count % threshold == 0:
        allowed, reason = consolidation_allowed()
        if allowed:
            _maybe_consolidate_memory(event_count, buffer, reason=reason)
        else:
            deferred = list(state.get("consolidate_deferred_counts") or [])
            if event_count not in deferred:
                deferred.append(event_count)
            _save_session(
                {
                    **state,
                    **session_update,
                    "consolidate_deferred_counts": deferred[-20:],
                    "last_consolidate_skip_reason": reason,
                }
            )

    return path


def request_milestone_consolidate(*, note: str = "") -> None:
    """One-shot flag: next threshold tick may write MEMORY.md (episodic-first)."""
    MILESTONE_FLAG.parent.mkdir(parents=True, exist_ok=True)
    MILESTONE_FLAG.write_text(
        json.dumps({"requested_at": _utc_now(), "note": note[:500]}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def approve_consolidate_eval(*, approved_by: str = "eval_gate", note: str = "") -> None:
    """Record eval-gate approval for one consolidation write."""
    EVAL_APPROVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    EVAL_APPROVE_FILE.write_text(
        json.dumps(
            {"approved": True, "approved_at": _utc_now(), "approved_by": approved_by, "note": note[:500]},
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def consolidation_allowed() -> tuple[bool, str]:
    """Episodic-first: MEMORY.md only on milestone or eval gate (or explicit legacy opt-in)."""
    if os.environ.get("TRAJECTORY_ALLOW_AUTO_CONSOLIDATE", "").strip() in {"1", "true", "TRUE"}:
        return True, "legacy_auto_consolidate"
    if os.environ.get("TRAJECTORY_MILESTONE_CONSOLIDATE", "").strip() in {"1", "true", "TRUE"}:
        return True, "env_milestone"
    if MILESTONE_FLAG.is_file():
        try:
            MILESTONE_FLAG.unlink()
        except OSError:
            pass
        return True, "milestone_flag"
    if EVAL_APPROVE_FILE.is_file():
        try:
            data = json.loads(EVAL_APPROVE_FILE.read_text(encoding="utf-8"))
            if data.get("approved"):
                try:
                    EVAL_APPROVE_FILE.unlink()
                except FileNotFoundError:
                    pass
                return True, "eval_gate_approved"
        except (json.JSONDecodeError, OSError):
            pass
    commit = WORKSPACE / "30_system" / "04_documentation" / "context" / "commit.md"
    if commit.is_file():
        text = commit.read_text(encoding="utf-8")
        if "[CONSOLIDATE_MEMORY]" in text:
            return True, "commit_marker"
    return False, "episodic_first_deferred"


def _maybe_consolidate_memory(
    event_count: int,
    buffer: list[dict[str, Any]],
    *,
    reason: str = "threshold",
) -> None:
    """Phase memory: append compact summary to .agent/MEMORY.md when consolidation_allowed."""
    memory_path = WORKSPACE / ".agent" / "MEMORY.md"
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    ts = _utc_now()
    summary = (
        f"\n[{ts[:10]}] [trajectory] Milestone consolidate at {event_count} events "
        f"({reason}); recent types: {', '.join(e['event_type'] for e in buffer[-5:])}.\n"
    )
    if memory_path.is_file():
        memory_path.write_text(memory_path.read_text(encoding="utf-8") + summary, encoding="utf-8")
    else:
        memory_path.write_text(summary, encoding="utf-8")


def sanitize_tool_name(raw: Any) -> str:
    name = str(raw or "unknown").strip()
    if len(name) > 120:
        name = name[:117] + "..."
    return name


def append_atdp_event(
    *,
    observation: str,
    hidden_status: str,
    action: str,
    outcome: str,
    reward: float | int | None = None,
    metadata: dict[str, Any] | None = None,
    run_id: str | None = None,
    trace_path: Path | None = None,
) -> Path:
    """Append ATDP-lite tuple as event_type=atdp_step. No PHI in fields."""
    from trajectory_rl.atdp import build_atdp_record

    payload = build_atdp_record(
        observation=observation,
        hidden_status=hidden_status,
        action=action,
        outcome=outcome,
        reward=reward,
        metadata=metadata,
    )
    return append_event("atdp_step", payload, run_id=run_id, trace_path=trace_path)
