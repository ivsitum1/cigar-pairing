"""Shared fixtures for scripts tests."""
import sys
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS = WORKSPACE / "40_operations/scripts"
CURSOR_SCRIPTS = WORKSPACE / ".cursor" / "scripts"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(CURSOR_SCRIPTS))


@pytest.fixture
def workspace():
    return WORKSPACE


@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal project structure for testing."""
    agent = tmp_path / ".agent"
    agent.mkdir()
    (agent / "task").mkdir()
    (agent / "system").mkdir()
    (agent / "SOPs").mkdir()
    (agent / "MEMORY.md").write_text("# MEMORY\n---\n", encoding="utf-8")
    (agent / "handoff_log.jsonl").write_text("", encoding="utf-8")

    identity_ctx = tmp_path / "30_system" / "context"
    identity_ctx.mkdir(parents=True)
    for name in ["user.md", "soul.md", "memory.md"]:
        (identity_ctx / name).write_text(f"# {name}\n---\n", encoding="utf-8")

    ctx = tmp_path / "30_system/04_documentation" / "context"
    ctx.mkdir(parents=True)
    (ctx / "main.md").write_text("# main\n---\n", encoding="utf-8")
    (ctx / "commit.md").write_text("# commit\n---\n", encoding="utf-8")
    (ctx / "log.md").write_text("# log\n---\n", encoding="utf-8")

    cursor_errors = tmp_path / ".cursor" / "errors"
    cursor_errors.mkdir(parents=True)

    return tmp_path
