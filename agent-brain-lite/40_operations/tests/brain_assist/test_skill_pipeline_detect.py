"""Tests for semantic pipeline auto-load (PRD / Ralph)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from brain_assist.skill_pipeline_detect import detect_pipeline  # noqa: E402
from brain_assist.skill_rerank import rank_skills  # noqa: E402


def test_detect_ralph_pipeline():
    hit = detect_pipeline("Ralph ON — execute PRD tasks autonomously")
    assert hit is not None
    assert hit["pipeline_id"] == "agentic-engineering"
    assert hit["target_skill"] == "ralph-loop"
    assert hit["skills"] == ["grill-me", "write-prd", "prd-to-issues", "ralph-loop"]


def test_detect_write_prd_pipeline():
    hit = detect_pipeline("Write PRD for new billing feature")
    assert hit is not None
    assert hit["target_skill"] == "write-prd"
    assert hit["skills"] == ["grill-me", "write-prd"]


def test_file_hint_prd_json():
    hit = detect_pipeline("fix this", context_files=["30_system/docs/prd.json"])
    assert hit is not None
    assert hit["target_skill"] == "write-prd"


def test_auto_pipeline_rank_skills():
    rows = rank_skills("Ralph loop iteration 3", auto_pipeline=True, dag_mode=True)
    ids = [r["id"] for r in rows]
    assert ids == ["grill-me", "write-prd", "prd-to-issues", "ralph-loop"]
    assert rows[0].get("pipeline_auto_load", {}).get("auto_load") is True


def test_no_pipeline_for_meta_analysis():
    hit = detect_pipeline("meta-analysis forest plot I2 heterogeneity")
    assert hit is None
