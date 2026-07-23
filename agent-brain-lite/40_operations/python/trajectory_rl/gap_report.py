"""Parse trajectory.jsonl for skill-gap events (SkillLens evolution bridge)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from brain_assist.rcml_registry import detect_relation_tag

WORKSPACE = Path(__file__).resolve().parents[3]
ARTIFACTS = WORKSPACE / "90_archive" / "artifacts"
SESSION_STATE = WORKSPACE / ".agent" / "memory" / "trajectory_session.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_trace_path(explicit: Path | None = None) -> Path | None:
    if explicit and explicit.is_file():
        return explicit
    if SESSION_STATE.is_file():
        try:
            data = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
            rel = data.get("trace_path")
            if rel:
                p = WORKSPACE / str(rel).replace("\\", "/")
                if p.is_file():
                    return p
        except json.JSONDecodeError:
            pass
    candidates = sorted(ARTIFACTS.glob("run_*/trajectory.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def parse_gap_events(trace_path: Path) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = event.get("event_type") or event.get("type") or ""
        payload = event.get("payload") or event.get("data") or {}

        if etype == "skill_gap":
            gaps.append({"event_type": etype, **payload})
            continue

        if etype == "tool_result" and payload.get("success") is False:
            gaps.append(
                {
                    "event_type": "tool_failure",
                    "tool": payload.get("selected_tool") or payload.get("tool"),
                    "error_class": payload.get("error_class"),
                    "prescreen_hint": payload.get("prescreen_hint"),
                }
            )
        elif etype == "tool_selected" and payload.get("tool_correct") is False:
            gaps.append(
                {
                    "event_type": "tool_selected_failure",
                    "tool": payload.get("selected_tool"),
                    "prescreen_hint": payload.get("prescreen_hint"),
                }
            )
    return gaps


def build_gap_report(
    *,
    trace_path: Path | None = None,
    skill_id: str | None = None,
    prompt: str | None = None,
) -> dict[str, Any]:
    path = resolve_trace_path(trace_path)
    if path is None:
        return {
            "exported_at": _utc_now(),
            "trace_path": None,
            "gaps": [],
            "error": "no_trajectory_found",
        }

    gaps = parse_gap_events(path)
    report: dict[str, Any] = {
        "exported_at": _utc_now(),
        "trace_path": str(path.relative_to(WORKSPACE)).replace("\\", "/"),
        "gap_count": len(gaps),
        "gaps": gaps,
    }
    if skill_id:
        report["skill_id"] = skill_id
    if prompt:
        report["prompt"] = prompt
        report["relation_tag"] = detect_relation_tag(prompt)
    if gaps:
        last = gaps[-1]
        report["suggested_case"] = {
            "skill_id": skill_id or "notebooklm-research-gate",
            "failure_text": json.dumps(last, ensure_ascii=False)[:2000],
            "correction_text": last.get("prescreen_hint") or "Apply skill procedure and retry with corrected args.",
        }
    return report
