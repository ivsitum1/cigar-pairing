"""Tests for author_claims_gate (brain vs project scope)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from brain_assist.author_claims_gate import (  # noqa: E402
    check_text,
    gate_before_retry,
    list_project_packs,
)


def test_brain_only_clean_text_passes():
    text = "Dexmedetomidine is commonly used during ECMO; titration follows institutional protocol."
    assert check_text(text) == []
    assert gate_before_retry(text)["allow_retry"] is True


def test_ecmo_dex_first_line_not_blocked_without_project():
    text = "Dexmedetomidin je univerzalni prvi izbor na ECMO-u za sedaciju."
    assert check_text(text) == []
    assert gate_before_retry(text)["allow_retry"] is True


def test_ecmo_dex_first_line_blocked_with_project():
    text = "Dexmedetomidin je univerzalni prvi izbor na ECMO-u za sedaciju."
    hits = check_text(text, project_id="sedacija-ecmo")
    assert any(h.rule_id == "CLIN-ECMO-DEX-FIRST" for h in hits)
    assert hits[0].scope == "project:sedacija-ecmo"
    assert gate_before_retry(text, project_id="sedacija-ecmo")["allow_retry"] is False


def test_em_dash_writing_violation_brain_scope():
    text = "Rezultati su bili značajni — razlika je opipljiva."
    hits = check_text(text, categories=["writing"])
    assert any(h.rule_id == "WRIT-EM-DASH" for h in hits)
    assert hits[0].scope == "brain"


def test_list_project_packs_includes_sedacija_ecmo():
    packs = list_project_packs()
    assert "sedacija-ecmo" in packs
