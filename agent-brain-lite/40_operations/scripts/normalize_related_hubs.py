#!/usr/bin/env python3
"""Normalize ## Related Hubs sections for consistent Obsidian graph hygiene.

Preserves context-specific bullets (any line not matching standard hub titles).
Rewrites standard links with correct relative paths from each file.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

SKIP_PARTS = frozenset({".git", ".claude", "node_modules", "agent-transcripts"})

STANDARD_TITLES = frozenset(
    {
        "Folder index hub",
        "All notes index",
        "Graph connectivity map",
    }
)

HUB_FILES: list[tuple[str, Path]] = [
    ("Folder index hub", Path("30_system/docs/FOLDER_INDEX.md")),
    ("All notes index", Path("30_system/docs/ALL_NOTES_INDEX.md")),
    ("Graph connectivity map", Path("30_system/docs/GRAPH_CONNECTIVITY_MAP.md")),
]

SECTION_START = re.compile(r"^## Related Hubs\s*$", re.M)
BULLET = re.compile(r"^-\s*\[([^\]]+)\]\(([^)]+)\)\s*$", re.M)


def find_section_span(text: str) -> tuple[int, int] | None:
    m = SECTION_START.search(text)
    if not m:
        return None
    start = m.start()
    rest = text[m.end() :]
    next_heading = re.search(r"^## [^\n]+\s*$", rest, re.M)
    if next_heading:
        end = m.end() + next_heading.start()
    else:
        end = len(text)
    return (start, end)


def extract_custom_bullets(section: str) -> list[str]:
    customs: list[str] = []
    seen: set[str] = set()
    for m in BULLET.finditer(section):
        title = m.group(1).strip()
        if title in STANDARD_TITLES:
            continue
        line = m.group(0).strip()
        if line not in seen:
            seen.add(line)
            customs.append(line)
    return customs


def build_standard_lines(from_file: Path, root: Path) -> list[str]:
    lines: list[str] = []
    for title, rel_target in HUB_FILES:
        target = (root / rel_target).resolve()
        if title == "Graph connectivity map" and target == from_file.resolve():
            continue
        rel = os.path.relpath(target, from_file.parent).replace("\\", "/")
        lines.append(f"- [{title}]({rel})")
    return lines


def normalize_file(path: Path, root: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8", errors="strict")
    span = find_section_span(text)
    if span is None:
        return False
    start, end = span
    section = text[start:end]
    customs = extract_custom_bullets(section)
    standard = build_standard_lines(path, root)
    body_lines = customs + standard if customs else standard
    new_section = "## Related Hubs\n\n" + "\n".join(body_lines) + "\n"
    new_text = text[:start] + new_section + text[end:]
    if new_text == text:
        return False
    if not dry_run:
        path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def collect_md_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*.md"):
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize Related Hubs sections.")
    ap.add_argument("--root", default=".", help="Workspace root")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    changed = 0
    for p in collect_md_files(root):
        if SECTION_START.search(p.read_text(encoding="utf-8", errors="ignore")):
            try:
                if normalize_file(p, root, args.dry_run):
                    changed += 1
            except OSError:
                continue
    print(f"updated_files: {changed}" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
