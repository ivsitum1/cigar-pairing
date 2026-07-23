"""Per-session buffer for hook-written distillation skeleton traces.

Hooks see tool metadata only (no model reasoning). This module accumulates
actions across postToolUse events and flushes a skeleton trace on sessionEnd/stop.
See 30_system/docs/DISTILLATION_TRACE_PROTOCOL.md § Hybrid capture.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.workspace_scope import resolve_workspace_root

from .emit import Action, CaptureRecord, capture

SESSION_FILE_NAME = "session_buffer.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def session_path(workspace: Path | None = None) -> Path:
    root = workspace or resolve_workspace_root()
    raw = root / ".agent" / "distillation"
    raw.mkdir(parents=True, exist_ok=True)
    return raw / SESSION_FILE_NAME


def _default_state(session_id: str | None = None) -> dict[str, Any]:
    return {
        "session_id": session_id or str(uuid.uuid4()),
        "started_at": _utc_now(),
        "actions": [],
        "tool_failures": 0,
    }


def load_session(workspace: Path | None = None) -> dict[str, Any]:
    path = session_path(workspace)
    if not path.is_file():
        return _default_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            base = _default_state(str(data.get("session_id") or uuid.uuid4()))
            base.update({k: data[k] for k in base if k in data})
            if isinstance(data.get("actions"), list):
                base["actions"] = data["actions"]
            return base
    except (json.JSONDecodeError, OSError):
        pass
    return _default_state()


def save_session(state: dict[str, Any], workspace: Path | None = None) -> None:
    path = session_path(workspace)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reset_session(*, session_id: str | None = None, workspace: Path | None = None) -> dict[str, Any]:
    state = _default_state(session_id)
    save_session(state, workspace)
    return state


def append_action(
    tool: str,
    *,
    success: bool = True,
    intent: str = "",
    result_summary: str = "",
    workspace: Path | None = None,
) -> None:
    state = load_session(workspace)
    actions = list(state.get("actions") or [])
    actions.append(
        {
            "tool": tool,
            "intent": intent,
            "result_summary": result_summary,
            "success": success,
        }
    )
    failures = int(state.get("tool_failures") or 0) + (0 if success else 1)
    state["actions"] = actions[-200:]
    state["tool_failures"] = failures
    save_session(state, workspace)


def infer_task_domain(actions: list[dict[str, Any]]) -> str:
    tools = " ".join(str(a.get("tool", "")).lower() for a in actions)
    if any(k in tools for k in ("pubmed", "clinical", "books_rag", "consensus")):
        return "clinical"
    if any(k in tools for k in (".r", "r-execution", "stats", "brms", "meta")):
        return "biostatistics"
    if any(k in tools for k in ("write", "strreplace", "grep", "shell", "pytest")):
        return "python"
    if any(k in tools for k in ("manuscript", "write", "prisma", "consort")):
        return "writing"
    return "general"


def build_skeleton_record(state: dict[str, Any]) -> CaptureRecord | None:
    raw_actions = state.get("actions") or []
    if not raw_actions:
        return None
    actions = [
        Action(
            tool=str(a.get("tool", "unknown")),
            intent=str(a.get("intent", "")),
            result_summary=str(a.get("result_summary", "")),
            success=bool(a.get("success", True)),
        )
        for a in raw_actions
        if isinstance(a, dict)
    ]
    if not actions:
        return None
    failures = int(state.get("tool_failures") or 0)
    session_id = str(state.get("session_id") or "unknown")
    domain = infer_task_domain(raw_actions)
    return CaptureRecord(
        context=(
            f"Auto skeleton from Cursor session {session_id}. "
            "Enrich with task context and reasoning before promotion."
        ),
        reasoning="",
        actions=actions,
        outcome={
            "success": failures == 0,
            "verification": "hook_skeleton",
            "tool_failures": failures,
            "action_count": len(actions),
        },
        task_domain=domain,
        source_model="hook-skeleton",
        tags=["skeleton", "auto_hook"],
        skeleton=True,
        enrichment_status="pending",
    )


def flush_skeleton(*, workspace: Path | None = None) -> Path | None:
    """Capture skeleton trace from buffer and reset session. Returns log path or None."""
    state = load_session(workspace)
    record = build_skeleton_record(state)
    reset_session(workspace=workspace)
    if record is None:
        return None
    return capture(record, workspace=workspace)
