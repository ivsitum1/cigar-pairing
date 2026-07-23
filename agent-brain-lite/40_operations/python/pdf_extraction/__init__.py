"""PDF text extraction with PyPDF2 and optional PaddleOCR (PP-StructureV3)."""

from .heuristics import needs_ocr
from .paddle_ppstructure import (
    CONTENT_NOTE_PADDLE,
    extract_document_pages,
    get_last_content_note,
    is_paddle_available,
)
from .pymupdf_fallback import CONTENT_NOTE_PADDLE_RASTER

PADDLE_CONTENT_NOTES = frozenset(
    {CONTENT_NOTE_PADDLE, CONTENT_NOTE_PADDLE_RASTER}
)

__all__ = [
    "CONTENT_NOTE_PADDLE",
    "CONTENT_NOTE_PADDLE_RASTER",
    "PADDLE_CONTENT_NOTES",
    "extract_document_pages",
    "get_last_content_note",
    "is_paddle_available",
    "needs_ocr",
]
