# RAG vs study data (codebooks)

Two independent capabilities in agent-rules. Do not mix them in one task or search scope.

## Books RAG (reference library retrieval)

| | |
|--|--|
| **Purpose** | Semantic search over indexed textbook/guideline text in `20_knowledge/wiki/sources/books_md/` |
| **Docs** | [BOOKS_RAG.md](BOOKS_RAG.md) |
| **Rule** | `.cursor/rules/books-rag.mdc` (on demand) |
| **Scripts** | `40_operations/scripts/build_books_rag_index.py`, `install_books_rag.py` |
| **MCP** | `books_rag` (`search_books`, `get_book_chunk`) |
| **Data** | `BOOKS_RAG_DATA_DIR` / `C:\books_rag\chroma\` (embeddings; not study variables) |

**Triggers:** cite from library, guideline, textbook, `books_rag`, rebuild index.

**Not:** extraction sheets, `variable_name`, meta-analysis project folders, `01_input/codebook/`.

---

## Study data codebooks (project variable contracts)

| | |
|--|--|
| **Purpose** | Define what each column means in **your** extraction sheet or analysis CSV |
| **Docs** | [study_data/README.md](study_data/README.md) |
| **Templates** | `40_operations/templates/codebooks/` (copied into study projects) |
| **Scripts** | `codebook_seed.py`, `prepare_study_codebook.py` (run from **study** project root) |
| **Lives in** | Study workspace: `01_input/data_extraction/codebook.md`, `01_input/codebook/dataset_codebook.md` |

**Triggers:** setup project, MA extraction, EDA on own data, validate-setup codebook warnings.

**Not:** Chroma, embeddings, `search_books`, `books_md` corpus.

---

## Agent routing

- User works on **RAG only** → load `BOOKS_RAG.md` + `books-rag.mdc`; ignore codebook/migration docs unless explicitly asked.
- User works on **codebook / MA / cohort** → load `study_data/` docs + relevant statistics skills; do not call `books_rag` unless they ask for library quotes.

---

## Related

- [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md) — brain vs study project roots
- [MCP_AND_SKILLS_LAYERS.md](../../.cursor/docs/MCP_AND_SKILLS_LAYERS.md)
