"""Tests for keyword hybrid boost."""
from __future__ import annotations

from books_rag.hybrid import apply_keyword_boost


def test_keyword_boost_orders_by_overlap() -> None:
    items = [
        {
            "chunk_id": "a",
            "score": 0.5,
            "text": "unrelated topic",
            "metadata": {"title": "Other", "domain": ""},
        },
        {
            "chunk_id": "b",
            "score": 0.48,
            "text": "Welch t-test assumptions",
            "metadata": {"title": "Statistics", "domain": "methods"},
        },
    ]
    out = apply_keyword_boost("Welch t-test pretpostavke", items, max_boost=0.2)
    assert out[0]["chunk_id"] == "b"
    assert out[0]["score"] > out[1]["score"]
