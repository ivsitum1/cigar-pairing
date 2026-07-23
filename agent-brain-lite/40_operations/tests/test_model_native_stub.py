"""Tests for model-native stub validator."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

WORKSPACE = Path(__file__).resolve().parents[2]
PRD = WORKSPACE / "30_system" / "docs" / "prd_geometry_incorporation.json"


def test_prd_exists_and_has_verification_protocol():
    assert PRD.is_file()
    data = json.loads(PRD.read_text(encoding="utf-8"))
    assert "verification_protocol" in data
    assert "VERIFIED" in data["verification_protocol"]["claim_statuses"]
