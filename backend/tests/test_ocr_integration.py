"""Full-stack PaddleOCR inference — not the HTTP/mock path.

Skipped when the pinned paddle stack is not installed (local lightweight runs).
CI installs backend/requirements.txt and must not skip.
"""
from __future__ import annotations

import io
import os
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import ocr_service  # noqa: E402


_CI = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"


def _paddle_stack_installed() -> bool:
    try:
        import paddle  # noqa: F401
        import paddleocr  # noqa: F401
        import scipy  # noqa: F401 — declared in requirements.txt

        return True
    except ImportError:
        return False


def _skip_integration_class() -> bool:
    """Local dev may omit the heavy stack; CI must never skip silently."""
    if _CI:
        return False
    return not _paddle_stack_installed()


def _synthetic_label_image(text: str = "CIGAR 42") -> bytes:
    """Non-sensitive fixture: high-contrast label for smoke OCR."""
    img = Image.new("RGB", (320, 80), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except OSError:
        font = ImageFont.load_default()
    draw.text((12, 18), text, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@unittest.skipIf(_skip_integration_class(), "paddleocr stack not installed (local only)")
class PaddleOcrIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if _CI and not _paddle_stack_installed():
            raise AssertionError(
                "CI installed backend/requirements.txt but paddle/paddleocr/scipy "
                "did not import — fix the stack, do not skip OCR proof."
            )
        ocr_service._engine = None  # type: ignore[attr-defined]
        ocr_service._engine_tried = False  # type: ignore[attr-defined]

    def test_requirements_import_surface(self) -> None:
        import fastapi  # noqa: F401
        import httpx  # noqa: F401
        import imagehash  # noqa: F401
        import python_multipart  # noqa: F401
        import numpy  # noqa: F401
        import scipy  # noqa: F401
        import uvicorn  # noqa: F401
        from paddleocr import PaddleOCR  # noqa: F401

        import paddle

        self.assertTrue(getattr(paddle, "__version__", ""))
        self.assertGreaterEqual(tuple(int(x) for x in numpy.__version__.split(".")[:2]), (2, 0))

    def test_paddle_inference_not_stub(self) -> None:
        ocr_service._engine = None  # type: ignore[attr-defined]
        ocr_service._engine_tried = False  # type: ignore[attr-defined]

        data = _synthetic_label_image()
        result = ocr_service.recognize_image_bytes(data)
        self.assertEqual(
            result.engine,
            "paddleocr",
            "expected live PaddleOCR, got stub — is the full requirements stack installed?",
        )
        self.assertIsInstance(result.text, str)
        self.assertIsInstance(result.lines, list)
        # PaddleOCR 3 should still read a high-contrast synthetic label.
        joined = result.text.upper().replace(" ", "")
        self.assertIn(
            "CIGAR",
            joined,
            f"expected readable text from inference, got {result.text!r}",
        )

    def test_http_ocr_route_uses_paddle_engine(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        ocr_service._engine = None  # type: ignore[attr-defined]
        ocr_service._engine_tried = False  # type: ignore[attr-defined]

        client = TestClient(app)
        data = _synthetic_label_image("ROUTE 99")
        r = client.post(
            "/ocr",
            files={"file": ("label.png", data, "image/png")},
        )
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertEqual(body["engine"], "paddleocr")
        self.assertIn("ROUTE", body.get("text", "").upper().replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
