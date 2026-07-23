---
title: Agent Rules (roditeljski mozak)
category: entity
tags: [entity, parent, escalation]
summary: Puni agent-rules repo za duboko znanje i istraživačke pipelinee.
created: 2026-06-12
---

# Agent Rules — roditeljski mozak

Putanja: `PARENT_BRAIN_PATH` u `.env`. Povezivanje: `python scripts/link_parent.py`.

## Što lite nasljeđuje (ne samo eskalacija)

- `30_system/SKILLS/` — svi parent skills
- `.cursor/rules/` — parent Cursor rules (osim parent orkestratora)
- `.cursor/mcp.json` — NotebookLM, PubMed, books_rag, …

## Lite dodaje

- 4 uredska čvora, lokalni wiki (`knowledge/`), overlay skills (wiki-ingest, wiki-query, project-setup)

Detalji: [[docs/PARENT_BRAIN]]
