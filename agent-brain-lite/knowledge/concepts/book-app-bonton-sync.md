---
title: Knjiga bontona ↔ app
category: domain
tags: [bonton, book, sync]
updated: 2026-08-22
---

# Sinkronizacija knjige i app bontona

## Izvori

- **Knjiga:** `docs/bonton/HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md` (EN, puni rukopis)
- **App:** `app/src/data/bonton.json` — 11 poglavlja, dvojezično HR/EN, format `Odjeljak\n• stavka`

## Pravilo destilacije

App nije sažetak cijele knjige — to su **operativna poglavlja** za Klub. Duga narativna poglavlja rukopisa ulaze u app samo kad imaju kratke, ponovljive precepte.

## Mapa (održavati u `docs/bonton/README.md`)

| Rukopis | App / Club |
|---------|------------|
| I–V spirit, space, offer… | `b-spirit` … `b-table` |
| Host / guest + nicotine | `b-host` |
| Lounge | `b-lounge` |
| Outdoors + foreign table | `b-outdoors` + `t-foreign-table` |
| Gift | `b-gift` |
| Words for the table | `lexicon` → `rijeci-za-stol` (ne duplicirati u rječnik) |

## Testovi

- `bonton.test.ts` — fiksno 11 chapter id-ova
- `parseLessonBody` — svako poglavlje mora imati odjeljak s bulletima
