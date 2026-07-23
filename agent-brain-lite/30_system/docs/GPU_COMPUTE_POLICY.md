# GPU compute policy

**Canonical rule:** `.cursor/rules/gpu-compute.mdc`  
**Helper:** `40_operations/python/common/gpu.py`

---

## Principle

All compute-heavy workloads use GPU when available. Device selection goes through `resolve_device()`; do not hardcode `cpu` except in unit tests or when the user sets `AGENT_COMPUTE_DEVICE=cpu`.

---

## GPU workloads in this repo

| Workload | Module | Env override |
|----------|--------|--------------|
| books_rag embeddings | `books_rag/embedder.py` | `BOOKS_RAG_DEVICE` |
| books_rag rerank | `books_rag/reranker.py` | `BOOKS_RAG_DEVICE` |
| model-native embeddings | `40_operations/python/model_native/embedder.py` | `MODEL_NATIVE_DEVICE` |
| residual hooks / SAE | `40_operations/python/model_native/residual_hooks.py` | `MODEL_NATIVE_DEVICE` |
| AI detection (transformers) | `30_system/behavior_rules/tools/ai_detection_advanced.py`, `check_ai_plagiarism.py` | `AGENT_COMPUTE_DEVICE` |
| PaddleOCR PDF extraction | `40_operations/python/pdf_extraction/device.py` | `PADDLE_OCR_DEVICE` |
| Local LLM summaries | Ollama | `BOOKS_RAG_OLLAMA_*` (Ollama uses GPU independently) |

Global default: `AGENT_COMPUTE_DEVICE=auto|cuda|cpu` (default `auto`).

---

## PyTorch CUDA install (required for GPU)

Plain `pip install torch` on Windows gives **CPU-only** wheels. Install CUDA build explicitly:

```powershell
python -m pip install --index-url https://download.pytorch.org/whl/cu128 --force-reinstall torch==2.10.0+cu128
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

Or use the repo helper (waits for a completed local wheel download):

```powershell
.\40_operations\scripts\install_cuda_torch.ps1 -DownloadIfMissing
```

Expected: `True 12.8` on RTX 4060 with current drivers.

**Contingency:** If Python 3.14 CUDA wheel fails at runtime, use a dedicated venv with Python 3.12 + the same cu128 command + `sentence-transformers`.

PaddleOCR GPU uses a separate venv (`C:\Users\Ivan\dise-rag-venv`) with `paddlepaddle-gpu`; not mixed into system Python.

---

## VRAM budget (RTX 4060, 8 GB)

- Ollama (e.g. gemma2:2b): ~1–2 GB when resident
- e5-small + MiniLM reranker: small (~500 MB combined during build)
- Avoid running large HF causal LMs (model_native hooks) in parallel with full books_rag rebuild
- Run heavy jobs **serially** when VRAM is tight

---

## books_rag index location

**Never store Chroma on OneDrive.** OneDrive conflict copies corrupt HNSW binaries.

- Index data: `C:\books_rag` per machine (`BOOKS_RAG_DATA_DIR`)
- Shared corpus: `20_knowledge/wiki/sources/books_md` (OneDrive OK)
- Each machine runs its own GPU rebuild once; manifest/progress live under `BOOKS_RAG_DATA_DIR`

Verify after rebuild:

```powershell
python 40_operations/scripts/books_rag_verify.py --json
```

---

## CPU fallback

When CUDA is unavailable, `resolve_device("auto")` returns `cpu` and logs a warning if `cuda` was explicitly requested. Builds and retrieval remain functional, slower.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
