# Books RAG — lokalni LLM (Ollama)

Ollama radi **generativni** sloj (sažetak, lokalni Q&A). **Embedding** ostaje `intfloat/multilingual-e5-small` u Chroma; Gemma/Llama ne zamjenjuju e5.

## Zašto

| Korak | Gdje radi | Cursor kontekst |
|-------|-----------|-----------------|
| Indeksiranje + vektorska pretraga | Lokalno (Python + Chroma) | Ne |
| Rerank (CrossEncoder) | Lokalno | Ne |
| Sažetak pogodaka | Ollama (opcija) | Manje (~1200 znakova umjesto više chunkova) |

## Instalacija (Windows)

1. Preuzmite [Ollama](https://ollama.com/download) i instalirajte.
2. U terminalu povucite mali model:

```bash
ollama pull gemma2:2b
```

Alternativa (malo veći): `ollama pull llama3.2:3b`

3. Provjera:

```bash
ollama run gemma2:2b "test"
curl http://127.0.0.1:11434/api/tags
```

## Automatski način (zadano)

| Varijabla | Zadano | Ponašanje |
|-----------|--------|-----------|
| `BOOKS_RAG_CONTEXT_MODE` | **`auto`** | Hook i MCP koriste **summary** (štedi kontekst). Ako Ollama radi → generativni sažetak; inače **fallback** (kratki izvadci + chunk_id). |
| `BOOKS_RAG_CONTEXT_MODE` | `off` | Stari način: puni chunkovi u kontekst |
| `BOOKS_RAG_CONTEXT_MODE` | `on` | Uvijek summary; Ollama samo ako je dostupna |

**Ne trebate** ručno `BOOKS_RAG_OLLAMA_ENABLED=1` u `auto` načinu.

Provjera:

```bash
python -c "from books_rag.retrieval import BooksRetriever; import json; print(json.dumps(BooksRetriever().status()['context_policy'], indent=2))"
```

## Ručno uključivanje (opcionalno)

| Varijabla | Preporuka |
|-----------|-----------|
| `BOOKS_RAG_OLLAMA_MODEL` | `gemma2:2b` |
| `BOOKS_RAG_GATEWAY_MAX_CHARS` | `1200` |
| `BOOKS_RAG_MAX_CHARS` | `1500` (injekcija u Cursor) |

Rerank (preporučeno, bez Ollame):

| Varijabla | Zadano |
|-----------|--------|
| `BOOKS_RAG_RERANK_ENABLED` | `1` |
| `BOOKS_RAG_RETRIEVE_K` | `20` |
| `BOOKS_RAG_RERANK_K` | `5` |
| `BOOKS_RAG_HYBRID_ENABLED` | `1` |

Restart MCP poslije promjene env.

## CLI bez Cursora

Potpuno lokalni odgovor (0 tokena u chatu):

```bash
python -m books_rag.local_gateway --query "Welch t-test pretpostavke"
python -m books_rag.local_gateway --query "regionalna anestezija" --json
```

## MCP alati

- `search_books(..., mode="chunks")` — klasični odlomci
- `search_books(..., mode="summary")` — sažetak + citati
- `search_books_answer(...)` — isto kao summary
- `get_book_chunk(chunk_id)` — puni tekst za citat

## Ako Ollama nije pokrenuta

Gateway automatski pada na **fallback**: kratki izvadci + chunk_id (bez halucinacije iz modela).

## Hardver

- **CPU-only:** `gemma2:2b`, mali `k`, prvi poziv sporiji (učitavanje modela).
- **GPU:** brži sažetak; embedding build i dalje koristi CPU/GPU preko sentence-transformers.

## Povezano

- [BOOKS_RAG.md](BOOKS_RAG.md)
- [RAG_VS_STUDY_DATA.md](RAG_VS_STUDY_DATA.md)
