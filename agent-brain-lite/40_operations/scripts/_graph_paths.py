"""Shared path filters for Obsidian graph / index scripts."""

from __future__ import annotations

from pathlib import Path

SKIP_PARTS = frozenset(
    {
        ".git",
        ".claude",
        "node_modules",
        "agent-transcripts",
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
    }
)

# External skill packs already merged into 30_system/SKILLS/reference — exclude from graph/index scans
SKIP_PATH_PREFIXES = (
    "90_archive/imports/",
)


def should_skip_file(path: Path, root: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return True
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return True
    return any(rel.startswith(prefix) for prefix in SKIP_PATH_PREFIXES)


def collect_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if path.is_file() and not should_skip_file(path, root):
            files.append(path)
    return files
