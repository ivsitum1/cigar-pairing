# Books RAG — canonical paths

**Version:** 1.0 | **Updated:** 2026-06-01

Single reference for agents, MCP, and scripts after migration off OneDrive.

| Role | Path | Notes |
|------|------|--------|
| **Index root** | `C:\books_rag` (Windows default) | Set `BOOKS_RAG_DATA_DIR` in `.env` |
| Chroma store | `%BOOKS_RAG_DATA_DIR%\chroma\` | Never sync via OneDrive |
| Manifest | `%BOOKS_RAG_DATA_DIR%\manifest.json` | |
| Build progress | `%BOOKS_RAG_DATA_DIR%\build_progress.json` | |
| Eval report | `%BOOKS_RAG_DATA_DIR%\eval_report.json` | |
| Install status | `%BOOKS_RAG_DATA_DIR%\install_status.json` | |
| Build lock | `%BOOKS_RAG_DATA_DIR%\.build.lock` | |
| **Corpus (shared)** | `20_knowledge/wiki/sources/books_md/` | OK on OneDrive |
| **Repo redirect** | `data/books_rag/README.md` | No chroma here |

## Environment

```env
BOOKS_RAG_DATA_DIR=C:/books_rag
```

Windows user env (optional, persistent):

```powershell
setx BOOKS_RAG_DATA_DIR C:\books_rag
```

## Code resolution

- Python: `books_rag.config.load_config()` → `cfg.data_dir`
- PowerShell: dot-source `40_operations/scripts/_books_rag_paths.ps1` → `$BooksRagDataDir`
- MCP: `.cursor/mcp.json` → `books_rag.env.BOOKS_RAG_DATA_DIR`

## Fused channel

- Module: `40_operations/python/brain_assist/fused_rag.py`
- MCP: `search_fused_rag` on `books_rag` server
- CLI: `python 40_operations/scripts/fused_rag_search.py -q "..." --json`

## Verify

```powershell
python 40_operations/scripts/books_rag_verify.py --json
python 40_operations/scripts/fused_rag_search.py -q "hybrid retrieval" --json
```

## Migrate / clean legacy OneDrive index

```powershell
.\40_operations\scripts\books_rag_migrate_off_onedrive.ps1 -SetUserEnv
```

See also: [BOOKS_RAG.md](BOOKS_RAG.md), [GPU_COMPUTE_POLICY.md](GPU_COMPUTE_POLICY.md).
