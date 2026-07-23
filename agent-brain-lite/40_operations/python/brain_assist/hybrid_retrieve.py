"""Hybrid wiki retrieval: TF-IDF + 1-hop wikilink bonus (text-graph RAG pilot)."""
from __future__ import annotations

import re
from pathlib import Path

from .tfidf_index import TfidfIndex

WORKSPACE = Path(__file__).resolve().parents[3]
WIKI_ROOT = WORKSPACE / "20_knowledge" / "wiki"
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def _collect_wiki_pages() -> tuple[list[str], list[str], dict[str, Path]]:
    ids: list[str] = []
    texts: list[str] = []
    paths: dict[str, Path] = {}
    if not WIKI_ROOT.is_dir():
        return ids, texts, paths
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
        texts.append(body[:8000])
        paths[page_id] = path
    return ids, texts, paths


def _outbound_links(body: str) -> set[str]:
    return {m.group(1).strip() for m in WIKILINK_RE.finditer(body)}


def _inbound_map(ids: list[str], texts: list[str]) -> dict[str, set[str]]:
    inbound: dict[str, set[str]] = {i: set() for i in ids}
    title_to_id = {i.split("/")[-1].lower(): i for i in ids}
    for page_id, body in zip(ids, texts):
        for link in _outbound_links(body):
            target = title_to_id.get(link.lower())
            if target and target != page_id:
                inbound[target].add(page_id)
    return inbound


def hybrid_search(
    query: str,
    *,
    top_k: int = 10,
    min_score: float = 0.02,
    link_bonus: float = 0.08,
) -> list[dict]:
    ids, texts, paths = _collect_wiki_pages()
    if not ids:
        return []
    index = TfidfIndex(ids, texts)
    ranked = index.rank(query, top_k=top_k * 2, min_score=min_score)
    inbound = _inbound_map(ids, texts)
    results: list[dict] = []
    seen: set[str] = set()
    for page_id, score in ranked:
        bonus = min(link_bonus * len(inbound.get(page_id, [])), link_bonus * 3)
        final = round(score + bonus, 4)
        results.append(
            {
                "page_id": page_id,
                "score": final,
                "tfidf": round(score, 4),
                "link_bonus": round(bonus, 4),
                "inbound_count": len(inbound.get(page_id, [])),
                "path": str(paths[page_id].relative_to(WORKSPACE)).replace("\\", "/"),
            }
        )
        seen.add(page_id)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
