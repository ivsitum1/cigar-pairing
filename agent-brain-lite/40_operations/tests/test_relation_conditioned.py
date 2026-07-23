"""Tests for Relation-Conditioned incorporation (SkillLens + LARGER)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

pytest.importorskip("sklearn")

from brain_assist.skill_verifier import verify_bundle, verify_skill  # noqa: E402
from brain_assist.skill_rwr import build_adjacency, degree_corrected_rwr  # noqa: E402
from brain_assist.skill_rerank import rank_skills  # noqa: E402
from harness.larger_graph_expand import anchor_nodes, expand_from_grep, load_graph  # noqa: E402


def test_verify_meta_analysis_accept_or_decompose():
    result = verify_bundle("meta-analysis forest plot pooled effect", dag_mode=True, top_k=5)
    actions = {d["id"]: d["action"] for d in result["decisions"]}
    assert "meta-analysis" in actions
    assert actions["meta-analysis"] in {"ACCEPT", "DECOMPOSE"}


def test_verify_unrelated_mostly_skip():
    result = verify_bundle("xyzzy plugh qwerty 999888777", top_k=5, dag_mode=False)
    assert not result["to_load"] or all(d["action"] == "SKIP" for d in result["to_load"])


def test_policy_granularity_forces_accept():
    decision = verify_skill(
        "anything",
        {"id": "core", "score": 0.01, "triggers": [], "granularity": "policy"},
    )
    assert decision["action"] == "ACCEPT"


def test_rwr_reaches_prerequisite():
    skills = [
        {"id": "grill-me", "depends_on": []},
        {"id": "write-prd", "depends_on": ["grill-me"]},
    ]
    adj = build_adjacency(skills)
    scores = degree_corrected_rwr(["write-prd"], adj, steps=4)
    assert "grill-me" in scores


def test_rwr_mode_changes_ranking():
    flat = rank_skills("Write PRD product requirements", top_k=4, dag_mode=False, rwr_mode=False)
    rwr = rank_skills("Write PRD product requirements", top_k=4, dag_mode=False, rwr_mode=True)
    assert flat and rwr
    assert any(r.get("rwr_score") for r in rwr)


@pytest.mark.skipif(
    not (REPO / "graphify-out" / "graph.json").is_file(),
    reason="graphify-out/graph.json not built",
)
def test_larger_expand_skill_rerank_neighbors():
    result = expand_from_grep("skill_rerank.py")
    assert result["anchors"]
    assert result["neighbor_count"] >= 1


@pytest.mark.skipif(
    not (REPO / "graphify-out" / "graph.json").is_file(),
    reason="graphify-out/graph.json not built",
)
def test_anchor_nodes_find_file():
    graph = load_graph()
    anchors = anchor_nodes("skill_rerank.py", graph)
    files = " ".join(str(a.get("source_file") or "") for a in anchors)
    assert "skill_rerank" in files.lower()


def test_gap_report_module_import():
    from trajectory_rl.gap_report import build_gap_report  # noqa: E402

    report = build_gap_report()
    assert "gaps" in report
