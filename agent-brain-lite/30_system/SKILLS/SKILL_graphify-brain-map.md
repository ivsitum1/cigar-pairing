---
name: graphify-brain-map
description: >-
  Query the agent-rules brain as a structural knowledge graph (code, rules, skills,
  MCP, hooks). Use for architecture questions, cross-file connections, god nodes,
  and token-efficient codebase navigation. Complements wiki/TGS (curated knowledge)
  and memory_engine (session events). Requires graphify-out/graph.json.
version: 1.0
last_updated: 2026-06-06
domain: engineering
tokens: ~480
triggers:
  - graphify
  - brain map
  - codebase graph
  - architecture query
  - god nodes
  - structural index
  - what connects
  - shortest path
  - graph query
  - map the brain
  - graphify query
  - knowledge graph brain
requires_packages:
  - graphifyy
  - ollama
reference_files:
  - ../docs/GRAPHIFY_BRAIN_INTEGRATION.md
pipeline_position: []
conflicts_with: []
disambiguation: >-
  Use for repo structure / cross-module wiring in agent-rules (or project brain
  folder). NOT for Obsidian wiki content (obsidian-wiki-agent), session memory
  (memory MCP), or textbook lookup (books_rag). NOT a substitute for user-facing
  wiki ingest.
---

# Skill: Graphify brain map

**Purpose:** Navigate the **mozak** (agent-rules) by **structure**: AST, imports, MCP configs, skill registry links, hook wiring. Reduces grep/read loops for "what connects X to Y?".

**Upstream:** [Graphify](https://github.com/safishamsi/graphify) (PyPI `graphifyy`, MIT). Brain integration doc: `30_system/docs/GRAPHIFY_BRAIN_INTEGRATION.md`.

---

## When to use

- User asks how rules, skills, scripts, or MCP servers **connect**.
- Orchestrator/CODE_IMPL needs **scoped context** before wide grep or serial Read.
- Rebuild or refresh structural index after major refactors.
- Compare `GRAPH_REPORT.md` god nodes with expected hubs (orchestrator, registry, memory).

**Not for:** clinical facts, manuscript prose, wiki curation, session recall, R analysis logic (`.R` weakly covered by Graphify).

---

## Prerequisites

1. **Package:** `pip install "graphifyy[mcp,ollama]"`.
2. **Full build:** Ollama + **`gemma4:latest`** (Gemma 4, 8B, local; `ollama pull gemma4:latest`).
3. **Graph artifact:** `graphify-out/graph.json` (run build script below if missing).
4. **MCP (optional):** `graphify` server in `.cursor/mcp.json`.

---

## Layering (do not confuse)

| Layer | Tool | Remembers |
|-------|------|-----------|
| Session | `memory` MCP | events, injections |
| Curated | wiki + TGS RAG | distilled concepts |
| **Structure** | **Graphify** | code/rules/skills wiring |

Prefer `graphify query` **before** reading many source files for architecture questions.

---

## Workflow

### A. Build or refresh graph

From repo root (agent-rules):

```powershell
python 40_operations/scripts/graphify_brain_build.py --force
```

Options:

- `--update` — incremental refresh.
- `--force` — overwrite after refactors.
- `--full` — semantic doc extract via **local Ollama** (default; no Anthropic/OpenAI).

Outputs: `graphify-out/graph.json` (always). `GRAPH_REPORT.md` / clustering with `--full` (slow; ~1500 doc chunks).

### B. Query (CLI)

```powershell
graphify query "what connects orchestrator to memory hooks?"
graphify path "memory_server" "memory_lifecycle"
graphify explain "skill_rerank"
```

PowerShell: use `graphify query "..."` not `/graphify query` (leading `/` is a path separator).

### C. Query (MCP)

1. Call `graph_status` — confirms graph exists and node count.
2. Call `query_graph(question=...)` for subgraph answers.
3. Use `graph_path(from_node=..., to_node=...)` for wiring between named entities.

### D. Merge with wiki (structure + curated knowledge)

```powershell
python 40_operations/scripts/graphify_wiki_merge.py
```

Uses `wiki-export/graph.json` (wikilinks from `20_knowledge/wiki/`, excludes `books_md`) merged into `graphify-out/merged.json`. MCP `graphify` prefers `merged.json` when present.

Options: `--skip-structural` (reuse existing graph.json), `--filtered-wiki` (exclude internal/pii pages).

---

## Maintenance

- **Post-commit AST refresh:** installed via `graphify hook install` (appended to `.git/hooks/post-commit`). Skip with `GRAPHIFY_SKIP_HOOK=1 git commit`.
- After large moves: `graphify_brain_build.py --force`.
- After wiki ingest: `graphify_wiki_merge.py --skip-structural`.
- Stale graph: check `graphify-out/manifest.json` mtime vs last refactor.

---

## Security

- Code stays local (Tree-sitter). `--full` uses **Ollama on localhost** only; no cloud API by default.
- Respect `.graphifyignore`; do not index `90_archive/` or `.agent/memory/`.

## Semantic graph (auto)

- [[Wiki semantic graph linking]]
- [[Obsidian-centered agent routing]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
