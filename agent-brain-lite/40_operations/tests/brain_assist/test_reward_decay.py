"""Tests for reward_decay hint penalty."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from brain_assist.reward_decay import (  # noqa: E402
    append_hint,
    apply_reward_decay,
    load_hint_counts,
)


def test_apply_reward_decay_no_hints():
    adjusted, penalty = apply_reward_decay(0.85, 0)
    assert adjusted == 0.85
    assert penalty == 0.0


def test_apply_reward_decay_with_hints():
    adjusted, penalty = apply_reward_decay(0.85, 2, decay_per_hint=0.1)
    assert adjusted == 0.65
    assert penalty == 0.2


def test_apply_reward_decay_floor():
    adjusted, penalty = apply_reward_decay(0.15, 5, decay_per_hint=0.1, floor=0.0)
    assert adjusted == 0.0
    assert penalty == 0.15


def test_load_hint_counts_and_append(tmp_path):
    ledger = tmp_path / "hint_ledger.jsonl"
    append_hint("meta-analysis", session_id="s1", reason="test", ledger_path=ledger)
    append_hint("meta-analysis", hints=2, ledger_path=ledger)
    append_hint("forest-plot", ledger_path=ledger)

    counts = load_hint_counts(ledger_path=ledger)
    assert counts["meta-analysis"] == 3
    assert counts["forest-plot"] == 1

    lines = [json.loads(l) for l in ledger.read_text().strip().split("\n")]
    assert lines[0]["skill_id"] == "meta-analysis"
    assert "ts" in lines[0]
