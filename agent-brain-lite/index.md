---
title: Master Index
category: meta
tags: [index, orchestrator, wiki]
created: 2026-06-12
updated: 2026-06-12
---

# Agent Brain Lite — Master Index

Lagani agentic mozak za uredske, medicinsko-znanstvene i izdavačke zadatke. Wiki stranice su Markdown s YAML frontmatter; Cursor pravila ostaju `.mdc`.

## Neural Network čvorovi

| Čvor | Uloga | Triggeri |
|------|-------|----------|
| [[nodes/00_orchestrator\|00 Orchestrator]] | Klasifikacija i routing | Svi zahtjevi |
| [[nodes/01_admin\|01 Admin]] | Ured, datoteke, checkliste | organiziraj, arhiva, rok |
| [[nodes/02_writer\|02 Writer]] | Email, memo, sažeci | napiši, draft, korekcija |
| [[nodes/03_automation\|03 Automation]] | Skripte, CSV, PowerShell | skripta, automatiziraj |
| [[nodes/04_research\|04 Research]] | Lookup, NotebookLM | istraži, provjeri, literatura |

## Skills (proceduralni workflowi)

- [[skills/wiki-ingest/SKILL\|wiki-ingest]] — dodaj sadržaj u wiki
- [[skills/wiki-query/SKILL\|wiki-query]] — pretraži wiki (RAG-lite)
- [[skills/project-setup/SKILL\|project-setup]] — koloniraj mozak u projekt
- Parent: `notebooklm-research-gate` u `30_system/SKILLS/` (nakon `link_parent.py`)

## Znanje (domena)

- [[knowledge/concepts/medicinsko-izdavastvo\|Medicinsko izdavaštvo — osnove]]
- [[knowledge/concepts/znanstvena-komunikacija\|Znanstvena komunikacija — osnove]]
- [[knowledge/references/pravo-osnove\|Pravo — bazalni pojmovi (ne pravni savjet)]]
- [[knowledge/entities/agent-rules-parent\|Agent Rules (roditeljski mozak)]]

## Sustav

- [[harness/LAYERS\|Harness — 4 sloja]]
- [[_meta/neural_map\|Neural map (graf čvorova)]]
- [[_meta/taxonomy\|Taxonomy (tagovi)]]
- [[docs/PROJECT_SETUP\|Upute: koloniranje u projekt]]
- [[docs/PARENT_BRAIN\|Nasljeđivanje agent rules (skills + rules)]]
- [[harness/LEARNING_LOOP|Learning loop (3 sloja)]]
- [[knowledge/learnings/LEARNING_BLOCK_TEMPLATE|LEARNING_BLOCK predložak]]
- [[hot]] — session cache
- [[log]] — aktivnost
