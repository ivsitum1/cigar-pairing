"""Tests for policy invariance rubric stability."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "python"
sys.path.insert(0, str(ROOT))

from brain_assist.policy_invariance import evaluate_invariance, paraphrase_rubric  # noqa: E402


def test_paraphrase_generates_variants() -> None:
    variants = paraphrase_rubric("You must never delete files without confirmation.")
    assert len(variants) >= 2


def test_stable_verdicts() -> None:
    r = evaluate_invariance([True, True, True])
    assert r.stable
    assert r.flip_rate == 0.0


def test_unstable_verdicts() -> None:
    r = evaluate_invariance([True, False, True])
    assert not r.stable
    assert r.flip_rate > 0.25
