#!/usr/bin/env python3
"""Export wiki graph and merge with Graphify structural graph."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STRUCTURAL = REPO_ROOT / "graphify-out" / "graph.json"
WIKI_GRAPH = REPO_ROOT / "wiki-export" / "graph.json"
MERGED = REPO_ROOT / "graphify-out" / "merged.json"


def _wiki_node_id(page_id: str) -> str:
    safe = page_id.replace("/", "_").replace("-", "_").replace(" ", "_").lower()
    return f"wiki_{safe}"


def _to_graphify_wiki_node(node: dict) -> dict:
    page_id = node["id"]
    return {
        "id": _wiki_node_id(page_id),
        "label": node.get("label") or page_id.split("/")[-1],
        "file_type": "wiki",
        "source_file": f"20_knowledge/wiki/{page_id}.md",
        "source_location": "L1",
        "wiki_category": node.get("category", ""),
        "graph_source": "wiki",
    }


def merge_graphs(structural_path: Path, wiki_path: Path, out_path: Path) -> dict:
    structural = json.loads(structural_path.read_text(encoding="utf-8"))
    wiki = json.loads(wiki_path.read_text(encoding="utf-8"))

    nodes = list(structural.get("nodes") or [])
    links = list(structural.get("links") or [])

    existing_ids = {n["id"] for n in nodes if "id" in n}
    id_map: dict[str, str] = {}

    for wnode in wiki.get("nodes") or []:
        page_id = wnode.get("id")
        if not page_id:
            continue
        gid = _wiki_node_id(page_id)
        id_map[page_id] = gid
        if gid not in existing_ids:
            nodes.append(_to_graphify_wiki_node(wnode))
            existing_ids.add(gid)

    for wlink in wiki.get("links") or []:
        src = id_map.get(wlink.get("source", ""))
        tgt = id_map.get(wlink.get("target", ""))
        if not src or not tgt:
            continue
        links.append(
            {
                "source": src,
                "target": tgt,
                "relation": wlink.get("relation", "wikilink"),
                "context": "wiki",
                "confidence": wlink.get("confidence", "EXTRACTED"),
                "source_file": f"20_knowledge/wiki/{wlink.get('source', '')}.md",
                "source_location": "L1",
                "weight": 1.0,
            }
        )

    merged = {
        "nodes": nodes,
        "links": links,
        "graph_meta": {
            "merged": True,
            "structural_nodes": len(structural.get("nodes") or []),
            "wiki_nodes": len(wiki.get("nodes") or []),
            "total_nodes": len(nodes),
            "total_links": len(links),
            "bridge_edges": 0,
            "bridged": False,
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
    return merged["graph_meta"]


def _apply_wiki_code_bridges(out_path: Path) -> int:
    bridge_script = REPO_ROOT / "40_operations/scripts/graphify_wiki_bridge.py"
    proc = subprocess.run(
        [sys.executable, str(bridge_script), "--merged", str(out_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 0
    m = __import__("re").search(r"added=(\d+)", proc.stdout or "")
    return int(m.group(1)) if m else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build merged brain graph (Graphify structure + wiki wikilinks)"
    )
    parser.add_argument(
        "--skip-structural",
        action="store_true",
        help="Do not rebuild graphify-out/graph.json",
    )
    parser.add_argument(
        "--filtered-wiki",
        action="store_true",
        help="Exclude visibility/internal and pii wiki pages",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=MERGED,
        help="Merged graph output path",
    )
    parser.add_argument(
        "--skip-bridge",
        action="store_true",
        help="Do not add wiki↔code bridge edges after merge",
    )
    args = parser.parse_args()

    if not args.skip_structural:
        rc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "40_operations/scripts/graphify_brain_build.py"), "--force"],
            cwd=REPO_ROOT,
            check=False,
        ).returncode
        if rc != 0:
            return rc

    if not STRUCTURAL.is_file():
        print(f"Missing structural graph: {STRUCTURAL}", file=sys.stderr)
        return 1

    wiki_script = REPO_ROOT / "40_operations/scripts/wiki_export_graph.py"
    wiki_args = [sys.executable, str(wiki_script)]
    if args.filtered_wiki:
        wiki_args.append("--filtered")
    rc = subprocess.run(wiki_args, cwd=REPO_ROOT, check=False).returncode
    if rc != 0:
        return rc

    if not WIKI_GRAPH.is_file():
        print(f"Missing wiki graph: {WIKI_GRAPH}", file=sys.stderr)
        return 1

    meta = merge_graphs(STRUCTURAL, WIKI_GRAPH, args.out)
    bridge_added = 0
    if not args.skip_bridge:
        bridge_added = _apply_wiki_code_bridges(args.out)
        if bridge_added and args.out.is_file():
            merged_data = json.loads(args.out.read_text(encoding="utf-8"))
            meta = merged_data.get("graph_meta") or meta
    print(
        f"\nOK: merged graph -> {args.out} ({args.out.stat().st_size:,} bytes)\n"
        f"  structural nodes: {meta['structural_nodes']}\n"
        f"  wiki nodes added: {meta['wiki_nodes']}\n"
        f"  total nodes: {meta['total_nodes']}, links: {meta['total_links']}\n"
        f"  bridge edges added: {bridge_added or meta.get('bridge_edges', 0)}",
        flush=True,
    )
    print("MCP graphify server prefers merged.json when present.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
