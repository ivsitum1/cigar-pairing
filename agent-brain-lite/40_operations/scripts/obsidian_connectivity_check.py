#!/usr/bin/env python3
"""Workspace connectivity check for Obsidian graph maintenance."""

from __future__ import annotations

import argparse
import pathlib
import re
from collections import defaultdict


MD_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WIKI_LINK_PATTERN = re.compile(r"\[\[([^\]|#]+)")


def _wiki_target_score(rel_posix: str) -> int:
    """Prefer canonical skill/wiki paths over archive staging duplicates."""
    if rel_posix.startswith("30_system/SKILLS/"):
        return 100
    if rel_posix.startswith("20_knowledge/wiki/"):
        return 80
    if rel_posix.startswith("30_system/"):
        return 70
    if rel_posix.startswith("40_operations/"):
        return 50
    if rel_posix.startswith(".agent/"):
        return 40
    if rel_posix.startswith("90_archive/"):
        return -100
    return 0


def resolve_wiki_target(
    wiki_target: str,
    stem_index: dict[str, list[pathlib.Path]],
    root: pathlib.Path,
) -> str | None:
    """Resolve [[wikilink]] to best matching file when stems collide."""
    key = pathlib.Path(wiki_target.strip()).stem.lower()
    candidates = stem_index.get(key, [])
    if not candidates:
        return None
    best = max(
        candidates,
        key=lambda p: (
            _wiki_target_score(p.relative_to(root).as_posix()),
            -len(p.relative_to(root).as_posix()),
        ),
    )
    return best.relative_to(root).as_posix()


def collect_markdown_files(root: pathlib.Path) -> list[pathlib.Path]:
    from _graph_paths import collect_markdown_files as _collect

    return _collect(root)


def build_graph(root: pathlib.Path, md_files: list[pathlib.Path]) -> tuple[dict[str, int], dict[str, int]]:
    rel_index = {path.relative_to(root).as_posix(): path for path in md_files}
    stem_index: dict[str, list[pathlib.Path]] = defaultdict(list)
    for path in md_files:
        stem_index[path.stem.lower()].append(path)

    inbound = {rel: 0 for rel in rel_index}
    outbound = {rel: 0 for rel in rel_index}

    for source in md_files:
        source_rel = source.relative_to(root).as_posix()
        text = source.read_text(encoding="utf-8", errors="ignore")

        for raw_target in MD_LINK_PATTERN.findall(text):
            target = raw_target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            resolved = (source.parent / target).resolve()
            try:
                resolved_rel = resolved.relative_to(root).as_posix()
            except ValueError:
                continue
            if resolved_rel in inbound:
                inbound[resolved_rel] += 1
                outbound[source_rel] += 1

        for wiki_target in WIKI_LINK_PATTERN.findall(text):
            resolved_rel = resolve_wiki_target(wiki_target, stem_index, root)
            if resolved_rel is None or resolved_rel not in inbound:
                continue
            inbound[resolved_rel] += 1
            outbound[source_rel] += 1

    return inbound, outbound


def main() -> int:
    parser = argparse.ArgumentParser(description="Check markdown graph connectivity for Obsidian.")
    parser.add_argument(
        "--root",
        default=".",
        help="Workspace root path (default: current directory).",
    )
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    md_files = collect_markdown_files(root)
    inbound, outbound = build_graph(root, md_files)

    total = len(md_files)
    orphan = [rel for rel in inbound if inbound[rel] == 0 and outbound[rel] == 0]
    weak = [rel for rel in inbound if inbound[rel] + outbound[rel] <= 1]
    connected = [rel for rel in inbound if inbound[rel] >= 1 and outbound[rel] >= 1]

    print(f"Markdown files: {total}")
    print(f"Connected: {len(connected)}")
    print(f"Weak: {len(weak)}")
    print(f"Orphan: {len(orphan)}")

    if orphan:
        print("\nTop orphan nodes:")
        for rel in sorted(orphan)[:30]:
            print(f"- {rel}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
