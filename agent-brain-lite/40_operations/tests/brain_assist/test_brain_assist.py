"""Tests for brain_assist TF-IDF routing."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

pytest.importorskip("sklearn")

from brain_assist.skill_rerank import rank_skills  # noqa: E402
from brain_assist.similar_errors import find_similar_errors  # noqa: E402


def test_skill_rerank_meta_analysis():
    hits = rank_skills("meta-analysis forest plot pooled effect", top_k=3)
    ids = [h["id"] for h in hits]
    assert any(x in ids for x in ("meta-analysis", "forest-plot", "publication-bias"))


def test_similar_errors_empty_prompt():
    assert find_similar_errors("") == []
