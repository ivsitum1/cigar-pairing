"""LARGER-style lexical anchor + confidence-filtered graph expansion (Graphify substrate)."""
from __future__ import annotations

import json
import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
GRAPH_DIR = WORKSPACE / "graphify-out"

RELATION_WEIGHTS: dict[str, float] = {
    "imports_from": 0.95,
    "import": 0.95,
    "calls": 0.90,
    "invokes": 0.90,
    "references": 0.75,
    "uses": 0.80,
    "conceptually_related_to": 0.55,
    "same_community": 0.70,
}
DEFAULT_WEIGHT = 0.50
MIN_EDGE_WEIGHT = 0.45


def resolve_graph_path(graph_path: Path | None = None) -> Path:
    if graph_path and graph_path.is_file():
        return graph_path
    merged = GRAPH_DIR / "merged.json"
    if merged.is_file():
        return merged
    return GRAPH_DIR / "graph.json"


def load_graph(graph_path: Path | None = None) -> dict:
    path = resolve_graph_path(graph_path)
    if not path.is_file():
        raise FileNotFoundError(f"Graph not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def anchor_nodes(grep_hit: str, graph: dict) -> list[dict]:
    needle = _norm(grep_hit)
    if not needle:
        return []

    tokens = [t for t in needle.split() if len(t) >= 3]
    hits: list[dict] = []

    for node in graph.get("nodes") or []:
        label = _norm(str(node.get("label") or ""))
        norm_label = _norm(str(node.get("norm_label") or ""))
        source_file = _norm(str(node.get("source_file") or "").replace("\\", "/"))
        blob = f"{label} {norm_label} {source_file}"

        if needle in blob or all(t in blob for t in tokens):
            hits.append(node)
        elif any(t in source_file for t in tokens if len(t) >= 5):
            hits.append(node)

    seen: set[str] = set()
    unique: list[dict] = []
    for n in hits:
        nid = n.get("id")
        if nid and nid not in seen:
            seen.add(nid)
            unique.append(n)
    return unique


def _edge_weight(link: dict) -> float:
    rel = str(link.get("relation") or link.get("context") or "").lower()
    base = RELATION_WEIGHTS.get(rel, DEFAULT_WEIGHT)
    conf = link.get("confidence_score")
    if conf is not None:
        try:
            base *= float(conf)
        except (TypeError, ValueError):
            pass
    w = link.get("weight")
    if w is not None:
        try:
            base *= float(w)
        except (TypeError, ValueError):
            pass
    return round(min(1.0, base), 4)


def expand_neighbors(
    anchor_ids: set[str],
    graph: dict,
    *,
    max_neighbors: int = 12,
    min_weight: float = MIN_EDGE_WEIGHT,
) -> list[dict]:
    neighbors: dict[str, dict] = {}
    id_to_node = {n.get("id"): n for n in graph.get("nodes") or [] if n.get("id")}

    for link in graph.get("links") or []:
        src = link.get("source")
        tgt = link.get("target")
        if not src or not tgt:
            continue
        weight = _edge_weight(link)
        if weight < min_weight:
            continue

        if src in anchor_ids and tgt not in anchor_ids:
            node = id_to_node.get(tgt, {})
            prev = neighbors.get(tgt)
            if prev is None or prev["weight"] < weight:
                neighbors[tgt] = {
                    "id": tgt,
                    "label": node.get("label") or tgt,
                    "source_file": node.get("source_file"),
                    "relation": link.get("relation"),
                    "weight": weight,
                    "from_anchor": src,
                }
        elif tgt in anchor_ids and src not in anchor_ids:
            node = id_to_node.get(src, {})
            prev = neighbors.get(src)
            if prev is None or prev["weight"] < weight:
                neighbors[src] = {
                    "id": src,
                    "label": node.get("label") or src,
                    "source_file": node.get("source_file"),
                    "relation": link.get("relation"),
                    "weight": weight,
                    "from_anchor": tgt,
                }

    ranked = sorted(neighbors.values(), key=lambda x: x["weight"], reverse=True)
    return ranked[:max_neighbors]


def expand_from_grep(
    grep_hit: str,
    *,
    graph_path: Path | None = None,
    max_neighbors: int = 12,
    min_weight: float = MIN_EDGE_WEIGHT,
) -> dict:
    graph = load_graph(graph_path)
    anchors = anchor_nodes(grep_hit, graph)
    anchor_ids = {a["id"] for a in anchors if a.get("id")}
    neighbors = expand_neighbors(anchor_ids, graph, max_neighbors=max_neighbors, min_weight=min_weight)
    return {
        "grep_hit": grep_hit,
        "graph_path": str(resolve_graph_path(graph_path).relative_to(WORKSPACE)).replace("\\", "/"),
        "anchors": [
            {
                "id": a.get("id"),
                "label": a.get("label"),
                "source_file": a.get("source_file"),
            }
            for a in anchors[:8]
        ],
        "neighbors": neighbors,
        "neighbor_count": len(neighbors),
    }
