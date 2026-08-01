"""PaddleOCR wrapper with a lightweight stub when Paddle is not installed."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from PIL import Image

from .images import load_rgb

# Windows / oneDNN PIR crash workaround (ArrayAttribute DoubleAttribute)
os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("FLAGS_onednn", "0")
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

log = logging.getLogger("ocr")

_engine: Any | None = None
_engine_tried = False


@dataclass
class OcrLine:
    text: str
    confidence: float
    box: list[list[float]] | None = None


@dataclass
class OcrResult:
    text: str
    lines: list[OcrLine]
    engine: str


def _load_paddle() -> Any | None:
    global _engine, _engine_tried
    if _engine_tried:
        return _engine
    _engine_tried = True
    try:
        from paddleocr import PaddleOCR  # type: ignore

        # 2.x API (Windows-stable); fall back to 3.x kwargs if needed
        try:
            _engine = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                show_log=False,
            )
        except TypeError:
            _engine = PaddleOCR(
                lang="en",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=True,
            )
        log.info("PaddleOCR loaded (lang=en)")
    except Exception as e:  # noqa: BLE001 — optional dependency
        log.warning("PaddleOCR unavailable (%s); using PIL stub", e)
        _engine = None
    return _engine


def _stub_ocr(image: Image.Image) -> OcrResult:
    """Last-resort when Paddle is not installed — returns empty structured result."""
    _ = image
    return OcrResult(text="", lines=[], engine="stub")


def _lines_from_result_obj(obj: Any) -> list[OcrLine]:
    """Normalize PaddleOCR 3.x Result / dict / classic list payloads."""
    lines: list[OcrLine] = []

    # Classic: [[box, (text, conf)], ...]
    if isinstance(obj, list) and obj and isinstance(obj[0], (list, tuple)):
        page = obj[0] if obj and isinstance(obj[0], list) and obj[0] and isinstance(obj[0][0], (list, tuple)) and len(obj[0][0]) == 2 else obj
        # detect nested page
        if obj and isinstance(obj[0], list) and obj[0] and isinstance(obj[0][0], (list, tuple)):
            first = obj[0][0]
            if len(first) == 2 and not isinstance(first[0], (int, float)):
                page = obj[0]
        for item in page if isinstance(page, list) else []:
            try:
                if not isinstance(item, (list, tuple)) or len(item) < 2:
                    continue
                box, rec = item[0], item[1]
                if isinstance(rec, (list, tuple)):
                    text = str(rec[0]).strip()
                    conf = float(rec[1]) if len(rec) > 1 else 0.0
                else:
                    text = str(rec).strip()
                    conf = 0.0
                if not text:
                    continue
                box_out = None
                if box is not None and hasattr(box, "__iter__"):
                    try:
                        box_out = [[float(p[0]), float(p[1])] for p in box]
                    except (TypeError, ValueError, IndexError):
                        box_out = None
                lines.append(OcrLine(text=text, confidence=conf, box=box_out))
            except (IndexError, TypeError, ValueError):
                continue
        return lines

    # PaddleX / OCR 3 result object with attributes or dict
    data: dict[str, Any] = {}
    if isinstance(obj, dict):
        data = obj
    else:
        for key in ("rec_texts", "rec_scores", "dt_polys", "texts", "scores"):
            if hasattr(obj, key):
                data[key] = getattr(obj, key)
        if hasattr(obj, "json") and callable(obj.json):
            try:
                data = {**data, **(obj.json() or {})}
            except Exception:  # noqa: BLE001
                pass
        if hasattr(obj, "keys") and callable(obj.keys):
            try:
                data = {**data, **dict(obj)}
            except Exception:  # noqa: BLE001
                pass

    texts = data.get("rec_texts") or data.get("texts") or []
    scores = data.get("rec_scores") or data.get("scores") or []
    polys = data.get("dt_polys") or data.get("rec_polys") or []
    for i, t in enumerate(texts):
        text = str(t).strip()
        if not text:
            continue
        conf = float(scores[i]) if i < len(scores) else 0.0
        box_out = None
        if i < len(polys):
            try:
                poly = polys[i]
                box_out = [[float(p[0]), float(p[1])] for p in poly]
            except (TypeError, ValueError, IndexError):
                box_out = None
        lines.append(OcrLine(text=text, confidence=conf, box=box_out))
    return lines


def _parse_paddle_payload(raw: Any) -> OcrResult:
    lines: list[OcrLine] = []
    if raw is None:
        return OcrResult(text="", lines=[], engine="paddleocr")

    # predict() often returns list of result objects
    if isinstance(raw, list):
        for item in raw:
            lines.extend(_lines_from_result_obj(item))
        if not lines:
            lines = _lines_from_result_obj(raw)
    else:
        lines = _lines_from_result_obj(raw)

    text = "\n".join(l.text for l in lines if l.text)
    return OcrResult(text=text, lines=lines, engine="paddleocr")


def recognize_image_bytes(data: bytes) -> OcrResult:
    image = load_rgb(data)
    engine = _load_paddle()
    if engine is None:
        return _stub_ocr(image)

    import numpy as np

    arr = np.array(image)
    try:
        if hasattr(engine, "ocr"):
            try:
                raw = engine.ocr(arr, cls=True)
            except TypeError:
                raw = engine.ocr(arr)
        elif hasattr(engine, "predict"):
            raw = engine.predict(arr)
        else:
            return _stub_ocr(image)
        return _parse_paddle_payload(raw)
    except Exception as e:  # noqa: BLE001
        log.exception("PaddleOCR failed: %s", e)
        return _stub_ocr(image)


def engine_status() -> dict[str, Any]:
    """Jeftin status za /health — ne ucitava PaddleOCR.

    Ranije je zvao `_load_paddle()`, pa je prvi health check povlacio cijeli
    OCR stack. Motor se ucitava lijeno na prvi stvarni `/ocr` poziv.
    """
    return {
        # None = jos nismo ni pokusali ucitati motor
        "paddleocr": (_engine is not None) if _engine_tried else None,
        "image_ttl": "request-scoped; not persisted",
    }
