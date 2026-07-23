"""Tests for skill_dag_rerank (P2 --dag mode)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

pytest.importorskip("sklearn")

from brain_assist.skill_dag_rerank import apply_dag_bundle, prereq_chain  # noqa: E402
from brain_assist.skill_rerank import rank_skills  # noqa: E402


def test_prereq_chain_write_prd():
    dep = {"write-prd": ["grill-me"], "prd-to-issues": ["write-prd"]}
    assert prereq_chain("write-prd", dep) == ["grill-me"]
    assert prereq_chain("prd-to-issues", dep) == ["grill-me", "write-prd"]


def test_dag_mode_injects_grill_me_for_write_prd():
    flat = rank_skills("Write PRD product requirements document", top_k=3, dag_mode=False)
    assert flat and flat[0]["id"] == "write-prd"

    dag = rank_skills("Write PRD product requirements document", top_k=3, dag_mode=True)
    ids = [r["id"] for r in dag]
    assert "write-prd" in ids
    assert "grill-me" in ids
    assert ids.index("grill-me") < ids.index("write-prd")
    assert dag[0].get("dag", {}).get("anchor") == "write-prd"


def test_dag_mode_no_injection_for_meta_analysis():
    dag = rank_skills("meta-analysis forest plot pooled effect", top_k=3, dag_mode=True)
    ids = [r["id"] for r in dag]
    assert "meta-analysis" in ids or "forest-plot" in ids
    assert "grill-me" not in ids


def test_apply_dag_bundle_prerequisite_role():
    registry = {
        "skills": [
            {"id": "grill-me", "domain": "engineering", "file": "SKILL_grill-me.md", "triggers": []},
            {
                "id": "write-prd",
                "domain": "engineering",
                "file": "SKILL_write-prd.md",
                "triggers": [],
                "depends_on": ["grill-me"],
                "pipeline_group": "agentic-engineering",
            },
        ]
    }
    flat = [
        {"id": "write-prd", "score": 0.5, "tfidf_score": 0.5, "domain": "engineering", "file": "", "triggers": []},
    ]
    bundled, meta = apply_dag_bundle(flat, registry, {"pipelines": []}, top_k=3)
    assert [r["id"] for r in bundled] == ["grill-me", "write-prd"]
    assert bundled[0]["dag_role"] == "prerequisite"
    assert bundled[1]["dag_role"] == "anchor"
    assert meta["prerequisites_injected"] == ["grill-me"]
