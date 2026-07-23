"""PyMuPDF raster + per-page OCR when Paddle PDFium cannot load the file."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Callable

from .heuristics import MIN_CHARS_PER_PAGE

CONTENT_NOTE_PADDLE_RASTER = "paddleocr_ppstructurev3_pymupdf_raster"


def is_pdf_header(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(5) == b"%PDF-"
    except OSError:
        return False


def classify_local_pdf(path: Path) -> str:
    """
    Rough file class for retry routing.

    Returns: pdf_ok | placeholder | html | empty_pdf | missing
    """
    if not path.is_file():
        return "missing"
    if not is_pdf_header(path):
        head = path.read_bytes()[:32].lower()
        if head.startswith(b"<!doctype") or head.startswith(b"<html"):
            return "html"
        return "placeholder"
    try:
        import fitz

        doc = fitz.open(path)
        n = doc.page_count
        doc.close()
        if n == 0:
            return "empty_pdf"
    except Exception:
        return "corrupt_pdf"
    return "pdf_ok"


def paddle_error_needs_raster(err: str | None) -> bool:
    if not err:
        return False
    needles = (
        "PDFium",
        "Data format error",
        "Failed to load document",
        "Failed to load page",
        "Unable to allocate",
        "out of memory",
        "MemoryError",
    )
    low = err.lower()
    return any(n.lower() in low for n in needles)


def extract_document_pages_raster(
    path: Path,
    *,
    pipeline_factory: Callable[[], Any],
    ocr_image_fn: Callable[[Any, Path], str | None],
    read_markdown_pages_fn: Callable[[Path], list[str]],
) -> tuple[list[str], int, str | None]:
    """
    Open PDF with PyMuPDF; use embedded text when dense enough, else raster + OCR per page.
    """
    try:
        import fitz
    except ImportError as e:
        return [], 0, f"pymupdf not installed: {e}"

    path = path.resolve()
    if not path.is_file():
        return [], 0, f"file not found: {path}"

    dpi = float(os.environ.get("PADDLE_OCR_RASTER_DPI", "150"))
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    max_pages = int(os.environ.get("PADDLE_OCR_RASTER_MAX_PAGES", "0"))

    try:
        pipeline = pipeline_factory()
    except RuntimeError as e:
        return [], 0, str(e)

    page_texts: list[str] = []
    try:
        doc = fitz.open(path)
    except Exception as e:
        return [], 0, f"pymupdf open: {e}"

    try:
        total = doc.page_count
        if total == 0:
            return [], 0, "pymupdf: document has 0 pages"
        limit = total if max_pages <= 0 else min(total, max_pages)

        for i in range(limit):
            page = doc[i]
            plain = (page.get_text("text") or "").strip()
            if len(plain) >= MIN_CHARS_PER_PAGE:
                page_texts.append(plain)
                continue

            try:
                with tempfile.TemporaryDirectory(prefix="paddle_raster_") as tmp:
                    img = Path(tmp) / f"page_{i:05d}.png"
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    pix.save(str(img))
                    inline = ocr_image_fn(pipeline, img)
                    if inline:
                        page_texts.append(inline)
                        continue
                    md_pages = read_markdown_pages_fn(Path(tmp))
                    if md_pages:
                        page_texts.append(md_pages[-1])
                    else:
                        page_texts.append("")
            except Exception as e:
                page_texts.append(f"\n_[Raster OCR failed on page {i + 1}: {e}]_\n")

        if max_pages > 0 and total > max_pages:
            page_texts.append(
                f"\n_[Raster OCR stopped at {max_pages}/{total} pages; "
                f"set PADDLE_OCR_RASTER_MAX_PAGES=0 for full document]_\n"
            )
    finally:
        doc.close()

    if not any(t.strip() for t in page_texts):
        return [], len(page_texts), "pymupdf raster: no text extracted"
    return page_texts, len(page_texts), None
