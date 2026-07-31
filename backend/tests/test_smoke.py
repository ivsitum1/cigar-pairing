"""Smoke tests for OCR API helpers (no Paddle required)."""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import band_service, ocr_service  # noqa: E402


class OcrSmokeTest(unittest.TestCase):
    def test_ocr_returns_shape(self) -> None:
        buf = io.BytesIO()
        Image.new("RGB", (64, 64), color=(40, 30, 20)).save(buf, format="JPEG")
        result = ocr_service.recognize_image_bytes(buf.getvalue())
        self.assertTrue(hasattr(result, "text"))
        self.assertTrue(hasattr(result, "lines"))
        self.assertIn(result.engine, ("paddleocr", "stub"))

    def test_band_reference_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            band_service.BAND_DIR = Path(tmp)  # type: ignore[misc]
            buf = io.BytesIO()
            Image.new("RGB", (48, 48), color=(200, 160, 40)).save(buf, format="JPEG")
            data = buf.getvalue()
            meta = band_service.add_reference("cig-demo", data)
            self.assertTrue(meta["ref_id"])
            hits = band_service.match_image(data, top_k=3)
            self.assertTrue(hits)
            self.assertEqual(hits[0].cigar_id, "cig-demo")
            self.assertGreater(hits[0].score, 0.5)


if __name__ == "__main__":
    unittest.main()
