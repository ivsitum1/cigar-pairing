"""Handoff log uses WORKSPACE_ROOT, not brain default."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def test_handoff_log_path_follows_workspace_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "my-study"
    (project / ".agent").mkdir(parents=True)
    (project / "01_input").mkdir()
    monkeypatch.setenv("WORKSPACE_ROOT", str(project))

    # Import after env set; reload workspace resolution via handoff helper
    sys.path.insert(0, str(_REPO / "40_operations" / "python"))
    from common.workspace_scope import resolve_workspace_root

    root = resolve_workspace_root()
    log_path = root / ".agent" / "handoff_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text('{"test": true}\n', encoding="utf-8")

    assert root == project.resolve()
    assert log_path.is_file()
    assert json.loads(log_path.read_text(encoding="utf-8").strip())["test"] is True
