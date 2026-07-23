from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


DIR_MAP: list[tuple[str, str]] = [
    ("00_inbox/raw", "00_inbox/00_inbox/raw"),
    ("10_projects/projects", "10_projects/10_projects/projects"),
    ("20_knowledge/wiki", "20_knowledge/20_knowledge/wiki"),
    ("20_knowledge/reference_library", "20_knowledge/20_knowledge/reference_library"),
    ("30_system/04_documentation", "30_system/30_system/04_documentation"),
    ("30_system/behavior_rules", "30_system/30_system/behavior_rules"),
    ("30_system/SKILLS", "30_system/30_system/SKILLS"),
    ("30_system/context", "30_system/context"),
    ("30_system/shared-brand", "30_system/30_system/shared-brand"),
    ("30_system/docs", "30_system/30_system/docs"),
    ("40_operations/R", "40_operations/40_operations/R"),
    ("40_operations/tests", "40_operations/40_operations/tests"),
    ("40_operations/scripts", "40_operations/scripts"),
    ("40_operations/logs", "40_operations/40_operations/logs"),
    ("90_archive/artifacts", "90_archive/90_archive/artifacts"),
    ("90_archive/ARCHIVE", "90_archive/90_archive/ARCHIVE"),
]

FILE_MAP: list[tuple[str, str]] = [
    ("index.md", "index.md"),
    ("30_system/UBIQUITOUS_LANGUAGE.md", "30_system/30_system/UBIQUITOUS_LANGUAGE.md"),
    ("30_system/WORKSPACE_RECONSTRUCTION_GUIDE.md", "30_system/30_system/WORKSPACE_RECONSTRUCTION_GUIDE.md"),
    ("30_system/claude.md", "30_system/30_system/claude.md"),
]

TEXT_EXTENSIONS = {
    ".md",
    ".mdc",
    ".py",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".txt",
    ".ini",
    ".sh",
    ".ps1",
}

SKIP_PREFIXES = (
    ".git",
    ".claude/worktrees",
    ".cursor/plans",
    "node_modules",
)


def should_skip(path: Path) -> bool:
    as_posix = path.relative_to(ROOT).as_posix()
    return any(as_posix.startswith(prefix) for prefix in SKIP_PREFIXES)


def move_path(src_rel: str, dst_rel: str) -> None:
    src = ROOT / src_rel
    dst = ROOT / dst_rel
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        raise RuntimeError(f"Target already exists: {dst}")
    shutil.move(str(src), str(dst))


def build_replacements() -> list[tuple[re.Pattern[str], str]]:
    replacements: list[tuple[re.Pattern[str], str]] = []
    for old_rel, new_rel in DIR_MAP + FILE_MAP:
        old = old_rel.replace("\\", "/")
        new = new_rel.replace("\\", "/")
        pattern = re.compile(rf"(?<![A-Za-z0-9_.-]){re.escape(old)}(?=[/\\)|\\s\"'])")
        replacements.append((pattern, new))
    return replacements


def rewrite_text_refs() -> int:
    replacements = build_replacements()
    updated_files = 0
    for path in ROOT.rglob("*"):
        if path.is_dir():
            continue
        if should_skip(path):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        for pattern, target in replacements:
            text = pattern.sub(target, text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated_files += 1
    return updated_files


def write_bridge_readme(old_rel: str, new_rel: str) -> None:
    bridge = ROOT / old_rel / "index.md"
    bridge.parent.mkdir(parents=True, exist_ok=True)
    bridge.write_text(
        "# Compatibility Bridge\n\n"
        f"Canonical content moved to `{new_rel}`.\n"
        "Use the canonical path for all new references.\n",
        encoding="utf-8",
    )


def create_root_index() -> None:
    root_index = ROOT / "index.md"
    if root_index.exists():
        return
    root_index.write_text(
        "# Workspace Index\n\n"
        "Obsidian-centric root for this repository.\n\n"
        "## Main Areas\n\n"
        "- [Inbox](00_inbox/00_inbox/raw)\n"
        "- [Projects](10_projects/10_projects/projects)\n"
        "- [Knowledge](20_knowledge/20_knowledge/wiki)\n"
        "- [System](30_system/30_system/docs)\n"
        "- [Operations](40_operations/scripts)\n"
        "- [Archive](90_archive/90_archive/ARCHIVE)\n",
        encoding="utf-8",
    )


def main() -> None:
    # Move all directories except scripts first so this script remains callable.
    pre_moves = [m for m in DIR_MAP if m[0] != "40_operations/scripts"]
    for src, dst in pre_moves:
        move_path(src, dst)
    for src, dst in FILE_MAP:
        move_path(src, dst)

    updated = rewrite_text_refs()
    create_root_index()

    # Create compatibility bridge directories for old entry points.
    for src, dst in DIR_MAP:
        write_bridge_readme(src, dst)

    # Move scripts last, after all work completes.
    move_path("40_operations/scripts", "40_operations/scripts")
    write_bridge_readme("40_operations/scripts", "40_operations/scripts")

    print(f"Rewrite complete. Updated text files: {updated}")


if __name__ == "__main__":
    main()
