"""Integration: project_init scope + memory isolation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_OPS = _REPO / "40_operations" / "python"
if str(_OPS) not in sys.path:
    sys.path.insert(0, str(_OPS))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from common.workspace_scope import resolve_project_scope, write_project_scope_file  # noqa: E402
from memory_engine.ingest import MemoryIngestor  # noqa: E402
from memory_engine.injection import ContextInjector  # noqa: E402
from memory_engine.models import MemoryEvent  # noqa: E402
from memory_engine.retrieval import MemoryRetriever  # noqa: E402
from memory_engine.store import MemoryStore  # noqa: E402


def test_project_init_scope_file_and_memory_isolation(tmp_path: Path) -> None:
    project = tmp_path / "crab-study"
    (project / ".agent").mkdir(parents=True)
    (project / "01_input").mkdir()
    (project / "agent-rules").mkdir()

    scope_path = write_project_scope_file(project, brain_path="agent-rules")
    data = json.loads(scope_path.read_text(encoding="utf-8"))
    assert data["scope"] == "crab-study"
    assert resolve_project_scope(project) == "crab-study"

    store = MemoryStore(project / ".agent" / "memory" / "memory.db")
    ingestor = MemoryIngestor(store, project / ".agent" / "memory" / "raw.jsonl")
    retriever = MemoryRetriever(store)
    injector = ContextInjector(retriever, project / ".agent" / "memory" / "ctx.md", max_chars=4000)

    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id="s1",
            project_scope="crab-study",
            payload={"result": "CRAB primary model converged"},
        )
    )
    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id="s2",
            project_scope="other-study",
            payload={"result": "unrelated meta-analysis"},
        )
    )

    ctx = injector.build_context(project_scope="crab-study", query="CRAB")
    assert "CRAB primary" in ctx
    assert "unrelated meta-analysis" not in ctx
