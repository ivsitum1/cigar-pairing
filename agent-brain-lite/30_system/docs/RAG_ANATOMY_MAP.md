# RAG Anatomy Map (agent-rules)

**Version:** 1.0 | **Last updated:** 2026-06-01  
**Source:** NotebookLM *RAG Anatomy, Harness, Workflow* (16 YouTube transcripts); external verification in [`notebooklm_rag_anatomy_external_verification.json`](notebooklm_rag_anatomy_external_verification.json).

Treat marketing claims (e.g. “delete hallucination”, model leaderboard %) as **UNVERIFIED** in operational docs.

---

## Corpus half (offline)

| Stage | Purpose | Repo touchpoints |
|-------|---------|------------------|
| Ingest | Normalize PDF/HTML/exports; strip boilerplate | `books_rag` ingest, `wiki-ingest`, `paddle-ocr` |
| Clean | PII/secrets policy; dedupe | ingest scripts, manifest |
| Chunk | Parent-child + layout-aware (see [`RAG_CHUNKING_MAP.md`](RAG_CHUNKING_MAP.md)) | `chunk_policy.py`, `wiki_chunk_ingest.py` |
| Embed | Same model for index and query | `books_rag`, embedding config in `gpu.py` |
| Index | Vector + sparse (BM25) dual write | Chroma under `BOOKS_RAG_DATA_DIR` (`C:\books_rag`); see [BOOKS_RAG_PATHS.md](BOOKS_RAG_PATHS.md) |

---

## Query half (online)

| Stage | Purpose | Repo touchpoints |
|-------|---------|------------------|
| Query rewrite / expand | Recall vs precision | optional query scripts |
| Retrieve | Top-K dense + sparse | `books_rag` MCP, `tgs_rag.py` |
| Fuse | RRF or weighted hybrid | `fused_rag` / `search_fused_rag` |
| Rerank | Cross-encoder shortlist | `rerank_ce.py` (P1); optional on fused search |
| Augment + ground | Labeled chunks; cite or refuse | writing skills + Swiss gate for clinical |

---

## Multi-hop

Use when evidence spans documents: hop *n* output becomes hop *n+1* query. Require **max hops**, **token budget**, and **stop on no new entities** (notebook + `progress.txt` risks).

---

## Harness cross-cut (four levers)

| Lever | RAG tie-in |
|-------|------------|
| Context | What chunks enter the prompt; ordering and budget |
| Tools | Retrieval MCP contracts; prescreen before retry |
| Loop | Max steps; no-progress detection |
| Governance | HITL for destructive tools; path sandbox |

Canonical map: [`LIFEHARNESS_4_LAYER.md`](LIFEHARNESS_4_LAYER.md).

---

## Related

- [[NotebookLM research gate]]
- [[LifeHarness four-layer model]]
- [`outputs/notebooklm/rag_anatomy_executive.md`](../../outputs/notebooklm/rag_anatomy_executive.md)
