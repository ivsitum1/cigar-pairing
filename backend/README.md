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

## Configuration

| Env | Default | Purpose |
|---|---|---|
| `CORS_ORIGINS` | localhost dev origins | comma-separated allowed origins |
| `BAND_REFS_DIR` | `backend/data/band_refs` | band reference storage |
| `MAX_UPLOAD_BYTES` | `12582912` (12 MB) | per-request upload ceiling → `413` |
| `MAX_IMAGE_PIXELS` | `50000000` | decompression-bomb guard → `400` |
| `OCR_HOST` / `OCR_PORT` | `0.0.0.0` / `8787` | bind address |

## Security note

**There is no authentication.** `POST /band/reference` writes to disk and
`GET /band/references` enumerates everything stored. That is fine on
`127.0.0.1`, but the default bind is `0.0.0.0` so an Android build on the same
network can reach it — which also means anyone else on that network can. Bind
to `127.0.0.1` (`OCR_HOST=127.0.0.1`) unless you specifically need LAN access,
and do not expose this service to the public internet as-is.

Uploads are read in 1 MiB chunks and rejected past `MAX_UPLOAD_BYTES`; images
are validated before decoding, so a non-image or oversized payload returns
`400`/`413` rather than crashing a worker.

## Tests

```bash
cd backend
pip install pillow "numpy<2" imagehash fastapi python-multipart httpx
python -m unittest discover -s tests -v
```

Paddle/torch are not needed — the service has a stub path, and the tests cover
path traversal, the upload ceiling, and `400`-vs-`500` behaviour without them.
CI runs this as a separate `backend` job.
