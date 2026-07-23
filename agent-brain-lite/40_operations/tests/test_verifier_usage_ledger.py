"""Tests for verifier usage ledger."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from brain_assist.verifier_usage_ledger import (  # noqa: E402
    prompt_hash,
    read_rows,
    record_larger,
    record_skill_lens,
    sanitize_text,
)


def test_prompt_hash_stable():
    assert prompt_hash("Meta Analysis") == prompt_hash("meta analysis")
    assert len(prompt_hash("x")) == 16


def test_sanitize_redacts_long_numbers():
    out = sanitize_text("patient id 12345678901 noted")
    assert "[REDACTED]" in out


def test_record_skill_lens_and_read(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("VERIFIER_USAGE_LEDGER_PATH", str(ledger))
    bundle = {
        "relation_tag": "causality",
        "decisions": [{"id": "meta-analysis", "action": "ACCEPT", "score": 0.2, "trigger_overlap": 0.5}],
        "to_load": [{"id": "meta-analysis", "action": "ACCEPT"}],
    }
    record_skill_lens(prompt="meta-analysis forest plot", bundle=bundle, session_id="s1")
    rows = read_rows(ledger)
    assert len(rows) == 1
    assert rows[0]["event"] == "beforeSubmitPrompt"
    assert rows[0]["relation_tag"] == "causality"
    assert rows[0]["decisions"][0]["id"] == "meta-analysis"


def test_record_larger(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("VERIFIER_USAGE_LEDGER_PATH", str(ledger))
    record_larger(
        grep_hit="skill_verifier",
        expand_result={
            "anchors": [{"source_file": "a.py"}],
            "neighbors": [{"source_file": "b.py", "relation": "imports", "weight": 0.8}],
        },
    )
    rows = read_rows(ledger)
    assert rows[0]["grep_hit"] == "skill_verifier"
    assert rows[0]["anchor_count"] == 1
    assert len(rows[0]["top_neighbors"]) == 1
