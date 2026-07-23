"""Phase 1 promote and enrich tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "40_operations" / "python"))

from distillation.emit import Action, CaptureRecord, capture  # noqa: E402
from distillation.enrich import enrich_skeleton  # noqa: E402
from distillation.promote import (  # noqa: E402
    promote_trace,
    trace_to_card_markdown,
    validate_promotable,
)


@pytest.mark.unit
def test_validate_rejects_skeleton_pending():
    ok, reason = validate_promotable(
        {"skeleton": True, "enrichment_status": "pending", "context": "x", "reasoning": "y"},
        phi_reviewed_confirm=True,
    )
    assert not ok
    assert "enrich" in reason


@pytest.mark.unit
def test_trace_to_card_has_sections(tmp_path):
    trace = {
        "trace_id": "dtr_test",
        "task_domain": "python",
        "tags": ["tdd"],
        "context": "User asked for tests.",
        "reasoning": "Write pytest first.",
        "actions": [{"tool": "pytest", "intent": "run", "result_summary": "green", "success": True}],
        "outcome": {"success": True, "verification": "pytest"},
    }
    md = trace_to_card_markdown(trace, corpus_path=tmp_path / "card_python_tdd.md")
    assert "## Context" in md
    assert "## Reasoning" in md
    assert "## Action" in md
    assert "## Outcome" in md
    assert "pytest" in md


@pytest.mark.unit
def test_promote_writes_corpus_and_marks_raw(tmp_path, monkeypatch):
    monkeypatch.delenv("DISTILLATION_CAPTURE_DISABLED", raising=False)
    corpus = tmp_path / "corpus"
    record = CaptureRecord(
        context="Implement hybrid distillation hook.",
        reasoning="Hooks lack reasoning text; agent enriches skeletons before promotion.",
        actions=[Action(tool="Write", intent="add hook", result_summary="ok")],
        outcome={"success": True, "verification": "pytest green"},
        task_domain="python",
        tags=["distillation"],
    )
    capture(record, workspace=tmp_path)
    tid = record.to_record()["trace_id"]
    # reload trace_id from file
    raw_dir = tmp_path / ".agent" / "distillation" / "raw"
    tid = json.loads(next(raw_dir.glob("dtr_*.json")).read_text(encoding="utf-8"))["trace_id"]

    out = promote_trace(tid, workspace=tmp_path, phi_reviewed_confirm=True, corpus_dir=corpus)
    assert out.is_file()
    assert "## Reasoning" in out.read_text(encoding="utf-8")
    raw = json.loads((raw_dir / f"{tid}.json").read_text(encoding="utf-8"))
    assert raw["promoted_to"]
    assert raw["phi_reviewed"] is True


@pytest.mark.unit
def test_enrich_supersedes_skeleton(tmp_path, monkeypatch):
    monkeypatch.delenv("DISTILLATION_CAPTURE_DISABLED", raising=False)
    sk = CaptureRecord(
        context="Auto skeleton placeholder.",
        actions=[Action(tool="Grep", success=True)],
        outcome={"success": True},
        task_domain="python",
        tags=["skeleton", "auto_hook"],
        skeleton=True,
        enrichment_status="pending",
    )
    capture(sk, workspace=tmp_path)
    raw_dir = tmp_path / ".agent" / "distillation" / "raw"
    sk_id = json.loads(next(raw_dir.glob("dtr_*.json")).read_text(encoding="utf-8"))["trace_id"]

    enriched = enrich_skeleton(
        sk_id,
        context="Real task context.",
        reasoning="Because hooks only see tool metadata.",
        workspace=tmp_path,
    )
    assert enriched["reasoning"]
    assert enriched.get("skeleton") is not True
    sk_row = json.loads((raw_dir / f"{sk_id}.json").read_text(encoding="utf-8"))
    assert sk_row["enrichment_status"] == "superseded"
    assert sk_row["enriched_trace_id"] == enriched["trace_id"]
