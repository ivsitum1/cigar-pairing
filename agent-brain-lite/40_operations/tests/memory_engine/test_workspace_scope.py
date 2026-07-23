"""Tests for workspace scope resolution."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

_OPS = Path(__file__).resolve().parents[2] / "python"
import sys

if str(_OPS) not in sys.path:
    sys.path.insert(0, str(_OPS))

from common.workspace_scope import (  # noqa: E402
    BRAIN_SCOPE,
    discover_federated_memory_sources,
    resolve_project_scope,
    resolve_workspace_root,
    write_project_scope_file,
)


def test_brain_workspace_scope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    brain = tmp_path / "agent-rules"
    (brain / "memory_engine").mkdir(parents=True)
    (brain / "30_system" / "SKILLS").mkdir(parents=True)
    (brain / ".agent").mkdir()
    monkeypatch.setenv("WORKSPACE_ROOT", str(brain))
    assert resolve_workspace_root() == brain.resolve()
    assert resolve_project_scope(brain) == BRAIN_SCOPE


def test_project_workspace_scope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "my-study"
    (project / ".agent").mkdir(parents=True)
    (project / "01_input").mkdir()
    (project / "agent-rules").mkdir()
    monkeypatch.setenv("WORKSPACE_ROOT", str(project))
    assert resolve_project_scope(project) == "my-study"


def test_scope_override_file(tmp_path: Path) -> None:
    project = tmp_path / "crab-trial"
    write_project_scope_file(project, brain_path="agent-rules")
    scope_file = project / ".agent" / "project_scope.json"
    data = json.loads(scope_file.read_text(encoding="utf-8"))
    data["scope"] = "theracrab"
    scope_file.write_text(json.dumps(data), encoding="utf-8")
    assert resolve_project_scope(project) == "theracrab"


def test_walk_up_from_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "psi-os"
    (project / ".agent").mkdir(parents=True)
    (project / "01_input").mkdir()
    nested = project / "02_analysis" / "data"
    nested.mkdir(parents=True)
    monkeypatch.delenv("WORKSPACE_ROOT", raising=False)
    monkeypatch.chdir(nested)
    assert resolve_workspace_root(cwd=nested) == project.resolve()


def test_discover_federated_sources_brain_only(tmp_path: Path) -> None:
    brain = tmp_path / "agent-rules"
    (brain / "memory_engine").mkdir(parents=True)
    (brain / "30_system" / "SKILLS").mkdir(parents=True)
    (brain / ".agent" / "memory").mkdir(parents=True)
    (brain / ".agent" / "memory" / "memory.db").write_bytes(b"")
    sources = discover_federated_memory_sources(brain)
    assert len(sources) == 1
    assert sources[0].label == "agent-rules"
