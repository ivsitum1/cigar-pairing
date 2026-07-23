"""Resolve Cursor IDE project folders from repo root (portable across machines)."""
from __future__ import annotations

import re
from pathlib import Path


def repo_path_to_cursor_slug(repo_root: Path) -> str:
    """Map repo path to Cursor projects folder name (e.g. c-Users-Admin-Documents-agent-rules)."""
    resolved = str(repo_root.resolve()).replace("\\", "/").lower().rstrip("/")
    resolved = resolved.replace(":", "")
    return re.sub(r"[/\s_]+", "-", resolved.strip("/"))


def resolve_cursor_project_dir(repo_root: Path) -> Path | None:
    """Return ~/.cursor/projects/<slug> if it exists."""
    base = Path.home() / ".cursor" / "projects"
    if not base.is_dir():
        return None
    primary = base / repo_path_to_cursor_slug(repo_root)
    if primary.is_dir():
        return primary
    # Fallback: any Cursor project folder mentioning agent-rules
    matches = sorted(
        (p for p in base.iterdir() if p.is_dir() and "agent-rules" in p.name.lower()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def cursor_terminals_dir(repo_root: Path) -> Path | None:
    project = resolve_cursor_project_dir(repo_root)
    if not project:
        return None
    terminals = project / "terminals"
    return terminals if terminals.is_dir() else None


def cursor_agent_tools_dir(repo_root: Path) -> Path | None:
    project = resolve_cursor_project_dir(repo_root)
    if not project:
        return None
    tools = project / "agent-tools"
    return tools if tools.is_dir() else None
