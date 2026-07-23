"""
Text-Graph Synergy RAG (TGS) for wiki: dual-channel retrieval with multi-hop graph
traversal and orphan entity bridging.

Inspired by NotebookLM TGS RAG synthesis (UNVERIFIED against primary paper).
"""
from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .merged_graph_index import DEFAULT_MERGED, MergedGraphIndex
from .tfidf_index import TfidfIndex

WORKSPACE = Path(__file__).resolve().parents[3]
WIKI_ROOT = WORKSPACE / "20_knowledge" / "wiki"
MERGED_GRAPH = DEFAULT_MERGED
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


@dataclass
class WikiGraph:
    ids: list[str]
    texts: list[str]
    paths: dict[str, Path]
    outbound: dict[str, set[str]]
    inbound: dict[str, set[str]]
    title_to_id: dict[str, str]


def build_wiki_graph() -> WikiGraph:
    ids: list[str] = []
    texts: list[str] = []
    paths: dict[str, Path] = {}
    if not WIKI_ROOT.is_dir():
        return WikiGraph([], [], {}, {}, {}, {})
    for path in WIKI_ROOT.rglob("*.md"):
        if path.name.startswith("."):
            continue
        rel = path.relative_to(WIKI_ROOT)
        page_id = str(rel.with_suffix("")).replace("\\", "/")
        try:
            body = path.read_text(encoding="utf-8")
        except OSError:
            continue
        ids.append(page_id)
        texts.append(body[:12000])
        paths[page_id] = path

    title_to_id = {i.split("/")[-1].lower(): i for i in ids}
    outbound: dict[str, set[str]] = {i: set() for i in ids}
    inbound: dict[str, set[str]] = {i: set() for i in ids}
    for page_id, body in zip(ids, texts):
        for link in {m.group(1).strip() for m in WIKILINK_RE.finditer(body)}:
            target = title_to_id.get(link.lower())
            if target and target != page_id:
                outbound[page_id].add(target)
                inbound[target].add(page_id)
    return WikiGraph(ids, texts, paths, outbound, inbound, title_to_id)


def _lexical_fallback(query: str, graph: WikiGraph, top_k: int) -> list[tuple[str, float]]:
    """When TF-IDF is flat (short query / rare tokens), score by token overlap on id + body."""
    tokens = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]
    if not tokens:
        return []
    scored: list[tuple[str, float]] = []
    for pid, body in zip(graph.ids, graph.texts):
        hay = f"{pid} {body[:4000]}".lower()
        hits = sum(1 for t in tokens if t in hay)
        if hits:
            scored.append((pid, hits / len(tokens)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def _text_channel(query: str, graph: WikiGraph, top_k: int, min_score: float) -> list[tuple[str, float]]:
    if not graph.ids:
        return []
    index = TfidfIndex(graph.ids, graph.texts)
    ranked = index.rank(query, top_k=top_k, min_score=min_score)
    if not ranked or max(sc for _, sc in ranked) <= 0.0:
        fallback = _lexical_fallback(query, graph, top_k)
        if fallback:
            return fallback
    return ranked


def _graph_beam_search(
    seeds: list[str],
    graph: WikiGraph,
    *,
    max_hops: int = 3,
    beam_width: int = 12,
) -> dict[str, float]:
    """Semantic beam over wikilink graph from seed nodes."""
    scores: dict[str, float] = {s: 1.0 for s in seeds if s in graph.outbound}
    visited_depth: dict[str, int] = {s: 0 for s in scores}
    queue: deque[str] = deque(seeds)

    while queue:
        node = queue.popleft()
        depth = visited_depth.get(node, 0)
        if depth >= max_hops:
            continue
        parent_score = scores.get(node, 0.0)
        for nbr in graph.outbound.get(node, ()):
            decay = 0.72 ** (depth + 1)
            candidate = parent_score * decay
            if candidate < 0.02:
                continue
            prev = scores.get(nbr, 0.0)
            if candidate > prev:
                scores[nbr] = candidate
                visited_depth[nbr] = depth + 1
                queue.append(nbr)

    # keep beam width
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:beam_width]
    return dict(ranked)


def _merged_graph_beam_search(
    seeds: list[str],
    graph: WikiGraph,
    merged: MergedGraphIndex,
    *,
    max_hops: int = 2,
    beam_width: int = 12,
) -> dict[str, float]:
    """Expand seeds via graphify merged.json (wiki paths through code nodes)."""
    scores: dict[str, float] = {}
    for seed in seeds:
        if seed not in graph.outbound:
            continue
        for nbr, sc in merged.wiki_neighbors_via_merged(seed, max_hops=max_hops).items():
            if nbr in graph.outbound:
                scores[nbr] = max(scores.get(nbr, 0.0), sc)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:beam_width]
    return dict(ranked)


def _orphan_bridge(
    active: set[str],
    pruned: set[str],
    graph: WikiGraph,
    *,
    bridge_boost: float = 0.15,
) -> dict[str, float]:
    """Resurrect pruned nodes with strong inbound links from active subgraph."""
    revived: dict[str, float] = {}
    for orphan in pruned:
        links_from_active = graph.inbound.get(orphan, set()) & active
        if not links_from_active:
            continue
        strength = min(bridge_boost * len(links_from_active), bridge_boost * 3)
        revived[orphan] = strength
    return revived


@dataclass
class TgsResult:
    page_id: str
    fused_score: float
    text_score: float
    graph_score: float
    bridge_score: float
    hops: int
    path: str


def tgs_search(
    query: str,
    *,
    top_k: int = 10,
    min_text_score: float = 0.02,
    text_weight: float = 0.55,
    graph_weight: float = 0.35,
    bridge_weight: float = 0.10,
    max_hops: int = 3,
    token_budget: int = 12000,
    stop_on_no_new_entities: bool = True,
    merged_graph_path: Path | None = None,
) -> list[dict]:
    graph = build_wiki_graph()
    if not graph.ids:
        return []

    merged = MergedGraphIndex.load(merged_graph_path or MERGED_GRAPH)

    text_ranked = _text_channel(query, graph, top_k=top_k * 3, min_score=0.0)
    text_scores = {pid: sc for pid, sc in text_ranked}
    seeds = [pid for pid, _ in text_ranked[: max(3, top_k)]]
    if not seeds and text_ranked:
        seeds = [text_ranked[0][0]]
    graph_scores = _graph_beam_search(seeds, graph, max_hops=max_hops)
    if merged is not None:
        merged_scores = _merged_graph_beam_search(seeds, graph, merged, max_hops=min(2, max_hops))
        for pid, sc in merged_scores.items():
            graph_scores[pid] = max(graph_scores.get(pid, 0.0), sc * 0.85)

    all_ids = set(text_scores) | set(graph_scores)
    pruned = set(graph.ids) - all_ids
    active = set(seeds) | set(graph_scores.keys())
    bridge_scores = _orphan_bridge(active, pruned, graph)

    fused: list[TgsResult] = []
    for pid in all_ids | set(bridge_scores):
        t = text_scores.get(pid, 0.0)
        g = graph_scores.get(pid, 0.0)
        b = bridge_scores.get(pid, 0.0)
        score = text_weight * t + graph_weight * g + bridge_weight * b
        hops = 0
        if pid in graph_scores and pid not in seeds:
            hops = min(max_hops, 3)
        if pid in graph.paths:
            try:
                path_str = str(graph.paths[pid].relative_to(WORKSPACE)).replace("\\", "/")
            except ValueError:
                path_str = str(graph.paths[pid])
        else:
            path_str = ""
        fused.append(
            TgsResult(
                page_id=pid,
                fused_score=round(float(score), 4),
                text_score=round(float(t), 4),
                graph_score=round(float(g), 4),
                bridge_score=round(float(b), 4),
                hops=hops,
                path=path_str,
            )
        )
    fused.sort(key=lambda x: x.fused_score, reverse=True)
    results = [
        {
            "page_id": r.page_id,
            "score": r.fused_score,
            "text_score": r.text_score,
            "graph_score": r.graph_score,
            "bridge_score": r.bridge_score,
            "hops": r.hops,
            "path": r.path,
        }
        for r in fused[:top_k]
    ]
    if stop_on_no_new_entities and len(results) >= 2:
        seen_entities: set[str] = set()
        filtered: list[dict] = []
        budget_chars = 0
        for row in results:
            tokens = set(re.findall(r"[a-z0-9]{4,}", row["page_id"].lower()))
            new = tokens - seen_entities
            if filtered and not new:
                break
            seen_entities |= tokens
            filtered.append(row)
            budget_chars += len(row.get("path") or row["page_id"]) * 80
            if budget_chars > token_budget:
                filtered.pop()
                break
        return filtered
    return results
