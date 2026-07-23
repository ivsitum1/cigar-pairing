"""Federated cross-workspace memory search (explicit MCP only)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from .store import MemoryStore

_OPS_PYTHON = Path(__file__).resolve().parent.parent / "40_operations" / "python"
if _OPS_PYTHON.is_dir() and str(_OPS_PYTHON) not in sys.path:
    sys.path.insert(0, str(_OPS_PYTHON))

from common.workspace_scope import (  # noqa: E402
    FederatedMemorySource,
    discover_federated_memory_sources,
    resolve_workspace_root,
)


def _federate_enabled() -> bool:
    return os.environ.get("AGENT_MEMORY_FEDERATE", "1").strip() in {"1", "true", "TRUE"}


def list_federated_sources(workspace_root: Path | None = None) -> list[FederatedMemorySource]:
    if workspace_root is None:
        workspace_root = resolve_workspace_root()
    return discover_federated_memory_sources(workspace_root)


def federated_cross_project_search(
    query: str,
    limit: int = 10,
    *,
    workspace_root: Path | None = None,
) -> dict:
    """Search across all discovered workspace memory.db files."""
    if workspace_root is None:
        workspace_root = resolve_workspace_root()

    sources = list_federated_sources(workspace_root)
    if not _federate_enabled() or len(sources) <= 1:
        store = MemoryStore((workspace_root / ".agent" / "memory" / "memory.db"))
        items = store.search_cross_project(query=query, limit=limit)
        for item in items:
            item["memory_workspace"] = sources[0].label if sources else "local"
            item["memory_db"] = str(sources[0].db_path) if sources else str(store.db_path)
        return {
            "query": query,
            "cross_project": True,
            "federated": False,
            "sources_queried": [sources[0].label] if sources else [],
            "count": len(items),
            "items": items,
        }

    per_source_limit = max(limit, limit * 2)
    merged: list[dict] = []
    seen_keys: set[tuple[str, str]] = set()

    for source in sources:
        store = MemoryStore(source.db_path)
        hits = store.search_cross_project(query=query, limit=per_source_limit)
        for hit in hits:
            obs_id = str(hit.get("observation_id", ""))
            dedupe_key = (source.label, obs_id)
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)
            enriched = dict(hit)
            enriched["memory_workspace"] = source.label
            enriched["memory_db"] = str(source.db_path)
            merged.append(enriched)

    merged.sort(key=lambda row: str(row.get("ts", "")), reverse=True)
    items = merged[:limit]

    return {
        "query": query,
        "cross_project": True,
        "federated": True,
        "sources_queried": [source.label for source in sources],
        "count": len(items),
        "items": items,
    }
