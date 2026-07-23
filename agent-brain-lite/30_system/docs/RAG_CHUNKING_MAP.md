# RAG Chunking Map (agent-rules)

**Version:** 1.0 | **Last updated:** 2026-06-24  
**Source:** NotebookLM Strategic RAG Chunking (`cea806f1`); extends [`RAG_ANATOMY_MAP.md`](RAG_ANATOMY_MAP.md) corpus half.

---

## Strategies

| Strategy | Search unit | Generation unit | Repo |
|----------|-------------|---------------|------|
| Parent-child | Small chunk (200–512 tokens est.) | Parent section via `parent_id` | `chunk_policy.py` |
| Contextual framing | Same chunk id | Embed text includes `doc_title > section_path` | `framed_embed_text()` |
| Layout-aware | Split on `#` headings or AST boundaries | Never mid-heading | `wiki_chunk_ingest.py` |
| Metadata filter | Required fields on ingest | Filter at query time | `doc_version`, `source_type`, `environment` |

---

## Required chunk metadata

```json
{
  "chunk_id": "uuid",
  "parent_id": "section-uuid or null for root",
  "section_path": "Chapter 1 > Methods",
  "doc_title": "Source title",
  "doc_version": "2026-06-01",
  "source_type": "wiki|book|pdf|web",
  "environment": "agent-rules"
}
```

---

## Ingest touchpoints

| Corpus | Script / module |
|--------|-----------------|
| Wiki | `40_operations/scripts/wiki_chunk_ingest.py` |
| Books | `40_operations/scripts/books_rag_reindex_chunked.py` (manifest) → `build_books_rag_from_manifest.py` (Chroma) |
| Generic | `40_operations/python/brain_assist/chunk_policy.py` |

---

## Out of scope

- **Late chunking** — requires long-context embedding API; document only.
- **Unverified % token savings** — no rules prose without local eval.

---

## Related

- [[RAG anatomy harness workflow]]
- [`notebooklm_rag_chunking_grill_prompts.md`](reference/notebooklm_rag_chunking_grill_prompts.md)
