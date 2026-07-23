"""Retrieval tests with mocked vector store."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from books_rag.config import make_test_config
from books_rag.retrieval import BooksRetriever


def test_format_search_results() -> None:
    cfg = make_test_config(Path("."))
    retriever = BooksRetriever(cfg)
    formatted = retriever.format_search_results(
        {
            "ready": True,
            "items": [
                {
                    "chunk_id": "abc_123",
                    "score": 0.88,
                    "text": "Regional nerve blocks.",
                    "metadata": {
                        "title": "Hadzic",
                        "domain": "medicine",
                        "page_hint": "42",
                        "source_md": "20_knowledge/wiki/sources/books_md/x.md",
                    },
                }
            ],
        }
    )
    assert "[books_rag:abc_123]" in formatted
    assert "Hadzic" in formatted
    assert "p.42" in formatted
