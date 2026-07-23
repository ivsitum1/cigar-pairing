"""Tests for merged graph index, bridges, and TGS merged hook."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

WORKSPACE = Path(__file__).resolve().parents[2]
PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.merged_graph_index import MergedGraphIndex, wiki_node_id  # noqa: E402
from brain_assist.tgs_rag import WikiGraph, _merged_graph_beam_search  # noqa: E402


def test_wiki_node_id_stable():
    assert wiki_node_id("concepts/Skill registry").startswith("wiki_")


def test_propose_bridge_links_token_overlap(tmp_path: Path):
    merged = {
        "nodes": [
            {
                "id": wiki_node_id("concepts/skill-rerank"),
                "file_type": "wiki",
                "source_file": "20_knowledge/wiki/concepts/skill-rerank.md",
                "label": "Skill Rerank",
            },
            {
                "id": "scripts_skill_rerank_py",
                "file_type": "code",
                "source_file": "40_operations/scripts/skill_rerank.py",
                "label": "skill_rerank.py",
            },
        ],
        "links": [],
    }
    path = tmp_path / "merged.json"
    path.write_text(json.dumps(merged), encoding="utf-8")
    index = MergedGraphIndex.load(path)
    assert index is not None
    links = index.propose_bridge_links()
    assert any(l["source"].startswith("wiki_") and l["target"] == "scripts_skill_rerank_py" for l in links)


def test_merged_graph_beam_finds_neighbor_via_code():
    wiki_a = wiki_node_id("concepts/a")
    wiki_b = wiki_node_id("concepts/b")
    code = "scripts_link_py"
    index = MergedGraphIndex(
        path=Path("merged.json"),
        nodes={wiki_a: {}, wiki_b: {}, code: {}},
        outbound={wiki_a: {code}, code: {wiki_b}, wiki_b: set()},
        inbound={wiki_a: set(), code: {wiki_a}, wiki_b: {code}},
        wiki_page_by_gid={wiki_a: "concepts/a", wiki_b: "concepts/b"},
        page_by_wiki_gid={"concepts/a": wiki_a, "concepts/b": wiki_b},
        code_nodes=[{"id": code, "file_type": "code", "source_file": "40_operations/scripts/link.py"}],
    )
    graph = WikiGraph(
        ids=["concepts/a", "concepts/b"],
        texts=["", ""],
        paths={},
        outbound={"concepts/a": set(), "concepts/b": set()},
        inbound={"concepts/a": set(), "concepts/b": set()},
        title_to_id={},
    )
    scores = _merged_graph_beam_search(["concepts/a"], graph, index, max_hops=2)
    assert "concepts/b" in scores
