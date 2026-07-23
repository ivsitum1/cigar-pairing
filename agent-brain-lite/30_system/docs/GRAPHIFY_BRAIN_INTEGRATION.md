# Graphify brain integration

**Version:** 1.0 | **Date:** 2026-06-06  
**Skill:** `30_system/SKILLS/SKILL_graphify-brain-map.md`  
**Upstream:** [Graphify](https://github.com/safishamsi/graphify) · [graphify.net](https://graphify.net/)

---

## Role in the mozak

Graphify adds a **structural memory layer** for the agent-rules repository. It does not replace:

| Layer | Location | Role |
|-------|----------|------|
| Session memory | `memory_engine/`, MCP `memory` | lifecycle events, injection |
| Curated wiki | `20_knowledge/wiki/` | distilled knowledge, wikilinks |
| TGS RAG | `tgs_rag.py` | wiki text + graph hybrid retrieval |
| books_rag | MCP `books_rag` | textbook vector search |

Graphify indexes **wiring**: rules, skills, Python/R scripts, MCP configs, hooks.

---

## Artifacts

```
graphify-out/
├── graph.json          # queryable graph (~local build; gitignored — 20+ MB)
├── GRAPH_REPORT.md     # god nodes (--full build only)
├── graph.html          # optional browser viz
├── manifest.json       # incremental cache anchor
└── cost.json           # local only — gitignored
```

Ignore rules: `.graphifyignore` (excludes `90_archive/`, wiki prose, books_md, memory DB).

---

## Setup (once per machine)

```powershell
pip install "graphifyy[mcp,ollama]"
python 40_operations/scripts/graphify_brain_build.py --force
```

Default: **code-only AST** (offline). **Full semantic docs (local Ollama, no cloud API):**

```powershell
# Ollama must be running; default model gemma4:latest (Gemma 4, 8B, local)
python 40_operations/scripts/graphify_brain_build.py --full --force
```

Optional:

```powershell
python 40_operations/scripts/graphify_brain_build.py --full --force --model gemma4:latest
$env:OLLAMA_MODEL = "gemma4:latest"
$env:GRAPHIFY_OLLAMA_NUM_CTX = "8192"   # lower if GPU RAM is tight
```

Install model if missing: `ollama pull gemma4:latest` (requires Ollama 0.20+).

Cloud backends (only if explicitly requested): `--backend gemini` + `GEMINI_API_KEY`, etc.

`--full` temporarily swaps `.graphifyignore` with `.graphifyignore.full` (allows `.md` in rules/skills/docs; wiki still via `graphify_wiki_merge.py`).

Optional post-commit AST refresh (installed):

```powershell
graphify hook install   # already applied — appends to .git/hooks/post-commit
GRAPHIFY_SKIP_HOOK=1 git commit   # skip one commit
```

Merge structure + wiki (+ wiki↔code bridges):

```powershell
python 40_operations/scripts/graphify_wiki_merge.py
python 40_operations/scripts/graphify_wiki_bridge.py --dry-run   # preview only
python 40_operations/scripts/graphify_merge_verify.py
```

---

## MCP

Server: `.cursor/mcp_servers/graphify_server.py` (registered as `graphify` in `.cursor/mcp.json`).

| Tool | Purpose |
|------|---------|
| `graph_status` | graph exists? size, mtime |
| `query_graph` | natural-language subgraph |
| `graph_path` | shortest path between nodes |
| `graph_explain` | node neighborhood |

---

## Agent routing

- **Architecture / "what connects X to Y?"** → Graphify MCP or CLI first; then targeted Read.
- **Domain knowledge / literature** → wiki-query, research-lookup, books_rag.
- **Session history** → memory MCP.

Cursor rule: `.cursor/rules/graphify-brain.mdc` (`alwaysApply: false`; loaded via skill triggers).

---

## POC success criteria

1. `graphify-out/graph.json` exists with >100 nodes on agent-rules.
2. `GRAPH_REPORT.md` lists orchestrator, registry, or memory-related god nodes.
3. `graphify query "orchestrator memory hooks"` returns a coherent subgraph.
4. MCP `graph_status` returns `status=ready`.

---

## Future (optional)

- ~~Extend TGS RAG to consume `graphify-out/merged.json`~~ — done: `tgs_rag.py` + `merged_graph_index.py`
- ~~Wiki↔code bridge edges~~ — done: `graphify_wiki_bridge.py` (auto-run from `graphify_wiki_merge.py`)
- `brain_health.py` warn if manifest older than 30 days

## Git hooks

`graphify hook install` appends to `.git/hooks/post-commit` and installs `post-checkout`. Rebuilds code graph after each commit (AST only, `PYTHONHASHSEED=0`). Skip: `GRAPHIFY_SKIP_HOOK=1`.

## Wiki merge pipeline

| Script | Output |
|--------|--------|
| `wiki_export_graph.py` | `wiki-export/graph.json` (concepts/entities/analysis; no books_md) |
| `graphify_wiki_merge.py` | `graphify-out/merged.json` (structural + wiki + bridges) |
| `graphify_wiki_bridge.py` | adds `bridges_to` edges on merged.json |
| `graphify_merge_verify.py` | integrity + query smoke test |

MCP `graphify` uses `merged.json` when it exists.

---

## Related

- [[Text-graph RAG synergy]]
- [[LifeHarness four-layer model]]
- `30_system/docs/MEMORY_SYSTEM.md`
- `30_system/docs/BRAIN_AND_PROJECT.md`
