"""FastAPI OCR + band-matching service."""
from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import band_service, ocr_service
from .config import CORS_ORIGINS, IMAGE_TTL_HINT, MAX_UPLOAD_BYTES
from .images import InvalidImage

app = FastAPI(title="cigar-pairing-ocr", version="0.1.0")


async def read_upload(file: UploadFile) -> bytes:
    """Procitaj upload uz gornju granicu.

    `await file.read()` bez granice cita cijeli body u memoriju, a servis se
    prema READMEu vrti na 0.0.0.0 — jedan veliki POST bi ga srusio. Citamo u
    komadima da odbijemo prevelik sadrzaj prije nego ga cijelog primimo.
    """
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(1 << 20)  # 1 MiB
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise HTTPException(
                413, f"file too large (limit {MAX_UPLOAD_BYTES} bytes)"
            )
        chunks.append(chunk)
    if total == 0:
        raise HTTPException(400, "empty file")
    return b"".join(chunks)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "ocr": ocr_service.engine_status(),
        "band": band_service.band_status(),
        "image_ttl": IMAGE_TTL_HINT,
    }


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)) -> dict:
    data = await read_upload(file)
    # request-scoped only — no disk write of the upload
    try:
        result = ocr_service.recognize_image_bytes(data)
    except InvalidImage as e:
        raise HTTPException(400, str(e)) from e
    return {
        "text": result.text,
        "lines": [
            {"text": l.text, "confidence": l.confidence, "box": l.box}
            for l in result.lines
        ],
        "engine": result.engine,
    }


@app.post("/band/reference")
async def band_reference(
    cigar_id: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    data = await read_upload(file)
    try:
        return band_service.add_reference(cigar_id, data)
    except ValueError as e:  # uklj. InvalidImage i neispravan cigar_id
        raise HTTPException(400, str(e)) from e


@app.get("/band/references")
def band_references(cigar_id: str | None = None) -> dict:
    return {"items": band_service.list_references(cigar_id)}


@app.post("/band/match")
async def band_match(
    file: UploadFile = File(...),
    top_k: int = 5,
) -> dict:
    data = await read_upload(file)
    try:
        hits = band_service.match_image(data, top_k=max(1, min(top_k, 20)))
    except InvalidImage as e:
        raise HTTPException(400, str(e)) from e
    return {
        "matches": [
            {"cigarId": h.cigar_id, "score": h.score, "refId": h.ref_id}
            for h in hits
        ]
    }
