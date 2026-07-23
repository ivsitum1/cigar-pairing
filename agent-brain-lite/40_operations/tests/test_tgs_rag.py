"""Tests for TGS multi-hop wiki RAG."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

WORKSPACE = Path(__file__).resolve().parents[2]
PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.tgs_rag import WikiGraph, _orphan_bridge, tgs_search  # noqa: E402


def test_orphan_bridge_revives_linked_pruned():
    graph = WikiGraph(
        ids=["a", "b", "c"],
        texts=["", "", ""],
        paths={},
        outbound={"a": {"b"}, "b": set(), "c": set()},
        inbound={"a": set(), "b": {"a"}, "c": {"b"}},
        title_to_id={},
    )
    active = {"a", "b"}
    pruned = {"c"}
    revived = _orphan_bridge(active, pruned, graph)
    assert "c" in revived
    assert revived["c"] > 0


@patch("brain_assist.tgs_rag.build_wiki_graph")
def test_tgs_search_fuses_channels(mock_build):
    graph = WikiGraph(
        ids=["concepts/skillrae", "concepts/lifeharness", "orphan"],
        texts=["skillrae execution", "lifeharness layer", "orphan page"],
        paths={
            "concepts/skillrae": WORKSPACE / "20_knowledge/wiki/concepts/SkillRAE retrieval augmented execution.md",
            "concepts/lifeharness": WORKSPACE / "20_knowledge/wiki/concepts/LifeHarness four-layer model.md",
            "orphan": WORKSPACE / "20_knowledge/wiki/orphan.md",
        },
        outbound={
            "concepts/skillrae": {"concepts/lifeharness"},
            "concepts/lifeharness": set(),
            "orphan": set(),
        },
        inbound={
            "concepts/skillrae": set(),
            "concepts/lifeharness": {"concepts/skillrae"},
            "orphan": {"concepts/lifeharness"},
        },
        title_to_id={"skillrae": "concepts/skillrae", "lifeharness": "concepts/lifeharness"},
    )
    mock_build.return_value = graph
    results = tgs_search("SkillRAE harness", top_k=5, min_text_score=0.0)
    assert results
    assert any(r["page_id"] == "concepts/skillrae" for r in results)
