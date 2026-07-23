"""Resolve Cursor workspace root and project scope for memory isolation."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BRAIN_SCOPE = "agent-rules"
SCOPE_FILE = ".agent/project_scope.json"
MEMORY_DB_REL = Path(".agent") / "memory" / "memory.db"
PROJECT_MARKERS = ("01_input", "agent-rules")
DEFAULT_BRAIN_SUBDIR = "agent-rules"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or BRAIN_SCOPE


def _is_project_root(path: Path) -> bool:
    if not (path / ".agent").is_dir():
        return False
    return any((path / marker).exists() for marker in PROJECT_MARKERS)


def _is_brain_root(path: Path) -> bool:
    return (path / "memory_engine").is_dir() and (path / "30_system" / "SKILLS").is_dir()


def _walk_up_for_project(start: Path) -> Path | None:
    current = start.resolve()
    for _ in range(12):
        if _is_project_root(current):
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def resolve_workspace_root(
    *,
    env: os._Environ[str] | None = None,
    cwd: Path | None = None,
    script_path: Path | None = None,
) -> Path:
    """Return the active workspace root (project or brain).

    Priority:
    1. WORKSPACE_ROOT environment variable
    2. Walk up from cwd for project markers (.agent + 01_input or agent-rules)
    3. Brain root inferred from script_path (three parents from .cursor/hooks or memory_engine)
    4. cwd as last resort
    """
    environ = env if env is not None else os.environ
    explicit = environ.get("WORKSPACE_ROOT", "").strip()
    if explicit:
        return Path(explicit).resolve()

    if cwd is None:
        cwd = Path.cwd()
    found = _walk_up_for_project(cwd)
    if found is not None:
        return found

    if script_path is not None:
        brain_candidate = script_path.resolve().parents[2]
        if _is_brain_root(brain_candidate):
            return brain_candidate

    return cwd.resolve()


@dataclass(frozen=True)
class FederatedMemorySource:
    """One workspace whose memory.db may be queried in federated cross-project search."""

    label: str
    workspace_root: Path
    db_path: Path


def read_project_scope_file(root: Path) -> dict[str, Any] | None:
    scope_path = root / SCOPE_FILE
    if not scope_path.is_file():
        return None
    try:
        data: dict[str, Any] = json.loads(scope_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data


def read_scope_override(root: Path) -> str | None:
    data = read_project_scope_file(root)
    if not data:
        return None
    scope = data.get("scope")
    if isinstance(scope, str) and scope.strip():
        return scope.strip()
    return None


def read_brain_path(root: Path) -> str:
    data = read_project_scope_file(root)
    if data:
        brain_path = data.get("brain_path")
        if isinstance(brain_path, str) and brain_path.strip():
            return brain_path.strip()
    if (root / DEFAULT_BRAIN_SUBDIR).is_dir():
        return DEFAULT_BRAIN_SUBDIR
    return DEFAULT_BRAIN_SUBDIR


def resolve_brain_root(workspace_root: Path) -> Path | None:
    """Return embedded brain root for a clinical project, if present."""
    workspace_root = workspace_root.resolve()
    if _is_brain_root(workspace_root):
        return workspace_root
    brain_rel = read_brain_path(workspace_root)
    candidate = (workspace_root / brain_rel).resolve()
    if _is_brain_root(candidate):
        return candidate
    return None


def _memory_db_if_exists(workspace_root: Path) -> Path | None:
    db_path = (workspace_root / MEMORY_DB_REL).resolve()
    return db_path if db_path.is_file() else None


def _parse_federated_roots(env_value: str) -> list[Path]:
    roots: list[Path] = []
    for part in env_value.split(","):
        part = part.strip()
        if part:
            roots.append(Path(part).expanduser().resolve())
    return roots


def discover_federated_memory_sources(
    workspace_root: Path | None = None,
    *,
    env: os._Environ[str] | None = None,
) -> list[FederatedMemorySource]:
    """Discover memory.db files for explicit cross-workspace search.

    Order (deduped by db_path):
    1. Active workspace
    2. Embedded brain (clinical project → agent-rules subfolder)
    3. AGENT_MEMORY_FEDERATED_ROOTS (comma-separated workspace roots)
    """
    environ = env if env is not None else os.environ
    if workspace_root is None:
        workspace_root = resolve_workspace_root(env=environ)
    else:
        workspace_root = workspace_root.resolve()

    seen: set[Path] = set()
    sources: list[FederatedMemorySource] = []

    def _append(label: str, root: Path) -> None:
        db_path = _memory_db_if_exists(root)
        if db_path is None or db_path in seen:
            return
        seen.add(db_path)
        sources.append(
            FederatedMemorySource(
                label=label,
                workspace_root=root.resolve(),
                db_path=db_path,
            )
        )

    _append(resolve_project_scope(workspace_root), workspace_root)

    brain_root = resolve_brain_root(workspace_root)
    if brain_root is not None and brain_root != workspace_root:
        _append(BRAIN_SCOPE, brain_root)

    for extra_root in _parse_federated_roots(environ.get("AGENT_MEMORY_FEDERATED_ROOTS", "")):
        if not extra_root.is_dir():
            continue
        if _is_brain_root(extra_root):
            _append(BRAIN_SCOPE, extra_root)
        elif _is_project_root(extra_root):
            _append(resolve_project_scope(extra_root), extra_root)
        else:
            _append(_slugify(extra_root.name), extra_root)

    return sources


def resolve_project_scope(root: Path | None = None) -> str:
    """Return stable project_scope slug for memory store and hooks."""
    if root is None:
        root = resolve_workspace_root()
    else:
        root = root.resolve()

    override = read_scope_override(root)
    if override:
        return override

    if _is_brain_root(root) and not _is_project_root(root):
        return BRAIN_SCOPE

    return _slugify(root.name)


def write_project_scope_file(
    project_root: Path,
    *,
    brain_path: str = "agent-rules",
) -> Path:
    """Create or update .agent/project_scope.json for a clinical project."""
    agent_dir = project_root / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    scope_path = agent_dir / "project_scope.json"
    payload = {
        "scope": _slugify(project_root.name),
        "created": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "brain_path": brain_path,
    }
    scope_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return scope_path


def is_brain_workspace(root: Path | None = None) -> bool:
    if root is None:
        root = resolve_workspace_root()
    root = root.resolve()
    scope = resolve_project_scope(root)
    return scope == BRAIN_SCOPE and _is_brain_root(root)
