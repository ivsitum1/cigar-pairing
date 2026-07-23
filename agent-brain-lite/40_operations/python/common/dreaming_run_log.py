"""Dreaming run log append (brain workspace only)."""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


def _enabled() -> bool:
    return os.environ.get("AGENT_DREAMING_RUN_LOG", "1").strip() in {"1", "true", "TRUE"}


def iso_week_file_label(when: date | None = None) -> str:
    when = when or date.today()
    iso = when.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def run_logs_dir(workspace_root: Path) -> Path:
    return workspace_root / ".agent" / "dreaming" / "run_logs"


def append_dream_event(
    workspace_root: Path,
    *,
    tool: str,
    outcome: str,
    ts: str | None = None,
) -> Path | None:
    """Append one JSONL event. Returns path written or None if disabled."""
    if not _enabled():
        return None
    log_dir = run_logs_dir(workspace_root)
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{iso_week_file_label()}.jsonl"
    record: dict[str, Any] = {
        "tool": tool,
        "outcome": outcome,
        "ts": ts or datetime.now(timezone.utc).isoformat(),
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def summarize_trajectory_trace(trace_path: Path, workspace_root: Path) -> Path | None:
    """Read trajectory.jsonl and append session-end summary event."""
    if not trace_path.is_file():
        return append_dream_event(
            workspace_root,
            tool="session",
            outcome="session_end no_trace",
        )
    ok = 0
    fail = 0
    last_tool = "unknown"
    for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        et = rec.get("event_type", "")
        payload = rec.get("payload") or {}
        if et == "tool_selected":
            last_tool = str(payload.get("selected_tool") or "unknown")
        if et == "tool_result":
            if payload.get("success"):
                ok += 1
            else:
                fail += 1
    return append_dream_event(
        workspace_root,
        tool="session_summary",
        outcome=f"session_end tools_ok={ok} tools_fail={fail} last_tool={last_tool}",
    )
