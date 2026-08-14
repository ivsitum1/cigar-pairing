# Synthesis — World Atlas of Coffee → pairing / Club (2026-08-12)

**Notebook:** [The World Atlas of Coffee](https://notebook.google.com/notebook/e2f2af38-1d1a-4f81-bb02-d841e760d627) (`e2f2af38`)  
**MCP id (proposed):** `world-atlas-of-coffee`  
**Sources:** 2  
**Raw:** `e2f2af38-RAW-2026-08-12.md`

> **VERIFIED** = grounded in NotebookLM answer with citations to Hoffmann corpus · **INFERRED** = cigar / Club application  
> Attribute coffee science to Hoffmann. Do **not** treat cigar scores as book content.

---

## 1. Što je ova bilježnica

**VERIFIED:** Hoffmann *World Atlas of Coffee* (beans → brew): perception, origins, process, roast, brew TDS, defects.

**Ne koristiti za:** brand rankings; “cigar chapter”; marketing roast names as quality hierarchy.

---

## 2. Usklađenost s appom (već ugrađeno)

| Artefakt | Status vs grill |
|----------|-----------------|
| `coffeePairingModel.json` | **Aligns** with Pass A–C (perception, families, defects, origins, body-first) |
| `engine/coffeePairing.ts` | **Aligns** soft overlay: roast/intensity/acidity/family; high-TDS styles; body priority |
| `coffees.json` (33) | Catalog present |
| Club `d-coffee` | **Implemented** 2026-08-12 (`d-wine-table`, `d-tequila` same batch) |
| Tip `t-coffee-espresso` | Exists; keep complementary to `d-coffee` |

**Verdict:** pairing model did **not** need a fresh NotebookLM dump to exist — dump **validates** it and adds Club/wrapper teaching layer.

---

## 3. Feed mapa

| Sloj | Što uzeti | Status |
|------|-----------|--------|
| Pairing engine | Keep body-first; B/I/F style weights; don’t invent new hard scores from chat formulas without tests | soft — empirical validate |
| Catalog tags | **Audited** 2026-08-12: +americano, +Burundi, +Panama Geisha; Sumatra duhan/drvo; `coffees.catalog.test.ts` |
| Club 101 `d-coffee` | Pass D–E bullets + brew styles + pace + water | **Done** — styles, pace, bridges, NO-list, house craft |
| Club facts | defects NO-list; roast date; 60 g/L; clean gear; water | **Done** 2026-08-14 — `d-coffee` -> „Kucni zanat” / „House craft” |
| Hard filters | Never promote phenolic / potato / wild ferment / vinegary under-extract / ashy over-extract as “character” | editorial rule |

---

## 4. Wrapper bridges (INFERRED — UI hints, not gospel)

| Wrapper | Coffee archetype | Confidence |
|---------|------------------|------------|
| Connecticut | Washed CA light/sweet (Costa Rica–type) | medium |
| Cameroon | Kenya / high-acid berry | medium |
| Habano | Semi-washed Sumatra tobacco/spice | medium–high (note overlap) |
| Maduro | Brazil nutty-cocoa ± darker roast | medium |

Use as **hints** in Club / blurbs; engine already body-matches — don’t hardcode wrapper→origin without tests.

---

## 5. Club 101 outline (from Pass E)

Practical Pića-track lesson (HR/EN), distinct from tip espresso essay:

1. Styles: espresso / ristretto / lungo / filter / americano / milk — what each does to body & bitterness  
2. Pace: warm not scalding; alternate gutljaj; water resets, acid coffee cleanses  
3. Bridges: CT / Cameroon / Habano / maduro archetypes (one line each)  
4. Avoid: defects + syrup-sweet milk drowning a mild cigar  
5. House craft: roast date, grind fresh, clean gear, decent water  

Finite verbs (HR canon). No infinitive stacks.

---

## 6. Adversarial / honesty

- NotebookLM labels some brew TDS numbers with citations — treat as **model-cited**, still verify against book if weights change.  
- Smoke-pace and wrapper map are **INFERRED**; say so in product copy.  
- MCP auth still broken for this account path; grill used Cursor browser session logged in as project owner.

---

## 7. Next actions

1. ~~Implement `d-coffee` (+ `d-wine-table` / `d-tequila`)~~ done 2026-08-12.  
2. ~~Optional: audit `coffees.json` tags vs regional grill map.~~ done 2026-08-12.  
3. `e2f4c754` = same notebook (alternate URL); no separate grill needed.  
4. ~~Club facts -> house craft in `d-coffee`~~ done 2026-08-14 (roast date, grind, 60 g/L, clean gear, water, bean storage).  
5. ~~Catalog: split prep / roast / bean~~ done 2026-08-14 (`style` = prep, `roast`, `species` + `country`; instant added).
