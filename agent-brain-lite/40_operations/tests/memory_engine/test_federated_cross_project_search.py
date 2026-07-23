"""Tests for federated cross-workspace memory search."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_OPS = Path(__file__).resolve().parents[2] / "python"
if str(_OPS) not in sys.path:
    sys.path.insert(0, str(_OPS))

from common.workspace_scope import (  # noqa: E402
    discover_federated_memory_sources,
    write_project_scope_file,
)
from memory_engine.federation import federated_cross_project_search  # noqa: E402
from memory_engine.ingest import MemoryIngestor  # noqa: E402
from memory_engine.models import MemoryEvent  # noqa: E402
from memory_engine.store import MemoryStore  # noqa: E402


def _seed_db(db_path: Path, scope: str, summary: str) -> None:
    store = MemoryStore(db_path)
    ingestor = MemoryIngestor(store, db_path.parent / "raw.jsonl")
    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id=f"s-{scope}",
            project_scope=scope,
            payload={"result": summary},
        )
    )


def test_discover_brain_and_project_sources(tmp_path: Path) -> None:
    project = tmp_path / "sedacija-ecmo"
    (project / ".agent").mkdir(parents=True)
    (project / "01_input").mkdir()
    brain = project / "agent-rules"
    (brain / "memory_engine").mkdir(parents=True)
    (brain / "30_system" / "SKILLS").mkdir(parents=True)
    (brain / ".agent" / "memory").mkdir(parents=True)
    write_project_scope_file(project, brain_path="agent-rules")

    _seed_db(brain / ".agent" / "memory" / "memory.db", "agent-rules", "brain digest sensor")
    _seed_db(project / ".agent" / "memory" / "memory.db", "sedacija-ecmo", "ECMO sedation protocol")

    sources = discover_federated_memory_sources(project)
    labels = {source.label for source in sources}
    assert "sedacija-ecmo" in labels
    assert "agent-rules" in labels
    assert len(sources) == 2


def test_federated_search_finds_other_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "my-trial"
    (project / ".agent").mkdir(parents=True)
    (project / "01_input").mkdir()
    brain = project / "agent-rules"
    (brain / "memory_engine").mkdir(parents=True)
    (brain / "30_system" / "SKILLS").mkdir(parents=True)
    (brain / ".agent" / "memory").mkdir(parents=True)
    write_project_scope_file(project, brain_path="agent-rules")

    _seed_db(brain / ".agent" / "memory" / "memory.db", "agent-rules", "machine weekly digest")
    _seed_db(project / ".agent" / "memory" / "memory.db", "my-trial", "primary outcome analysis")

    monkeypatch.setenv("WORKSPACE_ROOT", str(project))
    monkeypatch.setenv("AGENT_MEMORY_FEDERATE", "1")

    result = federated_cross_project_search(query="digest", limit=10, workspace_root=project)
    assert result["federated"] is True
    assert "agent-rules" in result["sources_queried"]
    summaries = " ".join(item["summary"] for item in result["items"])
    assert "digest" in summaries.lower()
    assert any(item["memory_workspace"] == "agent-rules" for item in result["items"])


def test_federated_roots_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    active = tmp_path / "active"
    (active / ".agent" / "memory").mkdir(parents=True)
    other = tmp_path / "other-study"
    (other / ".agent").mkdir(parents=True)
    (other / "01_input").mkdir()

    _seed_db(active / ".agent" / "memory" / "memory.db", "active", "local only")
    _seed_db(other / ".agent" / "memory" / "memory.db", "other-study", "disease phenotype mapping")

    monkeypatch.setenv("WORKSPACE_ROOT", str(active))
    monkeypatch.setenv("AGENT_MEMORY_FEDERATED_ROOTS", str(other))

    result = federated_cross_project_search(query="disease", limit=10, workspace_root=active)
    assert result["federated"] is True
    assert "other-study" in result["sources_queried"]
    assert any("disease" in item["summary"].lower() for item in result["items"])
