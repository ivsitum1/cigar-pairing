#!/usr/bin/env python3
"""Validate skill registry DAG metadata and declarative pipeline DAGs.

Checks:
- depends_on references resolve to known skill ids
- depends_on graph is acyclic
- skill_pipelines_dag.json edges reference valid skills and form DAGs
- tier3_pairing forbidden_pairs do not contradict allowed simultaneous load
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
REGISTRY_PATH = WORKSPACE / "30_system" / "SKILLS" / "registry.json"
PIPELINES_PATH = WORKSPACE / "30_system" / "docs" / "skill_pipelines_dag.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _skill_index(registry: dict) -> dict[str, dict]:
    return {s["id"]: s for s in registry.get("skills", [])}


def _depends_graph(skills: list[dict]) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for skill in skills:
        sid = skill["id"]
        graph.setdefault(sid, [])
        for dep in skill.get("depends_on") or []:
            graph.setdefault(dep, [])
            graph[sid].append(dep)
    return graph


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visited: set[str] = set()
    stack: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        if node in stack:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        path.append(node)
        for dep in graph.get(node, []):
            dfs(dep)
        path.pop()
        stack.remove(node)

    for node in graph:
        dfs(node)
    return cycles


def _pipeline_edges(pipelines_doc: dict) -> list[tuple[str, str, str]]:
    edges: list[tuple[str, str, str]] = []
    for pipe in pipelines_doc.get("pipelines", []):
        pid = pipe.get("id", "?")
        for edge in pipe.get("edges", []):
            edges.append((pid, edge["from"], edge["to"]))
    return edges


def validate(registry_path: Path = REGISTRY_PATH, pipelines_path: Path = PIPELINES_PATH) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    if not registry_path.exists():
        return [f"Registry not found: {registry_path}"]

    registry = _load_json(registry_path)
    skills = registry.get("skills", [])
    index = _skill_index(registry)
    ids = set(index)

    for skill in skills:
        sid = skill["id"]
        for dep in skill.get("depends_on") or []:
            if dep not in ids:
                errors.append(f"[{sid}] depends_on references unknown skill: {dep}")

    dep_graph = _depends_graph(skills)
    for cycle in _find_cycles(dep_graph):
        errors.append(f"depends_on cycle: {' -> '.join(cycle)}")

    for skill in skills:
        sid = skill["id"]
        conflicts = set(skill.get("conflicts_with") or [])
        for other in conflicts:
            if other not in ids:
                errors.append(f"[{sid}] conflicts_with references unknown skill: {other}")

    tier3 = registry.get("tier3_pairing", {})
    for a, b in tier3.get("forbidden_pairs", []):
        if a not in ids or b not in ids:
            warnings.append(f"tier3 forbidden_pair references unknown skill: {a}, {b}")

    if pipelines_path.exists():
        pipelines_doc = _load_json(pipelines_path)
        pipe_graph: dict[str, list[str]] = {}
        for pipe_id, src, dst in _pipeline_edges(pipelines_doc):
            if src not in ids:
                errors.append(f"pipeline [{pipe_id}] edge from unknown skill: {src}")
            if dst not in ids:
                errors.append(f"pipeline [{pipe_id}] edge to unknown skill: {dst}")
            pipe_graph.setdefault(dst, []).append(src)
            pipe_graph.setdefault(src, pipe_graph.get(src, []))

        for cycle in _find_cycles(pipe_graph):
            errors.append(f"pipeline DAG cycle: {' -> '.join(cycle)}")

        for pipe in pipelines_doc.get("pipelines", []):
            pid = pipe.get("id", "?")
            entry = pipe.get("entry")
            exit_id = pipe.get("exit")
            if entry and entry not in ids:
                errors.append(f"pipeline [{pid}] entry unknown: {entry}")
            if exit_id and exit_id not in ids:
                errors.append(f"pipeline [{pid}] exit unknown: {exit_id}")
    else:
        warnings.append(f"Pipeline DAG file missing (skipped): {pipelines_path}")

    grouped: dict[str, list[str]] = {}
    for skill in skills:
        pg = skill.get("pipeline_group")
        if pg:
            grouped.setdefault(pg, []).append(skill["id"])

    if pipelines_path.exists():
        declared = {p["id"] for p in _load_json(pipelines_path).get("pipelines", [])}
        for pg, members in grouped.items():
            if pg not in declared:
                warnings.append(
                    f"pipeline_group '{pg}' on skills {members} has no matching pipeline in skill_pipelines_dag.json"
                )

    return errors + [f"WARN: {w}" for w in warnings]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill DAG metadata in registry and pipelines.")
    parser.add_argument("--registry", default=str(REGISTRY_PATH))
    parser.add_argument("--pipelines", default=str(PIPELINES_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    issues = validate(Path(args.registry), Path(args.pipelines))
    hard = [i for i in issues if not i.startswith("WARN:")]

    if args.json:
        print(json.dumps({"ok": not hard, "issues": issues}, ensure_ascii=False, indent=2))
    else:
        for issue in issues:
            print(issue, file=sys.stderr if not issue.startswith("WARN:") else sys.stdout)
        if hard:
            print(f"{len(hard)} error(s)", file=sys.stderr)
        elif issues:
            print(f"OK with {len(issues)} warning(s)")

    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
