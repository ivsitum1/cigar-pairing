"""Tests for SkillLens + LARGER Cursor hook helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

pytest.importorskip("sklearn")

from harness.relation_conditioned_hook import (  # noqa: E402
    build_skill_lens_context,
    extract_grep_hit,
    extract_user_prompt,
    is_grep_tool_use,
    merge_additional_context,
)


def test_extract_user_prompt():
    assert extract_user_prompt({"prompt": "meta-analysis forest plot"}) == "meta-analysis forest plot"


def test_is_grep_tool():
    assert is_grep_tool_use({"toolName": "Grep", "arguments": {"pattern": "skill_rerank"}})
    assert is_grep_tool_use({"toolName": "Shell", "arguments": {"command": "rg skill_verifier"}})
    assert not is_grep_tool_use({"toolName": "Read", "arguments": {"path": "x.py"}})


def test_extract_grep_hit_from_pattern():
    payload = {"toolName": "Grep", "arguments": {"pattern": "skill_rerank.py"}}
    assert extract_grep_hit(payload) == "skill_rerank.py"


def test_extract_grep_hit_from_output():
    payload = {
        "toolName": "Grep",
        "arguments": {},
        "result": "40_operations/scripts/skill_rerank.py:10:from brain_assist",
    }
    assert "skill_rerank" in (extract_grep_hit(payload) or "")


def test_build_skill_lens_context_meta_analysis():
    ctx = build_skill_lens_context("meta-analysis forest plot pooled effect")
    assert ctx is not None
    assert "SkillLens" in ctx
    assert "meta-analysis" in ctx


def test_merge_additional_context():
    merged = merge_additional_context("existing", "[LARGER] neighbors")
    assert "existing" in merged
    assert "LARGER" in merged


@pytest.mark.skipif(
    not (REPO / "graphify-out" / "graph.json").is_file()
    and not (REPO / "graphify-out" / "merged.json").is_file(),
    reason="graphify-out not built",
)
def test_build_larger_context_smoke():
    from harness.relation_conditioned_hook import build_larger_context

    ctx = build_larger_context("skill_rerank.py")
    assert ctx is not None
    assert "LARGER" in ctx
