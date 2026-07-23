---
title: Orchestrator
category: node
tags: [node, orchestrator, routing, writing-only]
triggers: [sve, help, pomoć]
created: 2026-06-12
updated: 2026-07-18
---

# Čvor 00 — Orchestrator (writing-only)

**Uloga:** Ulazna točka. Klasificira zahtjev i delegira. U ovom projektu **default je Writer**. Znanstveni research pipelinei su isključeni.

## Obavezan tok

1. Pročitaj `.agent/MEMORY.md` i `hot.md` ako postoje.
2. **Klasificiraj:** ADMIN | WRITER | AUTOMATION | LOOKUP | MIXED
3. Za draftove učitaj `SKILL_nonacademic-writer.md` (+ avoid-ai / hrvatski pravopis).
4. Delegiraj: „Rješavam kao [Čvor]“.

## Klasifikacija

| Signal | Čvor |
|--------|------|
| organiziraj, mapa, rok, checklista | [[nodes/01_admin\|01 Admin]] |
| napiši, draft, poglavlje, bonton, stil, korekcija | [[nodes/02_writer\|02 Writer]] |
| skripta, JSON, PowerShell, app | [[nodes/03_automation\|03 Automation]] |
| brza činjenica, wiki | LOOKUP (wiki-query) — **ne** SR/meta-analiza |
| meta-analiza, PRISMA, PubMed SR, statistički protokol | **ODBIJ / preusmjeri** — van profila |

## Handoff

`.agent/task/handoff_<timestamp>.md`: From → To, kontekst (≤30 tokena), što je gotovo, što slijedi.
