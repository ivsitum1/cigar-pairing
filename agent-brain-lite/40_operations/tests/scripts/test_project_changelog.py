"""Tests for project changelog seeding and project_changelog_auto paths."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_seed_version_control_creates_changelog_files(tmp_path: Path) -> None:
    from project_init import seed_version_control

    seed_version_control(tmp_path)
    changelog = tmp_path / "05_version_control" / "changelog.md"
    readme = tmp_path / "05_version_control" / "CHANGELOG_AUTO_README.md"
    assert changelog.is_file()
    assert "Keep a Changelog" in changelog.read_text(encoding="utf-8")
    assert readme.is_file()
    assert "CHANGELOG_AUTO.jsonl" in readme.read_text(encoding="utf-8")


def test_project_changelog_auto_uses_version_control_dir(tmp_path: Path) -> None:
    import changelog_auto as ca
    import project_changelog_auto as pca

    pca.configure_project(tmp_path)
    assert ca.REPO_ROOT == tmp_path.resolve()
    assert ca.CHANGELOG_MD == tmp_path / "05_version_control" / "CHANGELOG_AUTO.md"
    assert ca.CHANGELOG_JSONL == tmp_path / "05_version_control" / "CHANGELOG_AUTO.jsonl"


def test_install_hook_when_git_present(tmp_path: Path) -> None:
    from project_init import install_project_changelog_hook

    agent_rules = Path(__file__).resolve().parents[3]
    git = tmp_path / ".git"
    git.mkdir(parents=True)
    (git / "hooks").mkdir(parents=True, exist_ok=True)

    install_project_changelog_hook(tmp_path, agent_rules)
    hook = git / "hooks" / "post-commit"
    assert hook.is_file()
    assert "project_changelog_auto.py" in hook.read_text(encoding="utf-8")
