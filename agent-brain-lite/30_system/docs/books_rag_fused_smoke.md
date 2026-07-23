# books_rag + TGS fused channel — smoke checklist

**Maps to:** PRD `prd_rag_anatomy_incorporation.json` US-R2 / RA-3  
**Code:** `40_operations/python/brain_assist/fused_rag.py`, MCP `search_fused_rag`  
**Paths:** [BOOKS_RAG_PATHS.md](BOOKS_RAG_PATHS.md)

## Prerequisites

- `BOOKS_RAG_DATA_DIR` set (default `C:\books_rag` on Windows; not on OneDrive)
- Chroma index built: `python 40_operations/scripts/books_rag_verify.py`
- Wiki under `20_knowledge/wiki/` for TGS channel

## Smoke steps

| Step | Command | Pass criterion |
|------|---------|----------------|
| 1 | `pytest 40_operations/tests/test_fused_rag.py -q` | All tests green |
| 2 | `python 40_operations/scripts/fused_rag_search.py -q "hybrid retrieval BM25" --json` | `mode` = `fused_books_tgs`, `results` non-empty when index ready |
| 3 | `python 40_operations/scripts/books_rag_eval.py --limit 3` | `ready: true` for at least one variant (optional if index building) |
| 4 | MCP `search_fused_rag` with same query | JSON: `books_data_dir`, `books_ready`, `books_rag` + `wiki_tgs` in `results` |

## Interpretation

- **Index not ready:** Step 2 may return empty `books` channel; TGS wiki may still return hits. Re-run after `books_rag_index_until_complete.py` finishes.
- **Hybrid RAG (notebook):** Production pattern = BM25 + dense + RRF + rerank; fused channel is books vector + wiki graph/text, not full BM25 yet.

## Last run (2026-06-01)

- `pytest test_fused_rag.py test_mcp_prescreen.py`: 6 passed
- `fused_rag_search.py -q "RAG hybrid BM25 rerank"`: `books_ready=true`, `wiki_hits=10`, `mode=fused_books_tgs`
- Index canonical path: `C:\books_rag` (`BOOKS_RAG_DATA_DIR` in `.env`; OneDrive `data/books_rag/chroma` removed)
- `books_rag_eval.py` (full, 12 queries on local index): `ready=true`, **0 variant errors**, dense avg ~0.87. Report: `C:\books_rag\eval_report.json`
- NotebookLM API: `notebooklm_sync_storage_from_profile.py` then `auth check --test` → token pass
