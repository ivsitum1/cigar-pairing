# Cigar Pairing OCR API

Online PaddleOCR + band-reference matching for the cigar-pairing app / Android APK.

## Setup

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Production OCR (optional, large):
# pip install paddlepaddle paddleocr
# Production CLIP band match (optional):
# pip install torch open-clip-torch
```

## Run

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8787
```

## Endpoints

| Method | Path | Body | Notes |
|--------|------|------|-------|
| GET | `/health` | — | OCR/band engine status |
| POST | `/ocr` | `multipart file` | text + lines (not persisted) |
| POST | `/band/reference` | `cigar_id` + `file` | store band photo + embedding |
| GET | `/band/references?cigar_id=` | — | list refs |
| POST | `/band/match` | `multipart file` | top-k visual matches |

Set app env: `VITE_OCR_API_URL=http://127.0.0.1:8787`

CORS: `CORS_ORIGINS` comma-separated. Band storage: `BAND_REFS_DIR` (default `backend/data/band_refs`).
