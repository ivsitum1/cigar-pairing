#!/usr/bin/env python3
"""Copy codebook templates from brain into a study project (idempotent)."""
from __future__ import annotations

import shutil
from pathlib import Path

AGENT_RULES = Path(__file__).resolve().parent.parent.parent
CODEBOOKS_DIR = AGENT_RULES / "40_operations" / "templates" / "codebooks"

# (template filename, project-relative destination)
CODEBOOK_COPIES = (
    ("extraction_codebook.md", Path("01_input/data_extraction/codebook.md")),
    ("dataset_codebook.md", Path("01_input/codebook/dataset_codebook.md")),
)

CODEBOOK_FOLDERS = (
    "01_input/codebook",
    "01_input/data_extraction",
)


def seed_codebooks(project_root: Path, agent_rules: Path | None = None) -> list[str]:
    """
    Create codebook folders and copy templates if destinations are missing.

    Returns:
        List of project-relative paths created.
    """
    project_root = Path(project_root).resolve()
    rules = Path(agent_rules).resolve() if agent_rules else AGENT_RULES
    src_dir = rules / "40_operations" / "templates" / "codebooks"

    created: list[str] = []
    for folder in CODEBOOK_FOLDERS:
        (project_root / folder).mkdir(parents=True, exist_ok=True)

    for template_name, dest_rel in CODEBOOK_COPIES:
        src = src_dir / template_name
        dest = project_root / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            continue
        if not src.is_file():
            raise FileNotFoundError(f"Missing brain template: {src}")
        shutil.copy2(src, dest)
        created.append(dest_rel.as_posix())

    return created


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Seed codebook templates into a project")
    parser.add_argument("--root", type=str, default=".", help="Project root")
    parser.add_argument(
        "--agent-rules",
        type=str,
        default=None,
        help="Path to agent-rules (default: parent of 40_operations/scripts)",
    )
    args = parser.parse_args()
    created = seed_codebooks(Path(args.root), Path(args.agent_rules) if args.agent_rules else None)
    if created:
        for p in created:
            print(f"Created {p}")
    else:
        print("Codebooks already present; nothing copied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
