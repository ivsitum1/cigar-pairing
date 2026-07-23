"""Unit tests for scan detection heuristics (no Paddle dependency)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from pdf_extraction.heuristics import needs_ocr  # noqa: E402


@pytest.mark.unit
def test_needs_ocr_empty():
    assert needs_ocr([]) is True


@pytest.mark.unit
def test_needs_ocr_sparse():
    assert needs_ocr(["a", "b"]) is True


@pytest.mark.unit
def test_needs_ocr_sufficient_text():
    text = " ".join(["word"] * 80)
    pages = [text] * 5
    assert needs_ocr(pages) is False


@pytest.mark.unit
def test_needs_ocr_force_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PADDLE_OCR_FORCE", "1")
    assert needs_ocr(["plenty of text " * 50]) is True
    monkeypatch.delenv("PADDLE_OCR_FORCE", raising=False)
