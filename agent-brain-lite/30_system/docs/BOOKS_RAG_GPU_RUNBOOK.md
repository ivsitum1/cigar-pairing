# Books RAG — GPU runbook

**Version:** 1.1 | **Updated:** 2026-06-28  
**Context:** CPU-only build može biti prespor za pun manifest (~550k redova). Pun rebuild preporučen na stroju s NVIDIA GPU.

---

## Preduvjeti (GPU)

| Stavka | Očekivano |
|--------|-----------|
| GPU | NVIDIA (npr. RTX klase, ≥8 GB VRAM) |
| Driver | `nvidia-smi` radi u PowerShellu |
| Python | **3.12** preporučen (vidi `GPU_COMPUTE_POLICY.md`) |
| Repo | `git pull` na `master` |
| Sync | `books_md` + `outputs/rag_chunks/` dostupni lokalno |

---

## Korak 1 — Okolina

```powershell
cd "C:\Users\<you>\Documents\agent rules"

setx BOOKS_RAG_DATA_DIR C:\books_rag

$env:BOOKS_RAG_DATA_DIR = "C:\books_rag"
$env:BOOKS_RAG_DEVICE = "cuda"
$env:AGENT_COMPUTE_DEVICE = "cuda"
```

Provjera:

```powershell
nvidia-smi
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Ako je `cuda` nedostupan, vidi `40_operations/scripts/install_cuda_torch.ps1` i `GPU_COMPUTE_POLICY.md`.

---

## Korak 2 — Manifest

`outputs/rag_chunks/books_chunk_manifest.jsonl` mora postojati lokalno. Ako nedostaje:

```powershell
python 40_operations/scripts/books_rag_reindex_chunked.py --doc-version 2026-06-24
```

---

## Korak 3 — Pun rebuild indeksa

```powershell
python 40_operations/scripts/build_books_rag_from_manifest.py --root . --force --no-resume
```

Napredak: `C:\books_rag\build_progress.json`. Resume: isti naredba **bez** `--force`.

---

## Korak 4 — Verifikacija

```powershell
python 40_operations/scripts/books_rag_verify.py --json
python 40_operations/scripts/fused_rag_search.py -q "regionalna anestezija komplikacije" --json
```

---

## Korak 5 — Drugi PC (slaba GPU): samo kopija

**Ne radi drugi rebuild** ako je indeks već napravljen na GPU stroju. Vektori u Chroma su neovisni o grafičkoj kartici na čitačkom PC-u.

```powershell
# USB, Explorer, ili:
.\40_operations\scripts\books_rag_sync_from_peer.ps1 -SourcePath "\\GPU-PC\c$\books_rag"

python 40_operations/scripts/books_rag_repair_manifest.py --root .
python 40_operations/scripts/books_rag_verify.py --json --cpu-ok
```

Uvjet: ista verzija `embedding_model` u `manifest.json` (default `intfloat/multilingual-e5-small`).

---

## CPU-only okruženje

Djelomični CPU indeks (~10k chunkova) **zanemari** pri GPU rebuildu (`--force`). Bez NVIDIA GPU-a koristi CPU torch ili prebaci build na GPU stroj.

---

## Troubleshooting

| Problem | Rješenje |
|---------|----------|
| `DuplicateIDError` | Povuci latest git; `manifest_index.py` dedupe |
| Chroma lock | Obriši `C:\books_rag\.build.lock` ako nema aktivnog procesa |
| `cuda requested but unavailable` | cu128 torch + `nvidia-smi` |
| MCP books_rag prazan | Restart Cursor; provjeri `BOOKS_RAG_DATA_DIR` |

---

## Povezano

- [`BOOKS_RAG_PATHS.md`](BOOKS_RAG_PATHS.md)
- [`GPU_COMPUTE_POLICY.md`](GPU_COMPUTE_POLICY.md)
- [`RAG_CHUNKING_MAP.md`](RAG_CHUNKING_MAP.md)
