"""Tests for empirical NotebookLM benchmark validation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(PY_ROOT))

from notebooklm.empirical_validate import run_empirical_validation, validate_claim  # noqa: E402


def test_validate_repo_artifact_verified():
    entry = {
        "id": "TEST",
        "type": "repo_artifact",
        "paths": ["40_operations/python/brain_assist/tgs_rag.py"],
        "symbols": ["tgs_search"],
    }
    result = validate_claim(entry)
    assert result["status"] == "VERIFIED"
    assert result["empirical"] is True


def test_validate_external_benchmark_unverified():
    entry = {
        "id": "EXT",
        "type": "external_benchmark",
        "note": "not in repo",
    }
    result = validate_claim(entry)
    assert result["status"] == "UNVERIFIED"
    assert result["empirical"] is False


def test_run_empirical_validation_registry():
    reg = WORKSPACE / "30_system" / "docs" / "notebooklm_benchmark_registry.json"
    report = run_empirical_validation(reg)
    assert report["summary"]["total"] >= 8
    assert report["summary"]["verified"] >= 5
    assert any(c["id"] == "TGS-IMPL" and c["status"] == "VERIFIED" for c in report["claims"])
