#!/usr/bin/env python3
"""Validate that every .py/.xml file is wikilinked from a code bridge cluster note."""

from __future__ import annotations

import argparse
import re
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
CODE_SUFFIXES = frozenset({".py", ".xml"})
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)\]\]")
CLUSTERS_DIR_REL = "30_system/docs/bridges/clusters"


def list_code_files(root: Path) -> set[str]:
    from _graph_paths import should_skip_file

    found: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_file(path, root):
            continue
        if path.suffix.lower() not in CODE_SUFFIXES:
            continue
        found.add(path.relative_to(root).as_posix())
    return found


def parse_wikilinked_code(root: Path) -> set[str]:
    linked: set[str] = set()
    clusters_dir = root / CLUSTERS_DIR_REL
    if not clusters_dir.is_dir():
        return linked
    for md in clusters_dir.glob("cluster_*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        for target in WIKI_LINK.findall(text):
            t = target.strip()
            if t.endswith(".py") or t.endswith(".xml"):
                linked.add(t.replace("\\", "/"))
    return linked


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate code bridge cluster coverage.")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    expected = list_code_files(root)
    linked = parse_wikilinked_code(root)
    missing = sorted(expected - linked)
    extra = sorted(linked - expected)

    print(f"Expected .py/.xml: {len(expected)}")
    print(f"Wikilinked from clusters: {len(linked)}")
    print(f"Missing: {len(missing)}")
    print(f"Extra/stale wikilinks: {len(extra)}")

    if missing:
        print("\nMissing (first 40):")
        for rel in missing[:40]:
            print(f"  {rel}")

    if extra:
        print("\nExtra (first 20):")
        for rel in extra[:20]:
            print(f"  {rel}")

    return 1 if missing or extra else 0


if __name__ == "__main__":
    raise SystemExit(main())
