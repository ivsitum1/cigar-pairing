---
name: paddle-ocr
description: Use for OCR on scanned PDFs and images via PaddleOCR PP-StructureV3. Triggers include OCR, paddleocr, scan PDF, extract text from image, scanned document.
version: 1.0
last_updated: 2026-05-22
domain: tools
tokens: ~650
triggers:
  - OCR
  - paddleocr
  - paddle ocr
  - scan PDF
  - scanned PDF
  - extract text from image
  - image OCR
requires_packages: []
reference_files:
  - 30_system/docs/PADDLEPADDLE.md
  - 40_operations/vendor/README.md
pipeline_position: []
---

# Skill: PaddleOCR (PP-StructureV3)

Priority OCR engine for **scanned PDFs** and **images** in this workspace. Digital PDFs still use PyPDF2 first (`--ocr auto`).

## When to use

- Scanned books/chapters in `20_knowledge/reference_library/`
- PDF with empty or sparse text layer (`extraction_failed`, `content_note: full_text_extract_py_pdf2` with little body text)
- Standalone PNG/JPG/TIFF needing text for notes or RAG
- User says: OCR, PaddleOCR, skenirani PDF

## Prerequisites (one-time)

**Windows (recommended):**

```powershell
.\40_operations\scripts\install_paddle_ocr.ps1
```

**Manual:** Python 3.12 venv + bootstrap + install:

```bash
python 40_operations/scripts/bootstrap_paddleocr_vendor.py
.venv-ocr/Scripts/python.exe 40_operations/scripts/install_paddle_ocr.py
```

- **Framework:** [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) **3.2.2** CPU wheels (`enable_mkldnn=False` in pipeline; see `30_system/docs/PADDLEPADDLE.md`).
- **OCR app:** `40_operations/vendor/PaddleOCR/` from `PaddleOCR-main.zip` (`PADDLEOCR_ZIP`).
- Do **not** use system Python 3.14; use `.venv-ocr` only.

## Step-by-step procedure

1. **Confirm install** — `python -c "from pdf_extraction import is_paddle_available; print(is_paddle_available())"` from repo root with `40_operations/python` on path, or run install script above.

2. **Reference library PDFs** (preferred batch path):

   ```bash
   python 40_operations/scripts/extract_pdf_library_to_md.py --root . --ocr auto
   ```

   - `--ocr paddle` — always PaddleOCR
   - `--ocr off` — PyPDF2 only
   - `--force-ocr` — Paddle even if text layer exists
   - `--only-prefix reference_library/medicine` — subset
   - `--prune-stale` — delete old `books_md` parts before rewrite
   - `--resume` — skip unchanged paddle extractions (`data/pdf_extract/progress.json`)

**Full library migration (all PDFs, Paddle forced):**

```powershell
.\40_operations\scripts\run_pdf_paddle_migration.ps1 -Root .
```

Audit: `python 40_operations/scripts/audit_books_md_extraction.py --root .`

3. **Then refresh stubs and RAG** (if indexing books):

   ```bash
   python 40_operations/scripts/ingest_pdf_sources.py --root .
   python 40_operations/scripts/build_books_rag_index.py --root . --force
   ```

4. **Report** — note `content_note: paddleocr_ppstructurev3` in output frontmatter; cite `books_md` paths, not raw PDF blobs in chat.

## Environment

| Variable | Default | Role |
|----------|---------|------|
| `PADDLE_OCR_LANG` | `en` | OCR language (PP-OCRv5) |
| `PADDLE_OCR_DEVICE` | `auto` | `auto`, `gpu`, `cpu` |
| `PADDLE_OCR_FORCE` | off | Treat as scan (skip density heuristic) |
| `PADDLEOCR_ZIP` | Downloads zip path | Bootstrap source |
| `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK` | unset | `True` skips model-host connectivity check on cold start |

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]` only after script run; OCR errors as `[BLANK]` with install or path fix.
- Do not invent text from scans; verify against source PDF when critical.

## Verification

- [ ] `install_paddle_ocr.py` completed without import error
- [ ] At least one previously empty scan produces non-empty `books_md` with `paddleocr_ppstructurev3`
- [ ] `ingest_pdf_sources.py` run if wiki PDF stubs must link new MD

## Related Hubs

- [Skill registry](registry.json)
- [PaddlePaddle stack](../docs/PADDLEPADDLE.md)
- [Deep learning policy](../docs/DEEP_LEARNING_POLICY.md)
- [Reference library access](../docs/REFERENCE_LIBRARY_AGENT_ACCESS.md)
- [Books RAG](../docs/BOOKS_RAG.md)
- [Vendor README](../../40_operations/vendor/README.md)
