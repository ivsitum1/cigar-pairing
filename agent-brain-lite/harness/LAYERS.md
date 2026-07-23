---
title: Harness — 4 sloja
category: meta
tags: [harness, layers]
---

# LifeHarness — lite verzija (4 sloja)

Pojednostavljeno iz agent rules `LIFEHARNESS_4_LAYER.md`. Bez Python hookova i SQLite memorije.

| Sloj | Svrha | Lite artefakt |
|------|-------|---------------|
| 1 — Environment | MCP ugovori | `.cursor/mcp.json` (symlink → agent rules) |
| 2 — Procedural Skill | Workflowi | `30_system/SKILLS/` (parent) + `skills/` (lite overlay) |
| 3 — Action | Izvršenje | Cursor alati, `scripts/project_init.py` |
| 4 — Trajectory | Kontinuitet | `.agent/MEMORY.md`, [[hot]], `.agent/task/`, `.agent/learning.jsonl` |

Learning loop: [[LEARNING_LOOP]] (3 sloja).

## RAG-lite

Pretraga Markdown wiki: YAML frontmatter (`title`, `tags`, `summary`) + grep po `knowledge/`. Nema vektorskog indeksa.
