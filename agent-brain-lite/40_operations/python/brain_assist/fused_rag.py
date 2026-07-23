"""
Fused retrieval: books_rag vector channel + wiki TGS graph channel.

Bridges book chunks to wiki nodes via source_md basename overlap and title token match.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .tgs_rag import tgs_search

WORKSPACE = Path(__file__).resolve().parents[3]


def _normalize_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _book_items(
    query: str,
    top_k: int,
    cfg: Any | None = None,
) -> list[dict[str, Any]]:
    try:
        from books_rag.config import load_config
        from books_rag.retrieval import BooksRetriever
    except ImportError:
        return []

    resolved = cfg or load_config()
    retriever = BooksRetriever(resolved)
    if not retriever.is_ready():
        return []
    result = retriever.search(
        query,
        k=top_k,
        mode="chunks",
        use_rerank=True,
        use_hybrid=True,
    )
    items: list[dict[str, Any]] = []
    for rank, row in enumerate(result.get("items") or []):
        meta = row.get("metadata") or {}
        score = float(row.get("score") or row.get("rerank_score") or (1.0 / (rank + 1)))
        items.append(
            {
                "channel": "books",
                "id": row.get("chunk_id") or row.get("id") or f"book_{rank}",
                "score": score,
                "title": meta.get("title") or "",
                "source_md": meta.get("source_md") or "",
                "domain": meta.get("domain") or "",
                "text_preview": (row.get("text") or "")[:240],
            }
        )
    return items


def _bridge_keys(item: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for field in ("title", "source_md", "domain"):
        val = str(item.get(field) or "")
        if val:
            keys.add(_normalize_key(Path(val).stem if "/" in val or "\\" in val else val))
            for tok in _normalize_key(val).split():
                if len(tok) > 3:
                    keys.add(tok)
    return keys


def _wiki_bridge_score(book_keys: set[str], wiki_page_id: str) -> float:
    wiki_key = _normalize_key(wiki_page_id.replace("/", " "))
    if not book_keys or not wiki_key:
        return 0.0
    wiki_tokens = set(wiki_key.split())
    overlap = book_keys & wiki_tokens
    if overlap:
        return min(0.35, 0.12 * len(overlap))
    for bk in book_keys:
        if len(bk) > 4 and bk in wiki_key:
            return 0.18
    return 0.0


def fused_search(
    query: str,
    *,
    top_k: int = 10,
    book_weight: float = 0.50,
    wiki_weight: float = 0.35,
    bridge_weight: float = 0.15,
    max_hops: int = 3,
) -> dict[str, Any]:
    cfg = None
    try:
        from books_rag.config import load_config

        cfg = load_config()
    except ImportError:
        pass

    books = _book_items(query, top_k=top_k, cfg=cfg)
    wiki = tgs_search(query, top_k=top_k, max_hops=max_hops)

    book_max = max((b["score"] for b in books), default=1.0) or 1.0
    wiki_max = max((w["score"] for w in wiki), default=1.0) or 1.0

    fused: list[dict[str, Any]] = []

    for b in books:
        norm_book = b["score"] / book_max
        bridge = 0.0
        bkeys = _bridge_keys(b)
        for w in wiki:
            bridge = max(bridge, _wiki_bridge_score(bkeys, w["page_id"]))
        fused.append(
            {
                "id": b["id"],
                "source": "books_rag",
                "fused_score": round(
                    book_weight * norm_book + bridge_weight * bridge,
                    4,
                ),
                "book_score": round(norm_book, 4),
                "wiki_score": 0.0,
                "bridge_score": round(bridge, 4),
                "title": b["title"],
                "source_md": b["source_md"],
                "text_preview": b["text_preview"],
            }
        )

    for w in wiki:
        norm_wiki = w["score"] / wiki_max
        bridge = 0.0
        for b in books:
            bridge = max(bridge, _wiki_bridge_score(_bridge_keys(b), w["page_id"]))
        fused.append(
            {
                "id": w["page_id"],
                "source": "wiki_tgs",
                "fused_score": round(
                    wiki_weight * norm_wiki + bridge_weight * bridge,
                    4,
                ),
                "book_score": 0.0,
                "wiki_score": round(norm_wiki, 4),
                "bridge_score": round(bridge, 4),
                "path": w.get("path", ""),
                "hops": w.get("hops", 0),
            }
        )

    fused.sort(key=lambda x: x["fused_score"], reverse=True)
    results = fused[:top_k]
    try:
        from .rerank_ce import rerank_items

        results = rerank_items(query, results, top_k=top_k)
    except ImportError:
        pass

    books_data_dir = str(cfg.data_dir) if cfg else ""
    books_chunk_count = 0
    if cfg and books:
        from books_rag.retrieval import BooksRetriever

        books_chunk_count = BooksRetriever(cfg).store.count()

    return {
        "mode": "fused_books_tgs",
        "query": query,
        "books_ready": bool(books),
        "books_data_dir": books_data_dir,
        "books_chunk_count": books_chunk_count,
        "wiki_root": str(WORKSPACE / "20_knowledge" / "wiki"),
        "wiki_hits": len(wiki),
        "results": results,
    }
