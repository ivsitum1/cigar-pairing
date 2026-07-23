"""Tests for fused books_rag + TGS search."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

WORKSPACE = Path(__file__).resolve().parents[2]
PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.fused_rag import _wiki_bridge_score, fused_search  # noqa: E402


def test_wiki_bridge_score_overlap():
    book_keys = {"skillrae", "lifeharness"}
    score = _wiki_bridge_score(book_keys, "concepts/SkillRAE retrieval augmented execution")
    assert score > 0


@patch("brain_assist.fused_rag._book_items")
@patch("brain_assist.fused_rag.tgs_search")
def test_fused_search_combines_channels(mock_tgs, mock_books):
    mock_books.return_value = [
        {
            "channel": "books",
            "id": "chunk_1",
            "score": 0.9,
            "title": "LifeHarness layer model",
            "source_md": "books_md/stats/lifeharness.md",
            "domain": "engineering",
            "text_preview": "harness layers",
        }
    ]
    mock_tgs.return_value = [
        {
            "page_id": "concepts/LifeHarness four-layer model",
            "score": 0.8,
            "text_score": 0.8,
            "graph_score": 0.5,
            "bridge_score": 0.0,
            "hops": 0,
            "path": "20_knowledge/wiki/concepts/LifeHarness four-layer model.md",
        }
    ]
    payload = fused_search("LifeHarness", top_k=5)
    assert payload["mode"] == "fused_books_tgs"
    assert len(payload["results"]) >= 2
    sources = {r["source"] for r in payload["results"]}
    assert "books_rag" in sources
    assert "wiki_tgs" in sources
