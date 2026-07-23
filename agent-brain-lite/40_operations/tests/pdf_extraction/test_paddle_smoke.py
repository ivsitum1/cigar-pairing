"""Smoke tests for PaddleOCR import (skipped when not installed)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "40_operations" / "python"))

from pdf_extraction.paddle_ppstructure import is_paddle_available  # noqa: E402


@pytest.mark.ocr
def test_paddle_import_probe():
    if not is_paddle_available():
        pytest.skip("PaddleOCR not installed; run install_paddle_ocr.py")
    from paddleocr import PPStructureV3  # noqa: F401

    import paddle
    from pdf_extraction.device import PADDLEPADDLE_VERSION

    ver = getattr(paddle, "__version__", "")
    assert ver.startswith("3.2."), f"expected PaddlePaddle 3.2.x, got {ver!r}"
    assert PADDLEPADDLE_VERSION.startswith("3.2.")
