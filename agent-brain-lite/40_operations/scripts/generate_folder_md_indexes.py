#!/usr/bin/env python3
"""Generate distributed markdown indexes by top-level folder."""

from __future__ import annotations

import argparse
import os
import pathlib
from collections import defaultdict


def rel_link(target: pathlib.Path, from_file: pathlib.Path) -> str:
    """POSIX relative path from ``from_file`` to ``target`` (both absolute).

    Computed from the *directory* containing ``from_file`` so the emitted
    markdown link resolves correctly regardless of how deeply the index is
    nested. Previously links were hand-prefixed with a fixed number of ``../``
    segments, which was off by one for files under ``30_system/docs/indexes/``
    and broke thousands of graph links.
    """
    return os.path.relpath(target, from_file.parent).replace(os.sep, "/")


SKIP_PARTS = {".git", ".claude", "agent-transcripts"}
SKIP_TOPLEVEL = {"90_archive/ARCHIVE"}
# Hand-curated hubs — never overwrite with auto folder listing
PROTECTED_INDEX_NAMES = frozenset(
    {
        "SKILLS_INDEX.md",
        "ALL_NOTES_INDEX.md",
    }
)
# Root compatibility bridge only — real skills live under 30_system/SKILLS/
SKIP_TOPLEVEL_FOLDER_INDEX = frozenset({"SKILLS"})


def collect_md(root: pathlib.Path) -> list[pathlib.Path]:
    from _graph_paths import collect_markdown_files

    files = collect_markdown_files(root)
    return [
        p
        for p in files
        if not (
            (rel := p.relative_to(root)).parts
            and rel.parts[0] in SKIP_TOPLEVEL
        )
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate distributed markdown indexes.")
    parser.add_argument("--root", default=".", help="Workspace root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    indexes_dir = root / "30_system/docs" / "indexes"
    indexes_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[str]] = defaultdict(list)
    for p in sorted(collect_md(root)):
        rel = p.relative_to(root).as_posix()
        top = rel.split("/", 1)[0] if "/" in rel else "_root"
        grouped[top].append(rel)

    index_files: list[str] = []
    for top, items in sorted(grouped.items()):
        if top in SKIP_TOPLEVEL_FOLDER_INDEX:
            continue
        safe_top = top.replace(".", "_")
        filename = f"{safe_top}_INDEX.md"
        out = indexes_dir / filename
        if filename in PROTECTED_INDEX_NAMES and out.exists():
            continue
        lines = [
            f"# {top} Markdown Index",
            "",
            f"Cluster index for `{top}` markdown notes.",
            "",
            "## Related Hubs",
            "",
            "- [Folder index hub](../FOLDER_INDEX.md)",
            "- [Graph connectivity map](../GRAPH_CONNECTIVITY_MAP.md)",
            "",
            "## Notes",
            "",
        ]
        for rel in items:
            lines.append(f"- [{rel}]({rel_link(root / rel, out)})")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        index_files.append(out.relative_to(root).as_posix())

    # Prune stale orphan indexes for top-levels that no longer exist (or became
    # gitignored / archived). Without this, deleted folders leave behind index
    # files full of dangling links. Hand-curated hubs are never pruned.
    generated_names = {pathlib.Path(p).name for p in index_files}
    pruned = 0
    for existing in indexes_dir.glob("*_INDEX.md"):
        if existing.name in generated_names or existing.name in PROTECTED_INDEX_NAMES:
            continue
        existing.unlink()
        pruned += 1

    hub_path = root / "30_system/docs" / "FOLDER_INDEX.md"
    hub_lines = [
        "# Folder Index Hub",
        "",
        "Distributed markdown routing hub to avoid over-centralization in a single all-notes page.",
        "",
        "## Related Hubs",
        "",
        f"- [README]({rel_link(root / 'index.md', hub_path)})",
        "- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)",
        "",
        "## Folder Indexes",
        "",
    ]
    # Only advertise a docs index when one actually exists on disk.
    docs_index = root / "30_system/docs" / "index.md"
    if docs_index.exists():
        hub_lines.insert(7, f"- [Docs index]({rel_link(docs_index, hub_path)})")
    for rel in index_files:
        hub_lines.append(f"- [{rel}]({rel_link(root / rel, hub_path)})")
    hub_path.write_text("\n".join(hub_lines) + "\n", encoding="utf-8")

    print(f"Generated folder hub with {len(index_files)} indexes (pruned {pruned} stale)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
