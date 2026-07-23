"""
Lightweight cross-encoder rerank for fused RAG shortlists.

Uses lexical overlap proxy when sentence-transformers cross-encoder unavailable.
"""
from __future__ import annotations

import re
from typing import Any


def _token_set(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def rerank_items(query: str, items: list[dict[str, Any]], *, top_k: int = 10) -> list[dict[str, Any]]:
    """Re-score items by query-token overlap on title + text_preview (CE proxy)."""
    if not items:
        return []
    q = _token_set(query)
    if not q:
        return items[:top_k]

    scored: list[tuple[float, dict[str, Any]]] = []
    for item in items:
        blob = " ".join(
            str(item.get(k) or "")
            for k in ("title", "page_id", "text_preview", "source_md", "id")
        )
        t = _token_set(blob)
        overlap = len(q & t) / max(len(q), 1)
        base = float(item.get("score") or item.get("fused_score") or item.get("ce_score") or 0.0)
        combined = round(0.55 * base + 0.45 * overlap, 4)
        scored.append((combined, {**item, "ce_score": combined, "ce_overlap": round(overlap, 4)}))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [row for _, row in scored[:top_k]]
