"""Tests for chunk_policy parent-child and framing."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "python"
sys.path.insert(0, str(ROOT))

from brain_assist.chunk_policy import (  # noqa: E402
    framed_embed_text,
    orphan_chunks,
    resolve_parent,
    split_markdown_sections,
)


SAMPLE = """# Title

Intro paragraph.

## Methods

Method detail line one.
Method detail line two.

### Subsection

More text here.
"""


def test_framed_embed_text_includes_path() -> None:
    out = framed_embed_text("My Doc", "Methods", "body")
    assert "My Doc > Methods" in out
    assert "body" in out


def test_split_creates_parent_and_children() -> None:
    recs = split_markdown_sections(
        SAMPLE,
        doc_title="test/doc",
        doc_version="2026-06-24",
        source_type="wiki",
        child_max_chars=500,
    )
    assert len(recs) >= 2
    parents = [r for r in recs if r.metadata.get("role") == "parent"]
    children = [r for r in recs if r.metadata.get("role") == "child"]
    assert parents
    assert children
    assert all(c.parent_id for c in children)
    assert orphan_chunks(recs) == []


def test_resolve_parent() -> None:
    recs = split_markdown_sections(
        SAMPLE,
        doc_title="t",
        doc_version="v1",
        source_type="wiki",
    )
    child = next(r for r in recs if r.parent_id)
    parent = resolve_parent(recs, child.chunk_id)
    assert parent is not None
    assert parent.chunk_id == child.parent_id


def test_validates_required_metadata() -> None:
    recs = split_markdown_sections(
        SAMPLE,
        doc_title="t",
        doc_version="v1",
        source_type="wiki",
    )
    for r in recs:
        assert r.validates() == []
