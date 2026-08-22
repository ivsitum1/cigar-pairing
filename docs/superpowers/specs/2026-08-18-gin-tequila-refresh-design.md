# Gin + tequila refresh — design (val C)

**Date:** 2026-08-18  
**Status:** approved (user chose C — oboje, tekila prva)  
**Scope:** HR katalog pića + pairing note sloj (`notes`, `cigarHint`, profili). **Ne** puni rescrape Kluba/bontona.

## Goal

Obnoviti **gin** i **tekilu** u app katalogu koristeći postojeći scrape → Excel → JSON pipeline, nadopunjen W2 PDP obogativanjem i (gdje treba) **pagefetch** za product stranice. Cilj je:

1. Svježe cijene i `priceUrl` s HR shopova.
2. Kalibrirani profili (`profileEstimated: false` gdje je moguće).
3. Per-bottle **`cigarHint` HR+EN** i duže **`notes`** — posebno tekila (danas 0/26 hintova).
4. Čišći katalog (META duplikati, poklon setovi van pairing poola).

## Non-goals

- Promjena pairing enginea (`pairing.ts`, `rules.ts`, `curatedOpinion.ts` logika ostaje).
- Rescrape Club 101 / `club.json` / bonton knjige.
- Affiliate / više shopova na kartici (jedan `priceUrl` po boci, kao danas).
- Mezcal kao zasebna app kategorija (ostaje pod tequila s `style: mezcal`).

## Global constraints

- **Id stabilnost:** nikad brisati `id` bez unosa u alias JSON-a (nema drink alias datoteke danas — preferiraj `meta: true` + zadrži id).
- **HR copy:** `.cursor/rules/hr-copy-canon.mdc` — *cigara* padeži, *dim* vs *draw*, finite glagoli u hintovima.
- **Pairing copy:** `curatedOpinion.ts` **ne čita** `drink.cigarHint`; hint ide u DetailSheet / karticu pića, ne u engine poruke.
- **Ne izmišljati:** scrape/merge skripte ne smiju fabricirati tasting note ako stranica ne daje tekst.
- **CI gate:** `npm test`, `npx tsc -b --noEmit`, postojeći integrity testovi pića.
- **Excel lokalno:** `Gin_Kolekcija_Checklist.xlsx` / `Tequila_Kolekcija_Checklist.xlsx` u korijenu repoa — git-ignorirani; JSON u `app/src/data/` je izvor istine za app.

## Current baseline (2026-08-18)

| Metrika | Gin (65) | Tequila (26) |
|---------|----------|--------------|
| `profileEstimated: false` | 65/65 | 9/26 |
| `cigarHint` HR | 65 (22 unique) | 0 |
| `cigarHint` EN | 19 | 0 |
| `notes.hr` ≥ 80 znakova | ~4 | ~1 |
| `priceUrl` missing | 42 | 18 |
| META / gift noise | 18 META + 8 gift | 3 META + 5 gift |

Club 101: `d-gin-pairing`, `d-tequila` već postoje — **dovoljno** za edukativni sloj.

## Architecture

Tri sloja, isti redoslijed kao rum W2:

```
listing scrape → Excel MASTER (+ Serviranje + Cigare) → excel-to-*-json.py
                              ↓
                    PDP scrape (urllib / pagefetch)
                              ↓
              merge-drink-profile-enrichment.py + merge-drink-profiles.py
                              ↓
                    app/src/data/{gins,tequilas}.json
```

**pagefetch** (`sideprojects/pagefetch`) ulazi samo kao **fallback** na product URL kad `scrape-drink-product-pages.py` vrati prazan/opis ili HTTP block.

## Phase 1 — Tequila (priority)

### 1A Catalog refresh

- Pokrenuti `scrape-tequila-catalog.py` (allez + ecuga).
- `build-tequila-excel.py` — regenerira `Tequila_Kolekcija_Checklist.xlsx`.
- U Excelu:
  - **MASTER Ocjene:** sve 100% agave sipping boce s allez/ecuga (mixto / cocktail van).
  - **Katalog allez+ecuga:** puni URL + cijena.
  - **Serviranje + Cigare:** za svaku referentnu bocu — `cigarHint` HR (min. 80 znakova za top 12; ostatak stilski hint iz `cigar_hint_for_style` + 1 rečenica specifičnosti).
- `excel-to-tequila-json.py` — merge u `tequilas.json` (zadrži postojeće id gdje token match ≥ 2).

**Target:** 35–50 pairable bočica (sada 26), ≤5 META, 0 shop/url mismatch.

### 1B Profile enrichment (W2)

- `scrape-drink-product-pages.py --limit N` (samo `tequilas.json` s `priceUrl`).
- Ako urllib fail → `pagefetch` dump u `scripts/output/pdp_pagefetch/` pa ručno ili parser patch.
- `merge-drink-profile-enrichment.py` → tagovi/body/sweetness iz PDP teksta.
- `merge-drink-profiles.py --category tequila` → curated profile overrides.

**Target:** `profileEstimated: false` na ≥ 80% pairable bočica.

### 1C Pairing notes

- Excel sheet **Serviranje + Cigare** puni `cigarHint` + `notes.hr`.
- EN note/hint: u Excelu ili post-merge edit u JSON (paralelno HR).
- Stilski predlošci iz `tequila_shared.cigar_hint_for_style` — **proširiti** na 2–3 rečenice, ne jedna kratka fraza.
- Ažurirati `docs/tequila-cigar-pairing-notes.md` kao lookup (opcionalno, nije CI gate).

### 1D Quality gates

- Novi test `app/src/data/tequila.catalog.test.ts`:
  - svaka pairable boca: `notes.hr.length ≥ 40`, `cigarHint.hr.length ≥ 40`
  - referentni set (~12 id): `notes.hr ≥ 80`, EN isto
  - nema `shopHR` / `priceUrl` host mismatch
  - `profileEstimated !== true` za referentni set
- `npm test` + `tsc`.

## Phase 2 — Gin (polish + expansion)

### 2A Catalog refresh

- `scrape-gin-catalog.py` → `build-gin-excel.py` → MASTER.
- Cilj: pokriti allez listing (~70–90 SKU), ali pairing pool ostaje **qualityScore ≥ 7** (gift chooser već filtrira).
- Poklon setovi / minijature: `meta: true`, `pairable: false` ili ostaju ali bez duplikata META referentnih boca.

### 2B De-template cigarHint

- Problem: 23× isti „Connecticut / blagi Habano — gusta botanika”.
- Rješenje:
  - Referentne boce po stilu (London Dry, contemporary, mediterranean, croatian, plymouth) — **jedinstveni** hint HR+EN (≥ 80 znakova).
  - Ostatak: stilski hint + botanički tag iz profila (borovica, citrus, kamilica…), ne copy-paste.
- `gin_shared.cigar_hint_for_style` — proširiti na duže rečenice; Excel **Serviranje + Cigare** za top 15.

### 2C W2 + EN coverage

- Isti PDP pipeline kao tekila.
- Target: `cigarHint.en` i `notes.en` na svim pairable (≥ 40 znakova); referentni set ≥ 80.

### 2D Quality gates

- `app/src/data/gin.catalog.test.ts` — analogno tequili.
- Proširiti `curatedNotes.test.ts` s TEQUILA_CURATED_IDS + GIN_CURATED_IDS (po 12–15).

## Phase 3 — Club / bonton (touch-up only)

**Samo ako** katalog otkrije gap:

| Trigger | Akcija |
|---------|--------|
| ≥ 3 cristalino u katalogu | 1 fact u `club.json` (već postoji — provjeri) |
| Mezcal ≥ 3 pairable | 1 rečenica u `d-tequila` body (mezcal odlomak već postoji) |
| Novi HR gin brend (npr. lokalni) | 1 fact, ne cijeli rescrape |

Bez NotebookLM vala osim ako ručno tražiš dubinski essay.

## Success criteria

1. Tequila: ≥ 35 pairable, ≥ 12 referentnih s punim hint/note, 0 url/shop mismatch.
2. Gin: unique `cigarHint.hr` ≥ 40 od 65; EN coverage ≥ 90% pairable.
3. CI green (`npm test`, `tsc`).
4. Club/bonton JSON **netaknut** osim eventualne 1-linijske dopune.

## Risks

| Risk | Mitigation |
|------|------------|
| Excel nije u repou | Baseline snapshot `scripts/output/baseline_refresh_YYYYMMDD/` prije mergea |
| allez rate limit | `--resume`, pauza 1.8s, pagefetch samo za fail |
| Duplikat id pri mergeu | `excel-to-*` token overlap + ručni pregled META |
| Predloški hintovi | test minimalne duljine + curated id lista |

## Estimated effort

| Faza | PDP fetchovi | Ručni Excel | Agent/automation |
|------|--------------|-------------|------------------|
| Tequila | ~30–45 | 2–3 h (MASTER + hints) | 1 sesija |
| Gin | ~40–60 | 1–2 h (top 15 hints) | 1 sesija |
| Club touch-up | 0 | 15 min | optional |
