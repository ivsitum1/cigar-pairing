#!/usr/bin/env python3
"""Validate non-markdown bridge index coverage."""

from __future__ import annotations

import argparse
import pathlib
import re


SKIP_PARTS = {
    ".git",
    ".claude",
    "node_modules",
    "agent-transcripts",
    "__pycache__",
    ".pytest_cache",
    "venv",
}
SKIP_SUFFIXES = {".md"}

# Canonical memory logs only; machine-suffixed copies are local runtime noise.
_AGENT_MEMORY_CANONICAL = frozenset(
    {
        "raw_events.jsonl",
        "self_eval.jsonl",
        "eval_events.jsonl",
    }
)
_AGENT_MEMORY_MACHINE_SUFFIX = re.compile(
    r"^(memory|raw_events|self_eval)-.+",
    re.IGNORECASE,
)


def _should_skip_path(path: pathlib.Path) -> bool:
    parts = path.parts
    if any(part in SKIP_PARTS for part in parts):
        return True
    if any(part.startswith(".venv") for part in parts):
        return True
    if ".agent" in parts and "memory" in parts:
        name = path.name
        if name in _AGENT_MEMORY_CANONICAL:
            return False
        if _AGENT_MEMORY_MACHINE_SUFFIX.match(name):
            return True
        if name.startswith("memory-") and name.endswith(".db"):
            return True
    return False


def list_non_md_files(root: pathlib.Path) -> set[str]:
    files: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip_path(path):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        files.add(path.relative_to(root).as_posix())
    return files


def parse_indexed_files(index_path: pathlib.Path) -> set[str]:
    if not index_path.exists():
        return set()
    text = index_path.read_text(encoding="utf-8", errors="ignore")
    indexed: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("- `") or not line.endswith("`"):
            continue
        candidate = line[3:-1].strip()
        if not candidate or candidate.startswith("40_operations/scripts/") and candidate.endswith(".py"):
            # Keep script file entries too; this branch intentionally does nothing.
            pass
        indexed.add(candidate)
    return indexed


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate non-markdown bridge index coverage.")
    parser.add_argument("--root", default=".", help="Workspace root (default: current directory).")
    parser.add_argument(
        "--index",
        default="30_system/docs/bridges/non_markdown_bridges.md",
        help="Bridge index markdown path relative to root.",
    )
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    index_path = root / args.index

    expected = list_non_md_files(root)
    indexed = parse_indexed_files(index_path)
    missing = sorted(expected - indexed)
    extra = sorted(indexed - expected)

    print(f"Expected non-markdown files: {len(expected)}")
    print(f"Indexed files in bridge note: {len(indexed)}")
    print(f"Missing: {len(missing)}")
    print(f"Extra: {len(extra)}")

    if missing:
        print("\nMissing files:")
        for rel in missing[:200]:
            print(f"- {rel}")

    if extra:
        print("\nStale indexed entries:")
        for rel in extra[:200]:
            print(f"- {rel}")

    if missing or extra:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
