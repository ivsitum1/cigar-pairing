#!/usr/bin/env python3
"""Initialize a project with agent-brain-lite. Run from brain repo."""
import argparse
import os
import shutil
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent
BRAIN_FOLDER_NAME = "agent-brain-lite"

PROJECT_FOLDERS = [
    "01_work/inbox",
    "01_work/output",
    "01_work/correspondence",
    "01_work/scripts",
    ".agent/task",
]

README_MD = """# Projekt s Agent Brain Lite

Radni materijal: `01_work/`. Mozak: `agent-brain-lite/`.

- [Wiki indeks](agent-brain-lite/index.md)
"""

MEMORY_TEMPLATE = """# Project Memory

## Project name

(unesi)

## Milestones

-

## Notes

-
"""


def ignore_brain_copy(dirname: str, names: list[str]) -> list[str]:
    skip_dirs = {".git", "__pycache__", "_demo_project", "30_system", "40_operations", "memory_engine"}
    skip_files = {".env"}
    ignored: list[str] = []
    for name in names:
        full = os.path.join(dirname, name)
        if name in skip_files:
            ignored.append(name)
        elif name in skip_dirs and os.path.isdir(full):
            ignored.append(name)
    return ignored


def assert_safe_project_root(project_root: Path, brain_root: Path) -> None:
    project_resolved = project_root.resolve()
    brain_resolved = brain_root.resolve()
    if project_resolved == brain_resolved:
        raise SystemExit("Error: project root cannot be the brain repo itself.")
    try:
        project_resolved.relative_to(brain_resolved)
        raise SystemExit(
            "Error: project root must be OUTSIDE the brain repo "
            f"(got {project_resolved} inside {brain_resolved})."
        )
    except ValueError:
        pass


def copy_brain(dest: Path) -> None:
    if dest.exists():
        print(f"Exists: {dest} (skipping brain copy)")
        return
    shutil.copytree(BRAIN_ROOT, dest, ignore=ignore_brain_copy)
    print(f"Copied brain -> {dest}")


def link_or_copy_cursor(brain_cursor: Path, project_cursor: Path, no_symlink: bool) -> bool:
    if project_cursor.exists():
        print(f"Exists: {project_cursor} (skipping .cursor)")
        return True
    if no_symlink:
        shutil.copytree(brain_cursor, project_cursor)
        print(f"Copied .cursor -> {project_cursor}")
        return True
    try:
        os.symlink(brain_cursor, project_cursor, target_is_directory=True)
        print(f"Symlinked .cursor -> {brain_cursor}")
        return True
    except OSError as exc:
        print(f"Symlink failed ({exc}). Retrying with copy...")
        shutil.copytree(brain_cursor, project_cursor)
        print(f"Copied .cursor -> {project_cursor}")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Colonize agent-brain-lite into a project")
    parser.add_argument("--root", required=True, help="Project root directory")
    parser.add_argument(
        "--no-symlink",
        action="store_true",
        help="Copy .cursor instead of symlink (Windows fallback)",
    )
    parser.add_argument(
        "--skip-brain-copy",
        action="store_true",
        help="Only create project folders and link .cursor (brain already present)",
    )
    args = parser.parse_args()

    project_root = Path(args.root).resolve()
    assert_safe_project_root(project_root, BRAIN_ROOT)
    project_root.mkdir(parents=True, exist_ok=True)
    brain_dest = project_root / BRAIN_FOLDER_NAME

    print(f"Project root: {project_root}")
    print(f"Brain source: {BRAIN_ROOT}")

    if not args.skip_brain_copy:
        copy_brain(brain_dest)
    elif not brain_dest.is_dir():
        print("Error: --skip-brain-copy but agent-brain-lite not found in project")
        return 1

    for rel in PROJECT_FOLDERS:
        folder = project_root / rel
        folder.mkdir(parents=True, exist_ok=True)
        print(f"Ensured {rel}/")

    memory = project_root / ".agent" / "MEMORY.md"
    if not memory.exists():
        memory.parent.mkdir(parents=True, exist_ok=True)
        memory.write_text(MEMORY_TEMPLATE, encoding="utf-8")
        print("Created .agent/MEMORY.md")

    readme = project_root / "README.md"
    if not readme.exists():
        readme.write_text(README_MD, encoding="utf-8")
        print("Created README.md")

    brain_cursor = brain_dest / ".cursor"
    if not brain_cursor.is_dir():
        print("Error: brain .cursor not found")
        return 1

    if not link_or_copy_cursor(brain_cursor, project_root / ".cursor", args.no_symlink):
        return 1

    env_example = brain_dest / ".env.example"
    project_env = project_root / ".env"
    if env_example.is_file() and not project_env.exists():
        shutil.copy2(env_example, project_env)
        print("Created .env from .env.example")

    link_script = brain_dest / "scripts" / "link_parent.py"
    if link_script.is_file():
        import subprocess

        result = subprocess.run(
            [sys.executable, str(link_script)],
            cwd=str(brain_dest),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print("Warning: link_parent.py failed — run manually in agent-brain-lite:")
            print(f"  python scripts/link_parent.py")
            if result.stderr:
                print(result.stderr.strip())

    print("\nDone. Open the PROJECT ROOT in Cursor (not only agent-brain-lite).")
    print(f"  {project_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
