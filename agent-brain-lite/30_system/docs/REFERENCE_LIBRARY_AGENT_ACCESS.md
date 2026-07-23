# Reference library: how agents and Obsidian should use PDFs

## Why PDFs did not look “sorted” in Obsidian

- **Binary PDFs** do not behave like Markdown notes in the graph. The vault lists them under folder paths (`20_knowledge/reference_library/...`), not as a single “books shelf”.
- **Stub notes** in `20_knowledge/wiki/sources/pdf/` only pointed at file paths until full-text extract existed.
- **Domain sorting** now follows folder semantics: `medicine/anesthesiology`, `medicine/emergency`, `medicine/intensive_care`, `statistics`, `writing`, `opinions`, `coding`, plus `00_inbox/raw`.

## Canonical flow

0. **One-time OCR stack** (scanned PDFs; optional if all PDFs have text layers):

   ```powershell
   .\40_operations\scripts\install_paddle_ocr.ps1
   ```

   (Installs Python 3.12 if needed, creates `.venv-ocr`, bootstrap vendor, PaddlePaddle **3.2.2** CPU wheels + PaddleOCR. See [PADDLEPADDLE.md](PADDLEPADDLE.md).)

0b. **OneDrive:** ensure PDFs under `reference_library/` and `00_inbox/raw/` are **available offline** on this machine before bulk OCR.

1. **Place or copy** PDFs under `20_knowledge/reference_library/...` or `00_inbox/raw/`.
2. **Extract text to Markdown** (searchable, linkable, agent-friendly):

   `.\40_operations\scripts\extract_pdf_ocr.ps1 -Root . -Ocr auto`

   Or: `.venv-ocr\Scripts\python.exe 40_operations/scripts/extract_pdf_library_to_md.py --root . --ocr auto`

   - `--ocr paddle` — always PaddleOCR (PP-StructureV3)
   - `--ocr off` — PyPDF2 only
   - `--force-ocr` — Paddle even when a text layer exists
   - `--prune-stale` — remove old `books_md` parts for each PDF stem before rewrite
   - `--resume` — skip PDFs already in `data/pdf_extract/progress.json` with matching sha1 and paddle `content_note`

**Full corpus migration (Paddle on all PDFs):**

```powershell
.\40_operations\scripts\run_pdf_paddle_migration.ps1 -Root .
```

Then rebuild semantic index: `python 40_operations/scripts/build_books_rag_index.py --root . --force`

Inventory / audit: `python 40_operations/scripts/audit_books_md_extraction.py --root .`

3. **Refresh PDF stub notes and indexes**:

   `python 40_operations/scripts/ingest_pdf_sources.py --root .`

4. **Browse** extracted text by domain:
   - `20_knowledge/wiki/sources/books_md/INDEX.md`
5. **Graph / search**: open a `books_md` note; each note links to [[20_knowledge/wiki/index]], [[20_knowledge/wiki/sources/books_md/INDEX]], and its domain section (e.g. `INDEX#medicine_anesthesiology`). Refresh links after bulk adds: `python 40_operations/scripts/link_books_md_hubs.py --root .`

## Memory and workflow

- Session and OTA-style logging stay in `.agent/` and `30_system/04_documentation/context/` per existing rules.
- **Reference content** for citations and quotes: prefer `books_md` notes after extract, not raw PDF text in chat.
- **Semantic search** over the library: use MCP `books_rag` → `search_books` (see [BOOKS_RAG.md](BOOKS_RAG.md)); do not grep entire `books_md` for conceptual questions when the index is built.
- If extraction fails (encryption, missing OCR install), the stub under `books_md` marks `extraction_failed` and still points to the PDF path. After `install_paddle_ocr.py`, re-run extract with `--ocr auto` or `--force-ocr`.
- Successful Paddle runs set `content_note: paddleocr_ppstructurev3` in frontmatter.

## Regeneration after bulk adds

Run in order:

1. `extract_pdf_library_to_md.py` (or `extract_pdf_ocr.ps1` / `run_pdf_paddle_migration.ps1` for Paddle)
2. `ingest_pdf_sources.py`
3. `build_books_rag_index.py --force` when `books_md` text changed materially
4. Optional: `link_books_md_hubs.py`, `generate_folder_md_indexes.py`, `trace_pdf_md_links.py` (see `30_system/docs/AUTOMATION_INDEX.md`).
