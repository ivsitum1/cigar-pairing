"""Tests for failure_patterns_bridge clustering."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "scripts"))

import failure_patterns_bridge as fpb  # noqa: E402


def test_cluster_errors_empty(tmp_path):
    report = fpb.cluster_errors(tmp_path / "missing.jsonl")
    assert report["total"] == 0
    assert report["clusters"] == []


def test_cluster_errors_groups_by_context(tmp_path):
    log = tmp_path / "error_log.jsonl"
    rows = [
        {"id": "E1", "cat": "writing", "ctx": "manuscript", "err": "em dash", "fix": "remove"},
        {"id": "E2", "cat": "writing", "ctx": "manuscript", "err": "AI phrase", "fix": "rewrite"},
        {"id": "E3", "cat": "stats", "ctx": "cox", "err": "PH", "fix": "zph"},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    report = fpb.cluster_errors(log)
    assert report["total"] == 3
    assert report["by_category"]["writing"] == 2
    keys = [c["cluster_key"] for c in report["clusters"]]
    assert any("manuscript" in k for k in keys)

    clinical = [c for c in report["clusters"] if c["category"] == "writing"]
    assert any(c["size"] >= 2 for c in clinical)
