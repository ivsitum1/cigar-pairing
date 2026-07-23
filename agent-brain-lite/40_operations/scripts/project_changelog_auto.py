#!/usr/bin/env python3
"""Auto changelog for study projects (05_version_control/), not the brain repo.

Delegates to changelog_auto.py with project-scoped paths.

Usage:
  python agent-rules/40_operations/scripts/project_changelog_auto.py --root /path/to/my-study
  python agent-rules/40_operations/scripts/project_changelog_auto.py --root . --backfill
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import changelog_auto as ca  # noqa: E402

PROJECT_CHANGELOG_HEADER = """# Auto Changelog (Git commits)

Updated automatically on each commit at the project root. For reconstruction use this file and `05_version_control/CHANGELOG_AUTO.jsonl`.

---

"""


def configure_project(root: Path) -> Path:
    root = root.resolve()
    vc = root / "05_version_control"
    ca.REPO_ROOT = root
    ca.CHANGELOG_MD = vc / "CHANGELOG_AUTO.md"
    ca.CHANGELOG_JSONL = vc / "CHANGELOG_AUTO.jsonl"
    ca.CHANGELOG_MD_HEADER = PROJECT_CHANGELOG_HEADER
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description="Project-scoped auto changelog")
    parser.add_argument("--root", type=str, default=".", help="Project git root")
    args, remainder = parser.parse_known_args()
    configure_project(Path(args.root))
    sys.argv = [sys.argv[0], *remainder]
    return ca.main()


if __name__ == "__main__":
    sys.exit(main())
