"""Tests for cursor_paths.resolve_cursor_script."""
from pathlib import Path

import cursor_paths


def test_resolve_prefers_legacy_then_canonical(tmp_path):
    legacy = tmp_path / ".cursor" / "40_operations" / "scripts"
    legacy.mkdir(parents=True)
    (legacy / "error_ops.py").write_text("# ok\n", encoding="utf-8")
    got = cursor_paths.resolve_cursor_script(tmp_path, "error_ops.py")
    assert got == legacy / "error_ops.py"


def test_resolve_fallback_to_dot_cursor_scripts(tmp_path):
    scripts = tmp_path / ".cursor" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "error_ops.py").write_text("# ok\n", encoding="utf-8")
    got = cursor_paths.resolve_cursor_script(tmp_path, "error_ops.py")
    assert got == scripts / "error_ops.py"


def test_resolve_missing_returns_none(tmp_path):
    assert cursor_paths.resolve_cursor_script(tmp_path, "missing.py") is None


def test_repo_workspace_resolves_error_ops(workspace: Path):
    p = cursor_paths.resolve_cursor_script(workspace, "error_ops.py")
    assert p is not None and p.name == "error_ops.py"
