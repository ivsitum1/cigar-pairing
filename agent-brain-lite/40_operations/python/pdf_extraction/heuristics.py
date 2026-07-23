"""Heuristics for when PyPDF2 output is insufficient (scan-only PDFs)."""

from __future__ import annotations

import os

MIN_TOTAL_CHARS = int(os.environ.get("PADDLE_OCR_MIN_TOTAL_CHARS", "200"))
MIN_CHARS_PER_PAGE = int(os.environ.get("PADDLE_OCR_MIN_CHARS_PER_PAGE", "30"))


def needs_ocr(page_texts: list[str]) -> bool:
    """
    True when embedded text layer is missing or too sparse for search/RAG.

    Skips OCR when PADDLE_OCR_FORCE=1 (caller should route to Paddle directly).
    """
    if os.environ.get("PADDLE_OCR_FORCE", "").strip() in ("1", "true", "yes"):
        return True

    if not page_texts:
        return True

    stripped = [t.strip() for t in page_texts]
    total = sum(len(t) for t in stripped)
    if total < MIN_TOTAL_CHARS:
        return True

    n = max(len(stripped), 1)
    if total / n < MIN_CHARS_PER_PAGE:
        return True

    return False
