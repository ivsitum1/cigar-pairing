"""FastAPI OCR + band-matching service."""
from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import band_service, ocr_service
from .config import CORS_ORIGINS, IMAGE_TTL_HINT

app = FastAPI(title="cigar-pairing-ocr", version="0.1.0")

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
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty file")
    # request-scoped only — no disk write of the upload
    result = ocr_service.recognize_image_bytes(data)
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
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty file")
    try:
        return band_service.add_reference(cigar_id, data)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.get("/band/references")
def band_references(cigar_id: str | None = None) -> dict:
    return {"items": band_service.list_references(cigar_id)}


@app.post("/band/match")
async def band_match(
    file: UploadFile = File(...),
    top_k: int = 5,
) -> dict:
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty file")
    hits = band_service.match_image(data, top_k=max(1, min(top_k, 20)))
    return {
        "matches": [
            {"cigarId": h.cigar_id, "score": h.score, "refId": h.ref_id}
            for h in hits
        ]
    }
