"""PP-StructureV3 document OCR (PDF/images) via vendored PaddleOCR."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .device import resolve_paddle_device
from .pymupdf_fallback import (
    CONTENT_NOTE_PADDLE_RASTER,
    extract_document_pages_raster,
    paddle_error_needs_raster,
)

CONTENT_NOTE_PADDLE = "paddleocr_ppstructurev3"

# Set by last extract_document_pages call (direct or raster fallback).
_last_content_note: str = CONTENT_NOTE_PADDLE


def get_last_content_note() -> str:
    return _last_content_note


def _configure_paddle_runtime() -> None:
    """Avoid oneDNN/mkldnn PIR errors on some Windows CPU builds."""
    os.environ.setdefault("FLAGS_use_mkldnn", "0")
    os.environ.setdefault("FLAGS_use_onednn", "0")
    os.environ.setdefault("FLAGS_enable_mkldnn", "0")

_pipeline: Any = None
_import_error: str | None = None


def is_paddle_available() -> bool:
    """True if paddleocr PPStructureV3 can be imported."""
    _ensure_import_probe()
    return _import_error is None


def _ensure_import_probe() -> None:
    global _import_error
    if _import_error is not None:
        return
    _configure_paddle_runtime()
    try:
        from paddleocr import PPStructureV3  # noqa: F401
    except Exception as e:
        _import_error = str(e)


def _get_pipeline() -> Any:
    global _pipeline, _import_error
    if _pipeline is not None:
        return _pipeline
    _configure_paddle_runtime()
    try:
        from paddleocr import PPStructureV3
    except Exception as e:
        _import_error = str(e)
        raise RuntimeError(
            "PaddleOCR not installed. Run: python 40_operations/scripts/install_paddle_ocr.py"
        ) from e

    lang = os.environ.get("PADDLE_OCR_LANG", "en")
    device = resolve_paddle_device()
    use_gpu = device == "gpu"

    _pipeline = PPStructureV3(
        lang=lang,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_formula_recognition=False,
        engine="paddle",
        device="gpu:0" if use_gpu else "cpu",
        enable_mkldnn=False,
    )
    return _pipeline


def _read_markdown_pages(out_dir: Path) -> list[str]:
    md_files = sorted(out_dir.rglob("*.md"))
    if not md_files:
        return []

    pages: list[str] = []
    for md in md_files:
        text = md.read_text(encoding="utf-8", errors="replace").strip()
        if text:
            pages.append(text)

    if len(pages) <= 1:
        return pages

    # Single concatenated export: try split on common page headers
    combined = "\n\n".join(pages)
    parts = re.split(r"\n(?=#{1,3}\s*Page\s+\d+)", combined, flags=re.IGNORECASE)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]
    return pages


def _text_from_result_obj(res: Any) -> str | None:
    """Best-effort plain text from a predict() result object."""
    for attr in ("markdown", "md", "text"):
        val = getattr(res, attr, None)
        if isinstance(val, str) and val.strip():
            return val.strip()
    data = getattr(res, "res", None) or getattr(res, "data", None)
    if isinstance(data, dict):
        for key in ("markdown", "md", "rec_texts"):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
            if key == "rec_texts" and isinstance(val, list):
                joined = "\n".join(str(x) for x in val if x)
                if joined.strip():
                    return joined.strip()
    return None


def _ocr_image_path(pipeline: Any, img_path: Path) -> str | None:
    """Run PP-Structure on a single page image."""
    out_dir = img_path.parent / "ocr_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = pipeline.predict(input=str(img_path))
    if outputs is None:
        outputs = []
    for res in outputs:
        inline = _text_from_result_obj(res)
        if inline:
            return inline
        if hasattr(res, "save_to_markdown"):
            res.save_to_markdown(save_path=str(out_dir))
        elif hasattr(res, "save_to_json"):
            res.save_to_json(save_path=str(out_dir))
    md_pages = _read_markdown_pages(out_dir)
    if md_pages:
        return "\n\n".join(md_pages)
    return None


def _raster_fallback_enabled() -> bool:
    v = os.environ.get("PADDLE_OCR_RASTER_FALLBACK", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def extract_document_pages(path: Path) -> tuple[list[str], int, str | None]:
    """
    OCR a PDF or image; return (page_texts, page_count, error_message).

    page_texts align with ## Page N sections in downstream markdown writer.
    """
    global _last_content_note
    _last_content_note = CONTENT_NOTE_PADDLE

    path = path.resolve()
    if not path.is_file():
        return [], 0, f"file not found: {path}"

    try:
        pipeline = _get_pipeline()
    except RuntimeError as e:
        return [], 0, str(e)

    page_texts: list[str] = []
    direct_err: str | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="paddleocr_") as tmp:
            out_dir = Path(tmp) / "out"
            out_dir.mkdir(parents=True, exist_ok=True)
            outputs = pipeline.predict(input=str(path))
            if outputs is None:
                outputs = []

            for res in outputs:
                inline = _text_from_result_obj(res)
                if inline:
                    page_texts.append(inline)
                    continue
                if hasattr(res, "save_to_markdown"):
                    res.save_to_markdown(save_path=str(out_dir))
                elif hasattr(res, "save_to_json"):
                    res.save_to_json(save_path=str(out_dir))

            if not page_texts:
                page_texts = _read_markdown_pages(out_dir)

        if not page_texts:
            direct_err = "PaddleOCR produced no text"
    except Exception as e:
        direct_err = f"paddleocr: {e}"

    if page_texts and not direct_err:
        return page_texts, len(page_texts), None

    if _raster_fallback_enabled() and paddle_error_needs_raster(direct_err):
        raster_texts, raster_n, raster_err = extract_document_pages_raster(
            path,
            pipeline_factory=_get_pipeline,
            ocr_image_fn=_ocr_image_path,
            read_markdown_pages_fn=_read_markdown_pages,
        )
        if raster_texts and not raster_err:
            _last_content_note = CONTENT_NOTE_PADDLE_RASTER
            return raster_texts, raster_n, None
        if raster_err:
            return [], 0, raster_err

    if direct_err:
        return [], 0, direct_err
    return [], 0, "PaddleOCR produced no text"
