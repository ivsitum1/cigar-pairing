"""Tests for books_rag injection heuristics."""
from __future__ import annotations

from pathlib import Path

from books_rag.config import make_test_config
from books_rag.injection import build_injection_context, prompt_matches_books_cues, should_inject
from books_rag.retrieval import BooksRetriever


def test_prompt_cues() -> None:
    assert prompt_matches_books_cues("Citiraj prema knjizi o anesteziji")
    assert not prompt_matches_books_cues("hello world")


def test_should_inject_score() -> None:
    assert should_inject("random", 0.4, 0.35)
    assert not should_inject("random", 0.2, 0.35)
    assert should_inject("citiraj prema knjizi", 0.30, 0.35)


def test_build_injection_respects_budget(monkeypatch, tmp_path: Path) -> None:
    cfg = make_test_config(
        tmp_path,
        context_mode="off",
        min_injection_score=0.1,
        max_injection_chars=500,
        top_k_inject=3,
    )
    retriever = BooksRetriever(cfg)

    def fake_search(query: str, k: int | None = None, domain: str | None = None):
        return {
            "ready": True,
            "query": query,
            "items": [
                {
                    "chunk_id": "c1",
                    "score": 0.9,
                    "text": "x" * 300,
                    "metadata": {"title": "T", "domain": "medicine", "source_md": "a.md"},
                }
            ],
        }

    monkeypatch.setattr(retriever, "is_ready", lambda: True)
    monkeypatch.setattr(retriever, "search", fake_search)
    ctx = build_injection_context(retriever, "citiraj knjigu", cfg)
    assert ctx is not None
    assert len(ctx) <= 500
    assert "books_rag" in ctx
