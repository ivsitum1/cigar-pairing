"""Degree-corrected random walk on skill graph (SkillLens retrieval extension)."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
REGISTRY = WORKSPACE / "30_system" / "SKILLS" / "registry.json"

RESTART = 0.2
WALK_STEPS = 4
DEP_WEIGHT = 1.0
REV_WEIGHT = 0.75
PIPELINE_WEIGHT = 0.85


def build_adjacency(skills: list[dict], pipelines: list[dict] | None = None) -> dict[str, list[tuple[str, float]]]:
    adj: dict[str, list[tuple[str, float]]] = defaultdict(list)

    for skill in skills:
        sid = skill["id"]
        for dep in skill.get("depends_on") or []:
            adj[sid].append((dep, DEP_WEIGHT))
            adj[dep].append((sid, REV_WEIGHT))

    for pipe in pipelines or []:
        order: list[str] = []
        for edge in pipe.get("edges", []):
            for node in (edge.get("from"), edge.get("to")):
                if node and node not in order:
                    order.append(node)
        for i in range(len(order) - 1):
            a, b = order[i], order[i + 1]
            adj[a].append((b, PIPELINE_WEIGHT))
            adj[b].append((a, PIPELINE_WEIGHT * 0.9))

    return dict(adj)


def degree_corrected_rwr(
    seed_ids: list[str],
    adj: dict[str, list[tuple[str, float]]],
    *,
    steps: int = WALK_STEPS,
    restart: float = RESTART,
) -> dict[str, float]:
    """Return visit scores for skills reachable from seeds."""
    scores: dict[str, float] = {s: 1.0 for s in seed_ids}
    current = list(seed_ids)

    for _ in range(steps):
        next_scores: dict[str, float] = defaultdict(float)
        for sid in current:
            mass = scores.get(sid, 0.0)
            if mass <= 0:
                continue
            next_scores[sid] += mass * restart
            neighbors = adj.get(sid, [])
            if not neighbors:
                continue
            degree = sum(w for _, w in neighbors)
            if degree <= 0:
                continue
            spread = mass * (1.0 - restart)
            for nb, w in neighbors:
                next_scores[nb] += spread * (w / degree)
        scores = dict(next_scores)
        current = list(scores.keys())

    return scores


def rwr_expand_ranked(
    flat_results: list[dict],
    registry: dict,
    pipelines_doc: dict | None = None,
    *,
    top_k: int = 5,
) -> list[dict]:
    if not flat_results:
        return []

    skills = registry.get("skills") or []
    pipes = (pipelines_doc or {}).get("pipelines") or []
    adj = build_adjacency(skills, pipes)

    seeds = [flat_results[0]["id"]]
    if len(flat_results) > 1:
        seeds.append(flat_results[1]["id"])

    visit_scores = degree_corrected_rwr(seeds, adj)
    meta = {s["id"]: s for s in skills}
    flat_by_id = {r["id"]: r for r in flat_results}

    merged: list[dict] = []
    for sid, rwr_score in sorted(visit_scores.items(), key=lambda x: x[1], reverse=True):
        if sid not in meta:
            continue
        base = flat_by_id.get(sid)
        tfidf = (base.get("tfidf_score") or base.get("score", 0.0)) if base else 0.0
        combined = round(tfidf + rwr_score * 0.08, 4)
        entry = {
            **(base or {
                "id": sid,
                "domain": meta[sid].get("domain", ""),
                "file": meta[sid].get("file", ""),
                "triggers": meta[sid].get("triggers") or [],
            }),
            "score": combined,
            "tfidf_score": round(tfidf, 4),
            "rwr_score": round(rwr_score, 4),
            "rwr_seed": sid in seeds,
        }
        merged.append(entry)

    merged.sort(key=lambda x: x["score"], reverse=True)
    return merged[:top_k]
