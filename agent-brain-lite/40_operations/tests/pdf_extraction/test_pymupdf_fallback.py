"""Unit tests for OCR gap routing helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from pdf_extraction.pymupdf_fallback import (  # noqa: E402
    classify_local_pdf,
    is_pdf_header,
    paddle_error_needs_raster,
)


def test_is_pdf_header(tmp_path: Path) -> None:
    p = tmp_path / "ok.pdf"
    p.write_bytes(b"%PDF-1.4\n")
    assert is_pdf_header(p) is True
    html = tmp_path / "fake.pdf"
    html.write_text("<!DOCTYPE html>", encoding="utf-8")
    assert is_pdf_header(html) is False


def test_classify_html_as_pdf(tmp_path: Path) -> None:
    p = tmp_path / "g.pdf"
    p.write_text("<!DOCTYPE html><html></html>", encoding="utf-8")
    assert classify_local_pdf(p) == "html"


@pytest.mark.parametrize(
    "msg",
    [
        "paddleocr: Failed to load document (PDFium: Data format error).",
        "paddleocr: Unable to allocate 70.7 MiB",
        "Failed to load page.",
    ],
)
def test_paddle_error_needs_raster(msg: str) -> None:
    assert paddle_error_needs_raster(msg) is True


def test_paddle_error_no_raster_for_none() -> None:
    assert paddle_error_needs_raster(None) is False
    assert paddle_error_needs_raster("encrypted") is False
