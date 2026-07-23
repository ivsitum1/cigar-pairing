# PaddlePaddle in this workspace

This repo uses the official **PaddlePaddle** deep learning framework as the runtime for PDF OCR. We install **prebuilt wheels** from Baidu's package index; we do **not** clone or vendor the full [PaddlePaddle/Paddle](https://github.com/PaddlePaddle/Paddle) source tree (Apache-2.0, ~24k stars).

## Stack layers

| Layer | Role | Source in this repo |
|-------|------|---------------------|
| **PaddlePaddle** | Core framework (train/infer, CPU/GPU) | `pip install paddlepaddle==3.2.2` via `install_paddle_ocr.py` |
| **PaddleX** | Pipeline runtime for document OCR | `paddlex[ocr]==3.5.2` (required for PP-StructureV3) |
| **PaddleOCR** | OCR models and `PPStructureV3` API | Vendored under `40_operations/vendor/PaddleOCR/` (bootstrap zip) |
| **pdf_extraction** | Workspace wrapper | `40_operations/python/pdf_extraction/` |

Upstream links:

- Framework: [https://github.com/PaddlePaddle/Paddle](https://github.com/PaddlePaddle/Paddle)
- Releases: [PaddlePaddle 3.2.x](https://github.com/PaddlePaddle/Paddle/releases) (we pin `3.2.2` in `pdf_extraction/device.py`; avoid 3.3.x CPU oneDNN/PIR crash)
- Install guide: [paddlepaddle.org.cn – Quick Install](https://www.paddlepaddle.org.cn/install/quick)
- OCR project: [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

## One-time setup (Windows)

```powershell
.\40_operations\scripts\install_paddle_ocr.ps1
```

Creates `.venv-ocr` (Python **3.12**; 3.14 is unsupported by Paddle wheels). Installs:

1. `paddlepaddle` or `paddlepaddle-gpu` **3.2.2** from official indexes
2. Editable `paddleocr` from vendor (or PyPI fallback)
3. `paddlex[ocr]` and `requirements-ocr.txt`

## Run OCR

```powershell
.\40_operations\scripts\extract_pdf_ocr.ps1 -Root . -Ocr auto
```

Always use `.venv-ocr\Scripts\python.exe`, not system Python 3.14.

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PADDLE_OCR_DEVICE` | `auto` | `auto`, `gpu`, or `cpu` |
| `PADDLE_OCR_LANG` | `en` | OCR language |
| `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK` | unset | Set `True` to skip model-host connectivity check on first run |
| `PADDLEOCR_ZIP` | user Downloads | Path to `PaddleOCR-main.zip` for vendor bootstrap |

## Model cache

First inference downloads weights to `%USERPROFILE%\.paddlex\official_models\` (not committed). Subsequent runs use cache.

## Version pins (single source of truth)

Defined in `40_operations/python/pdf_extraction/device.py`:

- `PADDLEPADDLE_VERSION` — framework wheel (currently `3.2.2`)
- `PADDLEX_OCR_EXTRA_VERSION` — PaddleX OCR extra (currently `3.5.2`)

## Related docs

- [REFERENCE_LIBRARY_AGENT_ACCESS.md](REFERENCE_LIBRARY_AGENT_ACCESS.md) — PDF → markdown flow
- [40_operations/vendor/README.md](../../40_operations/vendor/README.md) — PaddleOCR vendor bootstrap
- Skill: `30_system/SKILLS/SKILL_paddle-ocr.md`
