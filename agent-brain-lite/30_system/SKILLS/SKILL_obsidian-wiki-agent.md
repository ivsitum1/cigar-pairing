---
name: obsidian-wiki-agent
description: >-
  Full Obsidian-aware agent workflow: vault wiki maintenance under 20_knowledge/wiki,
  ingest/index/log, graph checks, plus Obsidian syntax (wikilinks, embeds, callouts,
  Canvas, Bases, URIs, frontmatter) via reference playbook.
version: 2.2
last_updated: 2026-05-18
domain: tools
tokens: ~550
triggers:
  - obsidian wiki
  - Obsidian ingest
  - wiki ingestion
  - wikilink graph
  - wiki health check
  - wiki lint
  - graph connectivity
  - Karpathy wiki
  - second brain
  - LLM Wiki Mode
  - Obsidian tricks
  - Obsidian skill
  - Obsidian flavored markdown
  - OFM
  - wikilink
  - callout
  - transclusion
  - JSON Canvas
  - canvas file
  - Obsidian Bases
  - vault note
  - PKM
  - osobna baza znanja
  - napravi bilješku Obsidian
  - Obsidian URI
requires_packages: []
reference_files:
  - ../docs/KARPATHY_WIKI.md
  - reference/OBSIDIAN_AGENT_PLAYBOOK.md
  - reference/obsidian_literature/README.md
  - reference/obsidian_literature/CLAIM-EXTRACTION.md
  - reference/obsidian_literature/RESEARCH-GAPS.md
pipeline_position: []
conflicts_with: []
---

# Skill: Obsidian wiki agent (Cursor)

**Purpose:** Keep this workspace’s markdown graph Obsidian-friendly while running ingestion and maintenance. Includes **syntax and product tricks** by loading `reference/OBSIDIAN_AGENT_PLAYBOOK.md` when the task is not only procedural but also about formatting, Canvas, Bases, or links.

---

## When to use

- **Wiki ops:** ingest material, update `index.md` / `log.md`, connectivity audit.
- **Literature vault flow:** project-scoped papers → synthesis notes → writing handoff; load `reference/obsidian_literature/` when user asks for literature workflow, claim map, or evidence-gated gaps.
- **Obsidian craft:** wikilinks, embeds, callouts, block refs, frontmatter, Mermaid, tasks, Canvas JSON, Bases files, URIs.
- User names **Obsidian**, **PKM**, **second brain**, **tricks**, **vault**.

**Not for:** statistical analysis, manuscript IMRaD drafting, software PRD loops.

**Graph exclude:** `90_archive/imports/` is ignored in Obsidian (`.obsidian/app.json`) and in Python graph scripts (`_graph_paths.py`). Staging `SKILL.md` files are not brain skills; see [[Archived skills staging]].

---

## Prerequisites

- **Paths:** Default wiki root is `20_knowledge/wiki/` in this brain; derivative projects may use `knowledge_system/` per `30_system/docs/KARPATHY_WIKI.md` when user confirms that layout.
- **Inputs:** Source material (chat attachment, paths, or inbox files) the user wants ingested or edited; unclear targets require one clarifying question before bulk edits.
- **Python:** `python` available on PATH when running `40_operations/scripts/obsidian_connectivity_check.py` (Workflow B).
- **Risky ops:** `obsidian_workspace_rewrite.py` or mass renames only with **explicit user consent** (wide impact).
- **Optional:** Obsidian desktop/mobile for human preview; the agent works on plain markdown and JSON Canvas/Bases files regardless.
- **Context budget:** YAML `tokens` estimates this file only; loading `reference/OBSIDIAN_AGENT_PLAYBOOK.md` (Stage 3) adds roughly several hundred extra tokens when syntax or Canvas/Bases work is in scope.

---

## Progressive disclosure (mandatory)

1. **YAML scan only:** if triggers match, continue.
2. **Always load** this file body (workflow below).
3. **Load playbook** `30_system/SKILLS/reference/OBSIDIAN_AGENT_PLAYBOOK.md` when any apply:
   - user asks how to format something in Obsidian;
   - editing `.canvas` or `.base` files;
   - fixing broken wikilinks / callouts / YAML;
   - user says “tricks”, “syntax”, “OFM”, “embed”, “transclusion”.
4. Load `30_system/docs/KARPATHY_WIKI.md` when vault layout uses `knowledge_system/` from `project_init.py`.

---

## Canonical paths (agent-rules workspace)

| Role | Path |
|------|------|
| Wiki root | `20_knowledge/wiki/` |
| Subfolders | `entities/`, `concepts/`, `sources/`, `analysis/` |
| Hub index | `20_knowledge/wiki/index.md` |
| Maintenance log | `20_knowledge/wiki/log.md` |
| Routing concept | `20_knowledge/wiki/concepts/Obsidian-centered agent routing.md` |

**Wikilink hubs (Obsidian graph):** [[OBSIDIAN_AGENT_PLAYBOOK]] (syntax and Canvas or Bases habits), [[Claude agent Obsidian wiki workflow]] (single-page agent summary).

---

## Workflow A — Ingest or restructure notes

1. Read `20_knowledge/wiki/index.md`.
2. Decompose input into atomic notes; pick subtree (`concepts/`, `entities/`, `sources/`, `analysis/`).
3. Apply playbook rules for links, frontmatter, callouts, embeds.
4. Canonicalize titles; use `aliases` in YAML when one concept has several names.
5. Update `index.md` for hub-level topics; append `log.md` with inputs, outputs, decisions.

---

## Workflow B — Graph health (semantic linking)

From repo root:

```text
py -3 40_operations/scripts/generate_folder_md_indexes.py --root .
py -3 40_operations/scripts/wiki_semantic_link.py --root . --dry-run
py -3 40_operations/scripts/wiki_semantic_link.py --root . --apply --regenerate-reference-index
py -3 40_operations/scripts/wiki_semantic_link.py --root . --apply --embeddings
py -3 40_operations/scripts/wiki_skill_reference_graph.py --root . --apply
py -3 40_operations/scripts/generate_code_bridge_clusters.py --root .
py -3 40_operations/scripts/validate_code_bridge_clusters.py --root .
py -3 40_operations/scripts/obsidian_connectivity_check.py --root .
```

**Semantic layer:** path buckets + token overlap → `

## Skill reference graph (auto)

- [[CLAIM-EXTRACTION]]
- [[RESEARCH-GAPS]]
- [[KARPATHY_WIKI]]
- [[OBSIDIAN_AGENT_PLAYBOOK]]
- [[README]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
