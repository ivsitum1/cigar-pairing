"""Tests for SkillLens dual registry + Rcml training registry (v2)."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

pytest.importorskip("sklearn")

from brain_assist.dual_registry_evolve import (  # noqa: E402
    apply_rewrite_proposal,
    evolve_verifier_from_gap,
    propose_skill_rewrite,
)
from brain_assist.rcml_registry import (  # noqa: E402
    detect_relation_tag,
    export_contrastive_jsonl,
    export_instruction_jsonl,
    load_rcml_registry,
)
from brain_assist.skill_verifier import verify_bundle, verify_skill  # noqa: E402
from brain_assist.verifier_registry import load_verifier_registry, save_verifier_registry  # noqa: E402


def test_detect_relation_causality():
    assert detect_relation_tag("fix regression root cause in skill verifier") == "causality"


def test_rcml_export_non_empty():
    reg = load_rcml_registry()
    assert len(export_contrastive_jsonl(reg)) >= 5
    assert len(export_instruction_jsonl(reg)) >= 5


def test_verifier_rewrite_when_pending():
    reg = load_verifier_registry()
    reg["pending_rewrites"] = [{"skill_id": "meta-analysis", "status": "pending"}]
    decision = verify_skill(
        "meta-analysis forest plot",
        {
            "id": "meta-analysis",
            "score": 0.08,
            "triggers": ["meta-analysis", "forest plot"],
            "granularity": "procedure",
        },
        verifier_reg=reg,
        pending_rewrites={"meta-analysis"},
    )
    assert decision["action"] == "REWRITE"


def test_verify_bundle_includes_relation_tag():
    result = verify_bundle("fix bug root cause in imports", dag_mode=False, top_k=3)
    assert result.get("relation_tag") == "causality"


def test_evolve_verifier_tightens_threshold():
    reg = load_verifier_registry()
    before = json.loads(json.dumps(reg))
    updated = evolve_verifier_from_gap(reg, skill_id="meta-analysis", gap_type="tool_failure")
    pol = next(p for p in updated["skill_policies"] if p["skill_id"] == "meta-analysis")
    old = next(
        (p.get("accept_score", 0.12) for p in before.get("skill_policies") or [] if p.get("skill_id") == "meta-analysis"),
        0.12,
    )
    assert pol["accept_score"] <= old
    assert updated["evolution_log"]


def test_propose_and_apply_rewrite(tmp_path: Path, monkeypatch):
    skill_src = REPO / "30_system" / "SKILLS" / "SKILL_meta-analysis.md"
    original = skill_src.read_text(encoding="utf-8")
    proposals = tmp_path / "proposals"
    proposals.mkdir()
    monkeypatch.setattr(
        "brain_assist.dual_registry_evolve.PROPOSALS_DIR",
        proposals,
    )
    monkeypatch.setattr(
        "brain_assist.dual_registry_evolve.SKILLS_DIR",
        REPO / "30_system" / "SKILLS",
    )
    proposal = propose_skill_rewrite(
        "meta-analysis",
        failure_text="Used wrong test",
        correction_text="Always Welch t-test by default",
    )
    assert proposal["proposal_id"]
    result = apply_rewrite_proposal(Path(proposal["proposal_path"]), dry_run=True)
    assert result["ok"]
    try:
        apply_rewrite_proposal(Path(proposal["proposal_path"]), dry_run=False)
        updated = skill_src.read_text(encoding="utf-8")
        assert "Gap-driven amendment" in updated
    finally:
        skill_src.write_text(original, encoding="utf-8")


def test_verifier_registry_validate_script():
    import subprocess

    r = subprocess.run(
        [sys.executable, str(REPO / "40_operations" / "scripts" / "verifier_registry_validate.py")],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert r.returncode == 0, r.stderr
