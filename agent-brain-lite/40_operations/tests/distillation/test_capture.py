"""Phase 0 distillation capture: cleaning, PHI-scrub, and landing behaviour.

Verifies the notebook's step-1 (capture) + step-2 (clean) contract:
- terminal noise (ANSI, rate-limit lines, box chrome, BOM) is stripped;
- obvious identifiers are redacted and flagged for review;
- a clean trace is promotable, a PHI-hit trace is not;
- capture writes the Context→Reasoning→Action→Outcome record to a raw log.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "40_operations" / "python"))

from distillation.clean import clean_text, scrub_phi  # noqa: E402
from distillation.emit import Action, CaptureRecord, capture  # noqa: E402


@pytest.mark.unit
def test_clean_strips_ansi_ratelimit_bom_and_box():
    raw = (
        "﻿\x1b[32mRunning tests\x1b[0m\n"
        "Rate limit exceeded, retrying after 5s\n"
        "├─────────────┤\n"
        "12 passed in 0.4s\n"
    )
    cleaned = clean_text(raw)
    assert "﻿" not in cleaned
    assert "\x1b" not in cleaned
    assert "Rate limit" not in cleaned
    assert "├" not in cleaned
    assert "Running tests" in cleaned
    assert "12 passed in 0.4s" in cleaned


@pytest.mark.unit
def test_scrub_redacts_and_reports_categories():
    text = "Contact dr@hospital.org about MRN 12345678 seen 1980-04-12."
    scrubbed, hits = scrub_phi(text)
    assert "dr@hospital.org" not in scrubbed
    assert "12345678" not in scrubbed
    assert "1980-04-12" not in scrubbed
    assert set(hits) >= {"email", "long_digits", "date"}


@pytest.mark.unit
def test_clean_trace_is_promotable():
    _, hits = scrub_phi(clean_text("Fit a GLM and report the odds ratio with 95% CI."))
    assert hits == []


@pytest.mark.unit
def test_capture_writes_cra_record(tmp_path, monkeypatch):
    monkeypatch.delenv("DISTILLATION_CAPTURE_DISABLED", raising=False)
    record = CaptureRecord(
        context="\x1b[1mUser asks for a robust SE on a logistic model.\x1b[0m",
        reasoning="Prefer HC3 for small samples; statsmodels supports cov_type='HC3'.",
        actions=[Action(tool="Bash", intent="run statsmodels fit", result_summary="converged, OR=1.8")],
        outcome={"success": True, "verification": "pytest green; OR matches hand calc"},
        task_domain="biostatistics",
        tags=["glm", "robust-se"],
    )
    log_path = capture(record, workspace=tmp_path)

    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["schema_version"] == 1
    assert "\x1b" not in row["context"]
    assert row["task_domain"] == "biostatistics"
    assert row["actions"][0]["tool"] == "Bash"
    assert row["outcome"]["success"] is True
    assert row["promotable"] is True
    # A per-trace file is also written next to the log.
    assert (tmp_path / ".agent" / "distillation" / "raw" / f"{row['trace_id']}.json").exists()


@pytest.mark.unit
def test_to_record_trace_id_stable():
    record = CaptureRecord(context="same id on repeat", reasoning="test")
    a = record.to_record()
    b = record.to_record()
    assert a["trace_id"] == b["trace_id"]
    assert a["ts"] == b["ts"]


@pytest.mark.unit
def test_capture_flags_phi_trace_not_promotable(tmp_path):
    record = CaptureRecord(
        context="Patient email jane.doe@mail.com, MRN 55512345, presented today.",
        reasoning="Summarise the encounter.",
        outcome={"success": True},
    )
    capture(record, workspace=tmp_path)
    row = json.loads(
        (tmp_path / ".agent" / "distillation" / "raw" / "traces.jsonl").read_text(encoding="utf-8").strip()
    )
    assert row["promotable"] is False
    assert row["phi_reviewed"] is False
    assert "jane.doe@mail.com" not in json.dumps(row)
