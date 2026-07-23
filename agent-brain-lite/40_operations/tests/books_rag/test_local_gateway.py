"""Tests for local gateway fallback (no Ollama required)."""
from __future__ import annotations

from pathlib import Path

from books_rag.config import make_test_config
from books_rag.local_gateway import summarize_hits


def test_fallback_summary_without_ollama(tmp_path: Path) -> None:
    cfg = make_test_config(
        tmp_path,
        ollama_enabled=False,
        gateway_max_chars=800,
        top_k_inject=2,
    )
    items = [
        {
            "chunk_id": "c1",
            "text": "Welch test does not assume equal variances.",
            "metadata": {"title": "Stats Book"},
        }
    ]
    out = summarize_hits("Welch test", items, cfg)
    assert out["source"] == "fallback"
    assert "c1" in out["answer"]
    assert out["citations"][0]["chunk_id"] == "c1"
