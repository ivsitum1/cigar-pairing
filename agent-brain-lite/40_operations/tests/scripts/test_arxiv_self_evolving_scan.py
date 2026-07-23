"""Tests for arxiv_self_evolving_scan sensor."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "40_operations" / "scripts"))

import arxiv_self_evolving_scan as scan  # noqa: E402


@pytest.mark.unit
def test_in_window():
    assert scan.in_window("2026-07-05", date(2026, 7, 1), date(2026, 7, 7))
    assert not scan.in_window("2026-06-30", date(2026, 7, 1), date(2026, 7, 7))


@pytest.mark.unit
def test_build_payload_flags_new_hits():
    registry_ids = {"2607.00871"}
    hits = [
        {"id": "2607.00871", "published": "2026-07-01", "title": "Known", "url": "https://arxiv.org/abs/2607.00871"},
        {"id": "2607.09999", "published": "2026-07-04", "title": "Fresh", "url": "https://arxiv.org/abs/2607.09999"},
    ]
    payload = scan.build_payload(
        period="weekly",
        label="2026-W27",
        start=date(2026, 7, 1),
        end=date(2026, 7, 7),
        hits=hits,
        registry_ids=registry_ids,
        dry_run=False,
    )
    assert len(payload["hits_in_window"]) == 2
    assert [h["id"] for h in payload["new_hits"]] == ["2607.09999"]


@pytest.mark.unit
def test_dry_run_weekly_cli(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["arxiv_self_evolving_scan.py", "--period", "weekly", "--dry-run"])
    assert scan.main() == 0
    assert "Period: weekly" in capsys.readouterr().out
