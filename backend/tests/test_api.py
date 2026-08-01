"""HTTP razina: sto klijent stvarno dobije natrag.

Smoke testovi pokrivaju logiku servisa; ovdje provjeravamo da se greske
klijenta prijavljuju kao 4xx, a ne kao 500, i da granica uploada drzi.
"""
from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# BAND_REFS_DIR mora biti postavljen PRIJE importa app.config (mkdir na importu)
_TMP = tempfile.mkdtemp()
os.environ.setdefault("BAND_REFS_DIR", str(Path(_TMP) / "band_refs"))

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover — fastapi nije obavezan za smoke testove
    TestClient = None  # type: ignore[assignment]

from app.config import MAX_UPLOAD_BYTES  # noqa: E402
from app.images import InvalidImage, load_rgb  # noqa: E402


def png_bytes(size: tuple[int, int] = (32, 32)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (120, 90, 60)).save(buf, format="PNG")
    return buf.getvalue()


class ImageGuardTest(unittest.TestCase):
    def test_rejects_non_image(self) -> None:
        with self.assertRaises(InvalidImage):
            load_rgb(b"ovo definitivno nije slika")

    def test_rejects_empty(self) -> None:
        with self.assertRaises(InvalidImage):
            load_rgb(b"")

    def test_accepts_real_image(self) -> None:
        img = load_rgb(png_bytes())
        self.assertEqual(img.mode, "RGB")

    def test_rejects_oversized_pixel_count(self) -> None:
        """Decompression bomb: odbij po dimenzijama, prije alokacije piksela."""
        from app import images

        original = images.MAX_IMAGE_PIXELS
        try:
            images.MAX_IMAGE_PIXELS = 100  # 10x10 px
            with self.assertRaises(InvalidImage):
                images.load_rgb(png_bytes((64, 64)))
        finally:
            images.MAX_IMAGE_PIXELS = original


@unittest.skipIf(TestClient is None, "fastapi nije instaliran")
class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from app.main import app

        cls.client = TestClient(app)

    def test_health_is_cheap_and_does_not_load_models(self) -> None:
        """/health ne smije pokrenuti ucitavanje CLIP-a ni PaddleOCR-a.

        Drugi testovi u paketu vec mogu biti dotakli motore, pa stanje
        eksplicitno vracamo na nulu — inace bi test mjerio redoslijed
        izvrsavanja umjesto ponasanja /health.
        """
        from app import band_service, ocr_service

        band_tried, band_model = band_service._clip_tried, band_service._clip_model
        ocr_tried, ocr_engine = ocr_service._engine_tried, ocr_service._engine
        band_service._clip_tried, band_service._clip_model = False, None
        ocr_service._engine_tried, ocr_service._engine = False, None
        try:
            r = self.client.get("/health")
            self.assertEqual(r.status_code, 200)
            body = r.json()
            self.assertTrue(body["ok"])
            # None = motor jos nije ni pokusan; /health ga ne smije povuci
            self.assertIsNone(body["ocr"]["paddleocr"])
            self.assertIsNone(body["band"]["clip"])
            # i stanje mora ostati netaknuto nakon poziva
            self.assertFalse(band_service._clip_tried)
            self.assertFalse(ocr_service._engine_tried)
        finally:
            band_service._clip_tried, band_service._clip_model = band_tried, band_model
            ocr_service._engine_tried, ocr_service._engine = ocr_tried, ocr_engine

    def test_ocr_rejects_non_image_with_400(self) -> None:
        r = self.client.post("/ocr", files={"file": ("x.png", b"nije slika", "image/png")})
        self.assertEqual(r.status_code, 400)

    def test_ocr_rejects_empty_with_400(self) -> None:
        r = self.client.post("/ocr", files={"file": ("x.png", b"", "image/png")})
        self.assertEqual(r.status_code, 400)

    def test_ocr_accepts_real_image(self) -> None:
        r = self.client.post("/ocr", files={"file": ("x.png", png_bytes(), "image/png")})
        self.assertEqual(r.status_code, 200)
        self.assertIn("engine", r.json())

    def test_upload_over_limit_gets_413(self) -> None:
        blob = b"\0" * (MAX_UPLOAD_BYTES + 1024)
        r = self.client.post("/ocr", files={"file": ("big.png", blob, "image/png")})
        self.assertEqual(r.status_code, 413)

    def test_band_reference_rejects_traversal_id_with_400(self) -> None:
        r = self.client.post(
            "/band/reference",
            data={"cigar_id": ".."},
            files={"file": ("b.png", png_bytes(), "image/png")},
        )
        self.assertEqual(r.status_code, 400)

    def test_band_match_rejects_non_image_with_400(self) -> None:
        r = self.client.post("/band/match", files={"file": ("x.png", b"nope", "image/png")})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
