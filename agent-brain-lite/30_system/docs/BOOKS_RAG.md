# Books RAG — semantic search over reference library

Local vector retrieval over `20_knowledge/wiki/sources/books_md/` (extracted PDF text). Complements session **memory** MCP (FTS) and on-demand **pdf** MCP; does not replace PubMed for new literature.

**Paths:** [BOOKS_RAG_PATHS.md](BOOKS_RAG_PATHS.md) (canonical `C:\books_rag` on Windows; repo `data/books_rag/` is redirect only).

**Not this:** study [codebooks](study_data/README.md) (`01_input/codebook/`, MA extraction variables). See [RAG vs study data](RAG_VS_STUDY_DATA.md).

## When to use what

| Tool | Use for |
|------|---------|
| `books_rag` MCP `search_books` | Quotes, definitions, chapters from your indexed books |
| `memory` MCP | Session history, project decisions, OTA |
| `pdf` MCP | One-off read of a PDF not yet in `books_md` |
| PubMed MCP | New published papers |

## Build index

**One-shot install (pip + index + verify):**

```bash
python 40_operations/scripts/install_books_rag.py
```

**Manual steps:**

```bash
pip install -r requirements.txt
python 40_operations/scripts/build_books_rag_index.py --root .
```

Progress (local index dir, default `C:\books_rag` on Windows): `full_build.log`, `build_progress.json`, `manifest.json`. Set `BOOKS_RAG_DATA_DIR` in `.env`.

Options:

- `--limit 50` — smoke test on first 50 MD files (by size, smallest first)
- `--force` — wipe Chroma collection and rebuild (required after chunk-size change)
- `--dry-run` — count files/chunks without embedding
- `--max-files 50` — index at most 50 new/changed files per run (batch / Task Scheduler)
- `--embed-buffer 12` — micro-flush every N chunks (default 12)
- `--no-lock` — skip `.build.lock` (not recommended)

### Micro-chunk defaults (anti-stall)

| Env / setting | Default | Role |
|---------------|---------|------|
| `BOOKS_RAG_CHUNK_CHARS` | 900 | Smaller text chunks (~200–250 tokens) |
| `BOOKS_RAG_CHUNK_OVERLAP_CHARS` | 120 | Overlap between chunks |
| `BOOKS_RAG_EMBED_BUFFER` | 12 | Embed + upsert every 12 chunks |
| `BOOKS_RAG_EMBED_BATCH` | 8 | sentence-transformers batch |
| `BOOKS_RAG_CHROMA_UPSERT_BATCH` | 24 | Chroma upsert batch |
| `BOOKS_RAG_MANIFEST_EVERY` | 1 | Checkpoint manifest after each file |

Files are processed **smallest first**; manifest stores only `{hash, chunks}` per file (no chunk ID lists). Re-index deletes by Chroma `source_md` metadata.

Index storage: **`BOOKS_RAG_DATA_DIR`** (default `C:\books_rag` on Windows). Not under OneDrive. Repo `data/books_rag/` is a redirect README only.

Refresh corpus first if you added PDFs:

```bash
# One-time if you have scanned books: install_paddle_ocr.py (see REFERENCE_LIBRARY_AGENT_ACCESS.md)
python 40_operations/scripts/extract_pdf_library_to_md.py --root . --ocr auto
python 40_operations/scripts/ingest_pdf_sources.py --root .
python 40_operations/scripts/build_books_rag_index.py --root .
```

Or install RAG stack and OCR together:

```bash
python 40_operations/scripts/install_books_rag.py --with-ocr
```

## Corpus migration (PaddleOCR, 2026)

When `books_md` is re-extracted with Paddle (`content_note: paddleocr_ppstructurev3`), **rebuild the vector index**:

```bash
python 40_operations/scripts/build_books_rag_index.py --root . --force
```

- PyPDF2-era chunks (`full_text_extract_py_pdf2`) are replaced in place when the same `source_pdf` is re-OCR'd; `--force` avoids stale Chroma embeddings.
- Audit extraction coverage: `python 40_operations/scripts/audit_books_md_extraction.py --root .` → `data/pdf_extract/inventory.json`.
- Full OCR pipeline: [REFERENCE_LIBRARY_AGENT_ACCESS.md](REFERENCE_LIBRARY_AGENT_ACCESS.md) → `run_pdf_paddle_migration.ps1`.

## Retrieval quality (rerank + hybrid)

| Env | Default | Role |
|-----|---------|------|
| `BOOKS_RAG_RETRIEVE_K` | `20` | Wide dense retrieval before rerank |
| `BOOKS_RAG_RERANK_K` | `5` | Final chunks after CrossEncoder |
| `BOOKS_RAG_RERANK_ENABLED` | `1` | Toggle rerank |
| `BOOKS_RAG_RERANK_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranker |
| `BOOKS_RAG_HYBRID_ENABLED` | `1` | Keyword boost on title/domain/excerpt |
| `BOOKS_RAG_HYBRID_BOOST` | `0.15` | Max score boost from token overlap |

## MCP tools (`books_rag` server)

- `search_books(query, k=8, domain="", mode="chunks"|"summary")` — semantic search; cite as `[books_rag:chunk_id]`
- `search_books_answer(query, k=5, domain="")` — rerank + local summary (see [BOOKS_RAG_LOCAL_LLM.md](BOOKS_RAG_LOCAL_LLM.md))
- `get_book_chunk(chunk_id)` — full chunk text
- `books_rag_status()` — chunk count, model, index %, rerank/ollama flags

Register in `.cursor/mcp.json` (already wired). Restart Cursor MCP after install.

**Batch index until 100%:**

```powershell
.\40_operations\scripts\books_rag_index_batch.ps1 -MaxFiles 50
python 40_operations/scripts/books_rag_index_until_complete.py --root . --max-files 50
```

**Eval (dense vs rerank vs summary):**

```bash
python 40_operations/scripts/books_rag_eval.py --json --output C:/books_rag/eval_report.json
```

## Hook injection

`books_rag_lifecycle.py` runs on `beforeSubmitPrompt` (and optional `sessionStart` status).

| Variable | Default | Meaning |
|----------|---------|---------|
| `BOOKS_RAG_ENABLED` | `1` | Master switch |
| `BOOKS_RAG_MIN_SCORE` | `0.35` | Minimum similarity to inject |
| `BOOKS_RAG_MAX_CHARS` | `4000` | Injection budget |
| `BOOKS_RAG_TOP_K` | `8` | MCP search default |
| `BOOKS_RAG_INJECT_TOP_K` | `5` | Hook injection count |
| `BOOKS_RAG_MODEL` | `intfloat/multilingual-e5-small` | Embedding model |
| `BOOKS_RAG_INJECT_STATUS_ON_START` | `0` | Show index status on session start |
| `BOOKS_RAG_CONTEXT_MODE` | **`auto`** | `auto` = compact summary injection/MCP; `off` = raw chunks; `on` = summary + Ollama if up |
| `BOOKS_RAG_OLLAMA_ENABLED` | (legacy) | Koristi `CONTEXT_MODE=on` umjesto ručnog flaga |
| `BOOKS_RAG_INJECT_SUMMARY` | (override) | `0`/`1` forsira isključeno/uključeno summary |

Injection runs when top score ≥ `BOOKS_RAG_MIN_SCORE`, or when the prompt matches library cues (e.g. *citiraj*, *guideline*, *anestezija*) and score ≥ 85% of that threshold.

## Limitations

- Scanned PDFs need PaddleOCR (`install_paddle_ocr.py`) and `--ocr auto`; without it they may stay empty (`extraction_failed` / short body skipped).
- First full build is CPU-heavy (tens of thousands of chunks); use incremental rebuilds afterward.
- Chroma + model cache use ~4+ GB under `%BOOKS_RAG_DATA_DIR%` (default `C:\books_rag`) plus Hugging Face cache.

## Related

- [BOOKS_RAG_LOCAL_LLM.md](BOOKS_RAG_LOCAL_LLM.md) — Ollama, Gemma/Llama, šteda Cursor konteksta
- [RAG_VS_STUDY_DATA.md](RAG_VS_STUDY_DATA.md) — do not mix with codebook / meta-analysis project docs
- [REFERENCE_LIBRARY_AGENT_ACCESS.md](REFERENCE_LIBRARY_AGENT_ACCESS.md)
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)
