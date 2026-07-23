#!/usr/bin/env python3
"""Validate graphify-out/merged.json integrity (structural + wiki)."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STRUCTURAL = REPO_ROOT / "graphify-out" / "graph.json"
WIKI_GRAPH = REPO_ROOT / "wiki-export" / "graph.json"
MERGED = REPO_ROOT / "graphify-out" / "merged.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(merged_path: Path, *, query: bool = True) -> dict:
    issues: list[str] = []
    if not merged_path.is_file():
        return {"ok": False, "issues": [f"missing: {merged_path}"]}

    merged = _load(merged_path)
    nodes = merged.get("nodes") or []
    links = merged.get("links") or []
    meta = merged.get("graph_meta") or {}

    node_ids = {n["id"] for n in nodes if n.get("id")}
    wiki_nodes = [n for n in nodes if n.get("file_type") == "wiki" or str(n.get("id", "")).startswith("wiki_")]
    code_nodes = [n for n in nodes if n.get("file_type") == "code"]

    broken = 0
    cross = 0
    wiki_ids = {n["id"] for n in wiki_nodes}
    code_ids = {n["id"] for n in code_nodes}
    for link in links:
        s, t = link.get("source"), link.get("target")
        if s not in node_ids or t not in node_ids:
            broken += 1
        if (s in wiki_ids and t in code_ids) or (t in wiki_ids and s in code_ids):
            cross += 1

    if not meta.get("merged"):
        issues.append("graph_meta.merged is not true")
    if meta.get("total_nodes") and meta["total_nodes"] != len(nodes):
        issues.append(
            f"graph_meta.total_nodes ({meta['total_nodes']}) != actual nodes ({len(nodes)})"
        )
    if broken:
        issues.append(f"{broken} links reference missing node ids")

    ft = Counter(n.get("file_type", "?") for n in nodes)
    query_ok = None
    query_snippet = ""
    if query:
        if shutil.which("graphify"):
            cmd = ["graphify", "query", "orchestrator memory hooks", "--graph", str(merged_path)]
        else:
            cmd = [sys.executable, "-m", "graphify", "query", "orchestrator memory hooks", "--graph", str(merged_path)]
        try:
            proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=60, check=False)
            out = (proc.stdout or proc.stderr or "").strip()
            query_ok = proc.returncode == 0 and "NODE" in out
            query_snippet = "\n".join(out.splitlines()[:4])
            if not query_ok:
                issues.append("graphify query smoke test failed")
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            query_ok = False
            issues.append(f"graphify query unavailable: {exc}")

    return {
        "ok": not issues,
        "path": str(merged_path),
        "size_bytes": merged_path.stat().st_size,
        "nodes": len(nodes),
        "links": len(links),
        "file_types": dict(ft),
        "wiki_nodes": len(wiki_nodes),
        "code_nodes": len(code_nodes),
        "cross_wiki_code_links": cross,
        "bridge_edges": sum(1 for l in links if l.get("relation") == "bridges_to"),
        "broken_links": broken,
        "graph_meta": meta,
        "query_ok": query_ok,
        "query_snippet": query_snippet,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify merged Graphify + wiki graph")
    parser.add_argument("--merged", type=Path, default=MERGED)
    parser.add_argument("--no-query", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = verify(args.merged, query=not args.no_query)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        status = "OK" if report["ok"] else "FAIL"
        print(f"merge verify: {status}")
        print(f"  path: {report.get('path')}")
        print(f"  size: {report.get('size_bytes', 0):,} bytes")
        print(f"  nodes: {report.get('nodes')} links: {report.get('links')}")
        print(f"  wiki: {report.get('wiki_nodes')} code: {report.get('code_nodes')}")
        print(f"  cross wiki-code links: {report.get('cross_wiki_code_links')}")
        print(f"  bridge edges (bridges_to): {report.get('bridge_edges')}")
        print(f"  broken links: {report.get('broken_links')}")
        if report.get("query_ok") is not None:
            print(f"  query smoke: {'pass' if report['query_ok'] else 'fail'}")
        if report.get("issues"):
            for issue in report["issues"]:
                print(f"  ISSUE: {issue}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
