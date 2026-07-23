---
title: Nasljeđivanje agent rules (roditelj)
category: doc
tags: [parent, inheritance, agent-rules]
---

# Dijete nasljeđuje roditelja (agent rules)

Brain-lite **nije izoliran** — koristi skills i Cursor rules iz agent rules. Lite dodaje uredski orkestrator (4 čvora) i lokalni Markdown wiki.

## Jednokratni setup

```powershell
copy .env.example .env
python scripts/link_parent.py
```

`.env`:

```
PARENT_BRAIN_PATH=C:\Users\Ivan\OneDrive\Dokumenti\agent rules
```

## Što se poveže

| Iz agent rules | U brain-lite |
|----------------|--------------|
| `.cursor/rules/*.mdc` (bez parent orkestratora) | symlink u `.cursor/rules/` |
| `30_system/SKILLS/`, `behavior_rules/` | junction `30_system/` |
| `.cursor/mcp.json` | symlink (NotebookLM, PubMed, books_rag, …) |
| `.cursor/docs/` | junction |

**Isključeno:** `00_orchestrator_agent.mdc` — zamijenjen lite `00_orchestrator.mdc`.

## Dva sloja skills

1. **Parent** — `30_system/SKILLS/registry.json` + `skills-auto-detect.mdc` (meta-analiza, pisanje, pravo, Swiss Cheese, …)
2. **Lite overlay** — `skills/registry.json` (wiki-ingest, wiki-query, project-setup)

## Read-only

Ne mijenjaj datoteke u `PARENT_BRAIN_PATH` iz lite projekta. Wiki i `01_work/` su tvoji.

## Ažuriranje parent veze

Nakon `git pull` u agent rules (kad dodate git):

```powershell
python scripts/link_parent.py
```
