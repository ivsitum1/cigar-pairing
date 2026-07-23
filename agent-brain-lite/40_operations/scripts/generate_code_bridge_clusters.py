#!/usr/bin/env python3
"""Generate Obsidian markdown bridge clusters for .py and .xml (wikilink graph edges)."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
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

HUB_REL = "30_system/docs/bridges/code_graph_hub.md"
CLUSTERS_DIR_REL = "30_system/docs/bridges/clusters"


def cluster_key(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "40_operations" and parts[1] == "scripts":
        return "40_operations/scripts"
    if parts[0] == "90_archive":
        return "90_archive"
    if parts[0] == "30_system" and len(parts) >= 3:
        return "/".join(parts[:3])
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0]


def slugify(cluster: str) -> str:
    return re.sub(r"[^\w]+", "_", cluster).strip("_")


def list_code_files(root: Path) -> list[str]:
    from _graph_paths import should_skip_file

    out: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_file(path, root):
            continue
        if path.suffix.lower() not in CODE_SUFFIXES:
            continue
        out.append(path.relative_to(root).as_posix())
    return sorted(out)


def _wiki_file(rel_posix: str) -> str:
    return f"[[{rel_posix}]]"


def build_cluster_note(cluster: str, files: list[str], root: Path) -> str:
    py_n = sum(1 for f in files if f.endswith(".py"))
    xml_n = sum(1 for f in files if f.endswith(".xml"))
    slug = slugify(cluster)
    lines = [
        "---",
        f"cluster: {cluster}",
        f"files: {len(files)}",
        "---",
        "",
        f"# Code cluster: `{cluster}`",
        "",
        f"Bridge note for **{py_n}** Python and **{xml_n}** XML files (Obsidian wikilinks).",
        "",
        "## Hubs",
        "",
        "- [[code_graph_hub]]",
        "- [[non_markdown_bridges]]",
        "- [[30_system/docs/GRAPH_CONNECTIVITY_MAP]]",
        "- [[30_system/docs/AUTOMATION_INDEX]]",
        "",
    ]
    if cluster == "40_operations/scripts":
        lines.append("- [[40_operations/scripts/README]]")
    if cluster.startswith("30_system/behavior_rules/tools"):
        lines.append("- [[30_system/behavior_rules/tools/README_tools]]")

    lines.extend(["", "## Files", ""])
    for rel in files:
        lines.append(f"- {_wiki_file(rel)}")
    lines.append("")
    return "\n".join(lines)


def build_hub(clusters: dict[str, list[str]]) -> str:
    total = sum(len(v) for v in clusters.values())
    py_n = sum(1 for files in clusters.values() for f in files if f.endswith(".py"))
    xml_n = sum(1 for files in clusters.values() for f in files if f.endswith(".xml"))

    # sort: operational clusters first, archive last
    def sort_key(item: tuple[str, list[str]]) -> tuple[int, str]:
        name, _ = item
        if name == "90_archive":
            return (2, name)
        if name.startswith("40_operations") or name.startswith("30_system"):
            return (0, name)
        return (1, name)

    ordered = sorted(clusters.items(), key=sort_key)

    lines = [
        "# Code graph hub (Python and XML)",
        "",
        "Master bridge for **.py** and **.xml** files. Each cluster note wikilinks every file so Obsidian Graph can attach operational code to the knowledge graph.",
        "",
        f"- **Total files:** {total} ({py_n} Python, {xml_n} XML)",
        f"- **Clusters:** {len(clusters)}",
        "",
        "## Hubs",
        "",
        "- [[README]]",
        "- [[non_markdown_bridges]]",
        "- [[30_system/docs/GRAPH_CONNECTIVITY_MAP]]",
        "- [[30_system/docs/AUTOMATION_INDEX]]",
        "- [[Wiki semantic graph linking]]",
        "",
        "## Clusters (by folder)",
        "",
    ]
    for cluster, files in ordered:
        slug = slugify(cluster)
        lines.append(f"- [[cluster_{slug}]] — `{cluster}` ({len(files)} files)")
    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```bash",
            "py -3 40_operations/scripts/generate_code_bridge_clusters.py --root .",
            "py -3 40_operations/scripts/validate_code_bridge_clusters.py --root .",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate wikilink bridge clusters for .py/.xml.")
    ap.add_argument("--root", default=".", help="Workspace root")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    files = list_code_files(root)
    clusters: dict[str, list[str]] = defaultdict(list)
    for rel in files:
        clusters[cluster_key(rel)].append(rel)

    clusters_dir = root / CLUSTERS_DIR_REL
    clusters_dir.mkdir(parents=True, exist_ok=True)

    # Remove stale cluster_*.md from prior runs
    for old in clusters_dir.glob("cluster_*.md"):
        slug_expected = {f"cluster_{slugify(k)}" for k in clusters}
        if old.stem not in slug_expected:
            old.unlink()

    for cluster, cluster_files in clusters.items():
        slug = slugify(cluster)
        note_path = clusters_dir / f"cluster_{slug}.md"
        note_path.write_text(build_cluster_note(cluster, cluster_files, root), encoding="utf-8")

    hub_path = root / HUB_REL
    hub_path.parent.mkdir(parents=True, exist_ok=True)
    hub_path.write_text(build_hub(clusters), encoding="utf-8")

    print(f"Wrote hub: {HUB_REL}")
    print(f"Wrote {len(clusters)} cluster notes under {CLUSTERS_DIR_REL}/")
    print(f"Indexed: {len(files)} code files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
