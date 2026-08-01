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

# Svaki upload se cita cijeli u memoriju (`await file.read()`), a servis se
# prema READMEu vrti na 0.0.0.0 zbog Android APK-a — bez gornje granice jedan
# veliki POST ga sruSi. 12 MB je s viskom za fotografiju racuna s mobitela.
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(12 * 1024 * 1024)))

# PIL-ov ugradeni prag (~178 Mpx) upozorava, ali ne odbija dovoljno rano za
# "decompression bomb" — mala datoteka koja se raspakira u gigabajte piksela.
MAX_IMAGE_PIXELS = int(os.environ.get("MAX_IMAGE_PIXELS", str(50_000_000)))

# Zajednicki token. Prazno = bez provjere (lokalni razvoj na 127.0.0.1).
# Cim se servis vezuje na 0.0.0.0 zbog APK-a, postavi ga: bez njega svatko na
# istoj mrezi moze pisati reference i nabrajati ih.
API_TOKEN = os.environ.get("OCR_API_TOKEN", "").strip()
