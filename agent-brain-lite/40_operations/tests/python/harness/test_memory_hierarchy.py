"""Tests for harness.memory_hierarchy."""
from pathlib import Path

import pytest


@pytest.fixture
def mh_paths(tmp_path, monkeypatch):
    agent = tmp_path / ".agent"
    agent.mkdir()
    mh = agent / "memory_hierarchy"
    monkeypatch.chdir(tmp_path)
    import harness.memory_hierarchy as mh_mod

    monkeypatch.setattr(mh_mod, "AGENT", agent)
    monkeypatch.setattr(mh_mod, "MEMORY_HIERARCHY", mh)
    monkeypatch.setattr(mh_mod, "INDEX_PATH", mh / "index.json")
    monkeypatch.setattr(mh_mod, "SUMMARIES_DIR", mh / "summaries")
    return mh_mod, mh


def test_bootstrap_creates_index(mh_paths):
    mh_mod, mh = mh_paths
    data = mh_mod.bootstrap()
    assert (mh / "index.json").is_file()
    assert data["nodes"] == []


def test_add_lemma_node(mh_paths):
    mh_mod, mh = mh_paths
    node = mh_mod.add_lemma_node(
        subgoal="verify PH assumption",
        summary="Use cox.zph before Cox model",
        provenance="test/provenance.md",
        solved_lemmas_line=1,
    )
    assert node["id"] == "lemma-001"
    assert (mh / "summaries" / "lemma-001-verify-ph-assumption.md").is_file()
    index = mh_mod.load_index()
    assert len(index["nodes"]) == 1
    assert "test/provenance.md" in index["nodes"][0]["provenance"]


def test_sync_from_solved_lemmas(mh_paths):
    mh_mod, mh = mh_paths
    lemmas = mh_paths[1].parent / "solved_lemmas.jsonl"
    lemmas.write_text(
        '{"subgoal":"a","summary":"sum a","provenance":""}\n'
        '{"subgoal":"b","summary":"sum b","provenance":"ref"}\n',
        encoding="utf-8",
    )
    added = mh_mod.sync_from_solved_lemmas(lemmas)
    assert added == 2
    assert len(mh_mod.load_index()["nodes"]) == 2
