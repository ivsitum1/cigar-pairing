"""Session buffer and auto-gate for Output Controller hook.

Tracks deliverable writes during a Cursor session (postToolUse) and runs
zero-tolerance output_controller_gate on sessionEnd/stop.

Opt-out: OUTPUT_GATE_HOOK_DISABLED=1
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.workspace_scope import resolve_workspace_root

from brain_assist.output_controller_gate import run_output_gate

SESSION_FILE = "session_queue.json"
REPORTS_DIR = "reports"
LAST_REPORT = "last_report.json"
MANUAL_QUEUE = "manual_queue.jsonl"

TEXT_EXTENSIONS = {".md", ".mdc", ".txt", ".r", ".R", ".rmd", ".Rmd", ".tex", ".json"}
WRITE_TOOLS = frozenset(
    {
        "write",
        "strreplace",
        "applypatch",
        "editnotebook",
        "writefile",
    }
)

_DELIVERABLE_MARKERS = (
    "/03_output/",
    "/manuscript/",
    "\\03_output\\",
    "\\manuscript\\",
)
_PROJECT_OUTPUT_RE = re.compile(
    r"10_projects[/\\]projects[/\\](?P<pid>[^/\\]+)[/\\]03_output[/\\]",
    re.IGNORECASE,
)
_EXCLUDE_MARKERS = (
    "/.agent/",
    "\\.agent\\",
    "/90_archive/",
    "\\90_archive\\",
    "/40_operations/tests/",
    "\\40_operations\\tests\\",
    "/node_modules/",
    "\\node_modules\\",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def gate_root(workspace: Path | None = None) -> Path:
    root = workspace or resolve_workspace_root()
    path = root / ".agent" / "output_gate"
    path.mkdir(parents=True, exist_ok=True)
    return path


def session_path(workspace: Path | None = None) -> Path:
    return gate_root(workspace) / SESSION_FILE


def _default_state(session_id: str | None = None) -> dict[str, Any]:
    return {
        "session_id": session_id or str(uuid.uuid4()),
        "started_at": _utc_now(),
        "flagged": {},
    }


def load_session(workspace: Path | None = None) -> dict[str, Any]:
    path = session_path(workspace)
    if not path.is_file():
        return _default_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            base = _default_state(str(data.get("session_id") or uuid.uuid4()))
            base.update({k: data[k] for k in ("session_id", "started_at") if k in data})
            flagged = data.get("flagged")
            if isinstance(flagged, dict):
                base["flagged"] = flagged
            return base
    except (json.JSONDecodeError, OSError):
        pass
    return _default_state()


def save_session(state: dict[str, Any], workspace: Path | None = None) -> None:
    session_path(workspace).write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def reset_session(*, session_id: str | None = None, workspace: Path | None = None) -> dict[str, Any]:
    state = _default_state(session_id)
    save_session(state, workspace)
    return state


def _norm_path(path: str, workspace: Path) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = (workspace / p).resolve()
    else:
        p = p.resolve()
    try:
        rel = p.relative_to(workspace.resolve())
        return rel.as_posix()
    except ValueError:
        return p.as_posix()


def is_deliverable_path(path: str, workspace: Path) -> bool:
    """True if path looks like a user-facing deliverable (not internal brain noise)."""
    norm = _norm_path(path, workspace).lower()
    if any(marker.lower() in norm for marker in _EXCLUDE_MARKERS):
        return False
    suffix = Path(norm).suffix.lower()
    if suffix not in {ext.lower() for ext in TEXT_EXTENSIONS}:
        return False
    if any(marker.lower() in norm for marker in _DELIVERABLE_MARKERS):
        return True
    if _PROJECT_OUTPUT_RE.search(norm):
        return True
    # Manuscript-like filenames under output-ish folders
    if any(part in norm for part in ("03_output", "manuscript", "draft")):
        name = Path(norm).name.lower()
        if any(k in name for k in ("manuscript", "draft", "results", "abstract", "report")):
            return True
    return False


def infer_project_id(path: str, workspace: Path) -> str | None:
    norm = _norm_path(path, workspace)
    m = _PROJECT_OUTPUT_RE.search(norm)
    if m:
        return m.group("pid")
    parts = Path(norm).parts
    try:
        idx = parts.index("projects")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    except ValueError:
        pass
    return None


def infer_domain(path: str) -> str:
    norm = path.lower()
    suffix = Path(norm).suffix
    if suffix in {".r", ".rmd"}:
        return "statistics"
    if "protocol" in norm or "sap" in norm or "methodolog" in norm:
        return "methodology"
    if suffix == ".py" and "40_operations" not in norm:
        return "code"
    if any(k in norm for k in ("manuscript", "abstract", "discussion", "introduction", "draft")):
        return "writing"
    if any(k in norm for k in ("analysis", "results", "statistic", "02_analysis")):
        return "statistics"
    return "writing"


def extract_path_from_tool_payload(payload: dict[str, Any]) -> str | None:
    """Best-effort path from Cursor postToolUse tool metadata."""
    for key in ("path", "file_path", "filePath", "target_file", "targetFile", "notebook_path"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    for container_key in ("arguments", "args", "input", "parameters"):
        container = payload.get(container_key)
        if isinstance(container, dict):
            for key in ("path", "file_path", "filePath", "target_file", "targetFile", "notebook_path"):
                val = container.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
        elif isinstance(container, str):
            try:
                parsed = json.loads(container)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                for key in ("path", "file_path", "filePath", "target_file"):
                    val = parsed.get(key)
                    if isinstance(val, str) and val.strip():
                        return val.strip()
    return None


def _tool_name(payload: dict[str, Any]) -> str:
    raw = (
        payload.get("toolName")
        or payload.get("tool_name")
        or payload.get("tool")
        or payload.get("name")
        or ""
    )
    return str(raw).strip().lower()


def flag_from_tool_payload(payload: dict[str, Any], workspace: Path) -> str | None:
    """If payload is a write to a deliverable path, flag it. Returns normalized path or None."""
    tool = _tool_name(payload)
    if tool and tool not in WRITE_TOOLS and not any(w in tool for w in WRITE_TOOLS):
        return None
    raw_path = extract_path_from_tool_payload(payload)
    if not raw_path:
        return None
    if not is_deliverable_path(raw_path, workspace):
        return None
    norm = _norm_path(raw_path, workspace)
    flag_deliverable(
        norm,
        domain=infer_domain(norm),
        project_id=infer_project_id(norm, workspace),
        workspace=workspace,
        source="postToolUse",
    )
    return norm


def flag_deliverable(
    path: str,
    *,
    domain: str | None = None,
    project_id: str | None = None,
    workspace: Path | None = None,
    source: str = "manual",
) -> None:
    ws = workspace or resolve_workspace_root()
    norm = _norm_path(path, ws)
    state = load_session(ws)
    flagged: dict[str, Any] = dict(state.get("flagged") or {})
    flagged[norm] = {
        "path": norm,
        "domain": domain or infer_domain(norm),
        "project_id": project_id or infer_project_id(norm, ws),
        "source": source,
        "flagged_at": _utc_now(),
    }
    state["flagged"] = flagged
    save_session(state, ws)


def ingest_manual_queue(workspace: Path | None = None) -> int:
    """Append entries from manual_queue.jsonl into session flagged set."""
    ws = workspace or resolve_workspace_root()
    queue_path = gate_root(ws) / MANUAL_QUEUE
    if not queue_path.is_file():
        return 0
    count = 0
    lines = queue_path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path.strip():
            continue
        flag_deliverable(
            path.strip(),
            domain=str(entry.get("domain") or infer_domain(path)),
            project_id=entry.get("project_id"),
            workspace=ws,
            source="manual_queue",
        )
        count += 1
    if count:
        queue_path.write_text("", encoding="utf-8")
    return count


def flush_gates(workspace: Path | None = None) -> dict[str, Any]:
    """Run output gate on all flagged deliverables; write report JSON."""
    ws = workspace or resolve_workspace_root()
    ingest_manual_queue(ws)
    state = load_session(ws)
    flagged: dict[str, Any] = dict(state.get("flagged") or {})
    session_id = str(state.get("session_id") or uuid.uuid4())

    results: list[dict[str, Any]] = []
    for norm, meta in flagged.items():
        abs_path = (ws / norm).resolve()
        if not abs_path.is_file():
            results.append(
                {
                    "path": norm,
                    "status": "skipped",
                    "reason": "file_missing",
                    "meta": meta,
                }
            )
            continue
        domain = str(meta.get("domain") or infer_domain(norm))
        project_id = meta.get("project_id")
        pid = str(project_id).strip() if project_id else None
        report = run_output_gate(path=abs_path, domain=domain, project_id=pid)
        results.append(
            {
                "path": norm,
                "status": "pass" if report.pass_all else "fail",
                "domain": domain,
                "project_id": pid,
                "gate": report.to_dict(),
                "meta": meta,
            }
        )

    summary = {
        "session_id": session_id,
        "generated_at": _utc_now(),
        "tolerance": "zero",
        "total": len(results),
        "passed": sum(1 for r in results if r.get("status") == "pass"),
        "failed": sum(1 for r in results if r.get("status") == "fail"),
        "skipped": sum(1 for r in results if r.get("status") == "skipped"),
        "results": results,
    }

    reports_dir = gate_root(ws) / REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = reports_dir / f"{session_id}_{stamp}.json"
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (gate_root(ws) / LAST_REPORT).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    reset_session(session_id=str(uuid.uuid4()), workspace=ws)
    summary["report_path"] = report_path.as_posix()
    return summary
