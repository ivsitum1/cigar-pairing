# Digestifs & regional specialties — shop audit

**Date:** 2026-07-27  
**Branch:** `research/digestifs-regional-liqueurs`  
**Scope:** neat-oriented herbal / regional bottles on **allez.hr** and **ecuga.com** that do **not** fit cleanly into rum / whisky / brandy / wine / coffee / tequila / gin.  
**Out of scope (per brief):** vermouth, cocktail bitters-as-mixer, cream liqueurs, RTD / punch / seasonal gin liqueurs.

## Method

| Source | What was done |
|--------|----------------|
| AlleZ | Scraped `https://allez.hr/shop/likeri` (69 SKUs, 6 pages) and `https://allez.hr/shop/absinthe-brandy-grappa-sake` (42 SKUs, 4 pages) → [`01_work/output/digestif_allez_raw.json`](../01_work/output/digestif_allez_raw.json) |
| Ecuga | Product pages verified via search + fetch (Becherovka, Agwa, Fernet, Unicum, Pelinkovac Aura, Chartreuse Yellow, Strega, Cynar, Averna, Dom Benedictine, Galliano, Absinthe) |
| [Wine-Searcher](https://www.wine-searcher.com/spirits) + [Drinkology](https://www.drinkology.de) | Style taxonomy (Liqueur–Herb–Spice / bitters digestifs), ABV cross-checks (e.g. Chartreuse Verte 55%, Averna 29%), national bitter map — full drink pass in [`DRINKS-WS-DRINKOLOGY-AUDIT.md`](DRINKS-WS-DRINKOLOGY-AUDIT.md) |
| App catalog | Grep of `app/src/data/*.json` — none of the shortlisted herbal digests appear as drink entries (only Club educational mentions) |

Scraped AlleZ prices were often blank in HTML listing (age-gate / lazy price); Ecuga prices below are from product pages as of 2026-07-27.

## Taxonomy gap (verified in code)

| Layer | Today | Effect on this domain |
|-------|--------|------------------------|
| `DrinkCategory` | 7 values, no digestif/herbal | No UI chip, no buffet five, no pairing filter |
| `shoppingPicks` brandy buckets | residual `liqueur` style under brandy | Only holds odd brandy-adjacent SKUs (e.g. Grand Marnier), not Becherovka-class bottles |
| `brandy_shared.py` | `NON_PAIRABLE_CATEGORIES` includes `liqueur`, `absinthe`, `pisco`, `sake` | Pipeline **discards** the interesting AlleZ “misc spirits” list |
| Club / Club101 | Facts already teach chartreuse-style herbs, aquavit, pastis, kirsch | Education ahead of catalog |

Conclusion: the shops **already stock** the category; the app **actively filters it out** of brandy and never created a home for it.

## AlleZ — what the likeri aisle actually is

Of 69 likeri SKUs, roughly **⅔ are out of brief** (cream, punch, seasonal light-up gin liqueurs, Disaronno, Fireball, Licor 43 family, coffee/chocolate cream, Choya umeshu, St. Germain, Grand Marnier/Drambuie).

**Neat / regional / herbal candidates on AlleZ:**

| Bottle | Why it matters | Buffet fit |
|--------|----------------|------------|
| Chartreuse Jaune / Verte | Monastic French herbal; no substitute | High |
| Dom Benedictine | Classic French herbal digestif | High |
| Strega Liquore | Italian saffron herbal; regional icon | High |
| Galliano L'Autentico | Italian yellow herbal; distinctive | Medium–high |
| Nonino Amaro Quintessentia | Amaro on grappa base; digestif culture | High |
| Tatratea (Apple & Pear 67%, Aronia 27%) | Slovak tea-herbal specialty | Medium (high ABV variants are “show” bottles) |
| Luxardo Maraschino | Unique cherry distillate/liqueur; more cocktail than cigar-neat | Low for this brief |
| Luxardo Bitter Bianco | Closer to aperitivo | Low (vermouth-adjacent use) |
| Slyrs Alpine Herbs | Alpine herbal, less iconic | Optional |
| Henry Bardouin Pastis | Anise ritual with water (AlleZ absinthe aisle) | Medium — aperitif ritual, Club already covers |
| Barsol Pisco (Quebranta, etc.) | Peruvian grape eau-de-vie; unique, not brandy | Medium — spirit, not herbal; brandy pipeline marks non-pairable |

Grappa on the same AlleZ list is **already covered** as brandy style `grappa` — not a gap.

## Ecuga — complementary shelf (herbal / national)

Verified product pages (shopHR = ecuga.com):

| Bottle | ABV | Price (page) | Region / identity | Neat? | Buffet fit |
|--------|-----|--------------|-------------------|-------|------------|
| Becherovka | 38% | 14 € | Czech national herbal bitter | Yes, cold | **Must** |
| Agwa de Bolivia | 30% | ~24 € | Coca-leaf herbal; essentially unique | Yes or cocktail | **Must** (uniqueness) |
| Branca Fernet | 35% | 24 € (1 L) | Italian fernet digestif | Yes, cold | **Must** |
| Unicum Zwack | 40% | 20 € | Hungarian national bitter | Yes | **Must** |
| Aura Pelinkovac Gorki | ~31% | 26 € | Croatian wormwood; Istria craft | Yes | **Must** (local) |
| Aura Pelinkovac Victoris | — | — | Premium HR pelinkovac | Yes | Strong alt |
| Chartreuse Yellow | 43% | 52 € | FR monastic (page: unavailable) | Yes | High (also AlleZ) |
| Dom Benedictine | — | — | FR herbal | Yes | High (also AlleZ) |
| Strega | 40% | 23 € | IT saffron herbal | Yes | High |
| Galliano Vanilla / L'Autentico | — | — | IT herbal-vanilla | Yes / cocktail | Medium |
| Averna Amaro | 29% | — | Sicilian amaro digestif | Yes / ice | High (ABV from Drinkology product page) |
| Cynar | 16.5% | 18 € (1 L) | Artichoke amaro | Yes / ice / mixer | Low–medium (ABV + aperitivo use) |
| Jacques Senaux Green Absinthe | 70% | — | Absinthe ritual | With water | Edge case |
| Mr. Jekyll Absinthe | 55% | — | Absinthe | With water | Edge case |

**Not found on AlleZ (or not in scraped likeri):** Becherovka, Agwa, Fernet Branca, Unicum, Aura Pelinkovac — Ecuga fills that Central/SE European gap.

## Shortlist for experiment (12)

Priority = unique regional identity + neat culture + HR availability + not already a first-class app category.

| # | Style bucket | Representative bottle | Shop | Notes |
|---|--------------|----------------------|------|-------|
| 1 | Czech herbal | Becherovka | ecuga | National; cheap entry |
| 2 | Coca-leaf herbal | Agwa de Bolivia | ecuga | No real substitute |
| 3 | Fernet / deep bitter | Fernet Branca | ecuga | Classic after-smoke bitter |
| 4 | Hungarian bitter | Unicum Zwack | ecuga | National icon |
| 5 | HR pelinkovac | Aura Pelinkovac Gorki | ecuga | Local wormwood |
| 6 | Monastic green | Chartreuse Verte | allez | High ABV herbal |
| 7 | Monastic yellow | Chartreuse Jaune | allez / ecuga | Softer than Verte |
| 8 | French herbal sweet | Dom Benedictine | allez / ecuga | Honey-spice digestif |
| 9 | Italian saffron herbal | Strega Liquore | allez / ecuga | Distinct yellow herbal |
| 10 | Amaro (alpine/grappa) | Nonino Amaro Quintessentia | allez | Bridges amaro ↔ grappa |
| 11 | Amaro (Sicily) | Averna | ecuga | Approachable digestif |
| 12 | Italian yellow herbal | Galliano L'Autentico | allez / ecuga | Sweeter; still neat-capable |

### Explicitly **not** in pilot shortlist

| Item | Reason |
|------|--------|
| Vermouth / Cocchi / Belsazar / Angostura | User brief: spirits neat only |
| Cream / punch / seasonal gin liqueurs | Cocktail dessert aisle |
| Grand Marnier / Drambuie / Disaronno | Already brandy/whisky-adjacent or mass dessert; Grand Marnier already in `brandies.json` as `liqueur` |
| Pisco / Absinthe / Sake | Unique, but different problem (eau-de-vie / ritual); optional phase 2 |
| Pastis | Aperitif-with-water more than cigar buffet staple; Club facts already cover |
| Cynar / Luxardo Bitter Bianco | Low ABV / aperitivo-first |
| Tatratea line | Keep as optional “world tea-herbal” if category expands |
| Genever | Already near gin (`genever` style in gin buckets) |

## Preliminary grouping (for later `style` values)

Suggested style ids if a category is added:

1. `herbal-bitter-central` — Becherovka, Unicum, (Jägermeister if added later)  
2. `herbal-bitter-italian` — Fernet, Averna, Nonino Amaro  
3. `herbal-monastic` — Chartreuse, Benedictine  
4. `herbal-saffron-yellow` — Strega, Galliano  
5. `pelinkovac` — Aura / Badel-class HR  
6. `specialty-botanical` — Agwa (and later Tatratea, alpine one-offs)

Five buffet segments could collapse to: Central bitter · Italian amaro/fernet · Monastic · Yellow herbal · Local / unique (pelinkovac + Agwa).

## Buffet intuition

A private buffet of **five** bottles that cover the spectrum without duplicating rum/whisky/cognac:

1. Becherovka (entry Central bitter)  
2. Fernet Branca or Averna (Italian bitter spectrum)  
3. Chartreuse Jaune or Benedictine (French monastic)  
4. Strega (Italian yellow herbal)  
5. Aura Pelinkovac **or** Agwa (local **or** one-of-a-kind)

That set is ~80–120 € at Ecuga/AlleZ list prices and has no real overlap with existing app categories.

## Evidence files

- [`01_work/output/digestif_allez_raw.json`](digestif_allez_raw.json) — raw AlleZ scrape  
- [`01_work/output/digestif_allez_classified.txt`](digestif_allez_classified.txt) — KEEP / SKIP tagging  
- [`01_work/output/DRINKS-WS-DRINKOLOGY-AUDIT.md`](DRINKS-WS-DRINKOLOGY-AUDIT.md) — Wine-Searcher + Drinkology (all drink categories)  
- Design follow-up: [`docs/superpowers/specs/2026-07-27-digestifs-regional-liqueurs-design.md`](../../docs/superpowers/specs/2026-07-27-digestifs-regional-liqueurs-design.md)
