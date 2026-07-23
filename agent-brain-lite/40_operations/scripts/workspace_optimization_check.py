#!/usr/bin/env python3
"""Workspace optimization scoring check (0-100)."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from typing import Tuple

_SCRIPTS = pathlib.Path(__file__).resolve().parent


SKIP_PARTS = {".git", ".claude", "node_modules", "agent-transcripts"}


def run(cmd: list[str], cwd: pathlib.Path) -> Tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def markdown_orphan_score(root: pathlib.Path) -> Tuple[int, str]:
    rc, out = run(
        ["python", "40_operations/scripts/obsidian_connectivity_check.py", "--root", str(root)],
        root,
    )
    if rc != 0:
        return 0, "markdown connectivity check failed"
    m = re.search(r"Orphan:\s+(\d+)", out)
    orphan = int(m.group(1)) if m else 999
    if orphan == 0:
        return 20, "markdown orphans = 0"
    return 0, f"markdown orphans = {orphan}"


def non_md_score(root: pathlib.Path) -> Tuple[int, str]:
    rc, out = run(
        ["python", "40_operations/scripts/validate_non_md_index.py", "--root", str(root)],
        root,
    )
    if rc == 0:
        return 20, "non-markdown index coverage pass"
    return 0, "non-markdown index coverage fail"


def pdf_trace_score(root: pathlib.Path) -> Tuple[int, str]:
    path = root / "30_system/docs" / "bridges" / "pdf_md_map.md"
    if not path.exists():
        return 0, "pdf map missing"
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"Unpaired \(missing md\):\s+(\d+)", text)
    missing = int(m.group(1)) if m else 999
    if missing == 0:
        return 20, "pdf->md trace missing = 0"
    return 0, f"pdf->md missing = {missing}"


def hostname_conflict_score(root: pathlib.Path) -> Tuple[int, str]:
    if str(_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS))
    from hostname_conflict_files import is_hostname_conflict_path

    active = []
    for p in root.rglob("*"):
        if not is_hostname_conflict_path(p):
            continue
        rel = p.relative_to(root).as_posix()
        if rel.startswith("90_archive/"):
            continue
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        active.append(rel)
    if not active:
        return 20, "no active hostname-conflict duplicates"
    return 0, f"active hostname-conflict duplicates = {len(active)}"


def archived_rules_not_mdc_score(root: pathlib.Path) -> Tuple[int, str]:
    archived_mdc = list((root / "90_archive").rglob(".cursor/rules/*.mdc"))
    if not archived_mdc:
        return 5, "no archived .cursor/rules/*.mdc under 90_archive"
    return 0, f"archived active .mdc rules = {len(archived_mdc)}"


def hub_score(root: pathlib.Path) -> Tuple[int, str]:
    required = [
        "30_system/docs/FOLDER_INDEX.md",
        "30_system/docs/bridges/non_markdown_bridges.md",
        "30_system/docs/bridges/pdf_md_map.md",
        "30_system/docs/GRAPH_CONNECTIVITY_MAP.md",
        "30_system/docs/AUTOMATION_INDEX.md",
    ]
    missing = [p for p in required if not (root / p).exists()]
    if missing:
        return 0, f"missing hubs: {', '.join(missing)}"
    return 10, "all required hubs present"


def workflow_score(root: pathlib.Path) -> Tuple[int, str]:
    path = root / "40_operations/scripts" / "run_all_checks.sh"
    if not path.exists():
        return 0, "run_all_checks.sh missing"
    text = path.read_text(encoding="utf-8", errors="ignore")
    required = ["validate_non_md_index.py", "validate_rules_links.py"]
    missing = [r for r in required if r not in text]
    if missing:
        return 0, "quality gate missing non-md validation"
    return 10, "quality gate includes non-md validation"


def index_health_score(root: pathlib.Path) -> Tuple[int, str]:
    idx_dir = root / "30_system/docs" / "indexes"
    if not idx_dir.exists():
        return 0, "30_system/docs/indexes missing"
    count = len(list(idx_dir.glob("*_INDEX.md")))
    if count >= 10:
        return 5, f"distributed indexes healthy ({count})"
    return 0, f"distributed indexes low ({count})"


def main() -> int:
    parser = argparse.ArgumentParser(description="Workspace optimization checker.")
    parser.add_argument("--root", default=".", help="Workspace root.")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()

    checks = [
        ("markdown_connectivity", markdown_orphan_score),
        ("non_markdown_coverage", non_md_score),
        ("pdf_traceability", pdf_trace_score),
        ("hostname_conflict_cleanup", hostname_conflict_score),
        ("archived_rules_not_mdc", archived_rules_not_mdc_score),
        ("required_hubs", hub_score),
        ("workflow_quality_gate", workflow_score),
        ("distributed_index_health", index_health_score),
    ]

    max_score = 110

    total = 0
    lines = []
    for name, fn in checks:
        points, note = fn(root)
        total += points
        lines.append(f"- {name}: {points} pts ({note})")

    print(f"WORKSPACE_OPTIMIZATION_SCORE={total}/{max_score}")
    print("DETAILS:")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
