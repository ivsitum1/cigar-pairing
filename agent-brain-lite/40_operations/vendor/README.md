# Vendor: PaddleOCR

Upstream source for OCR and document parsing (PP-StructureV3). Not committed by default; bootstrap locally from your zip.

**Framework (pip wheels, not vendored):** [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) 3.3.x — see [30_system/docs/PADDLEPADDLE.md](../../30_system/docs/PADDLEPADDLE.md).

## One-time bootstrap

```bash
python 40_operations/scripts/bootstrap_paddleocr_vendor.py
```

Default zip path: `%USERPROFILE%\Downloads\PaddleOCR-main.zip`  
Override: `set PADDLEOCR_ZIP=C:\path\to\PaddleOCR-main.zip`

Extracts into `40_operations/vendor/PaddleOCR/` (contents of `PaddleOCR-main/` inside the zip).

## Python version

Use **Python 3.8–3.12** for `paddlepaddle` wheels (3.14 is not supported yet). On Windows:

```powershell
py install 3.12
py -3.12 40_operations/scripts/install_paddle_ocr.py
```

## Install runtime (after bootstrap)

**Recommended (Windows, Python 3.12 venv):**

```powershell
.\40_operations\scripts\install_paddle_ocr.ps1
```

Creates `.venv-ocr` and installs PaddlePaddle + paddleocr. Extract PDFs with:

```powershell
.\40_operations\scripts\extract_pdf_ocr.ps1 -Root . -Ocr auto
```

**Manual:**

```bash
py -3.12 -m venv .venv-ocr
.venv-ocr\Scripts\python.exe 40_operations/scripts/install_paddle_ocr.py
```

Installs PaddlePaddle (GPU if CUDA is available, else CPU), paddleocr from vendor (editable with `SETUPTOOLS_SCM_PRETEND_VERSION`) or PyPI fallback, and `40_operations/requirements-ocr.txt`.

Model weights download on first inference (cache under user home, not in this repo).

## Git

`40_operations/vendor/PaddleOCR/` is listed in root `.gitignore` to avoid pushing the full upstream tree. Commit bootstrap scripts, `requirements-ocr.txt`, and `40_operations/python/pdf_extraction/` instead.

## Usage in this workspace

```bash
python 40_operations/scripts/extract_pdf_library_to_md.py --root . --ocr auto
```

## Related docs

- [DEEP_LEARNING_POLICY.md](../../30_system/docs/DEEP_LEARNING_POLICY.md) — brain vs study ML/DL
- [REFERENCE_LIBRARY_AGENT_ACCESS.md](../../30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS.md) — PDF → markdown flow
