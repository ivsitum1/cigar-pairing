"""Runtime config for the OCR API."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BAND_DIR = Path(os.environ.get("BAND_REFS_DIR", ROOT / "data" / "band_refs"))
BAND_DIR.mkdir(parents=True, exist_ok=True)

# Images are held only in memory during a request; no OCR payload persistence.
IMAGE_TTL_HINT = "request-scoped; not persisted"

CORS_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,capacitor://localhost,http://localhost",
    ).split(",")
    if o.strip()
]

HOST = os.environ.get("OCR_HOST", "0.0.0.0")
PORT = int(os.environ.get("OCR_PORT", "8787"))
