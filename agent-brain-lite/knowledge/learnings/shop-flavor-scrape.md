---
title: Shop flavor scrape — CigarWorld i Famous Smoke
category: learning
tags: [scraping, cigarworld, famous-smoke, flavor-enrichment, automation]
summary: Operativna pravila za HTTP/Playwright/browser scrape okusa s CigarWorlda i Famous Smokea.
updated: 2026-07-25
---

# Shop flavor scrape (CW + Famous)

## CigarWorld

- Product stranice daju **VariantInfo** (`wrapper variety`, length, ring) i aroma canvas (`data-content` 12 znamenki, `data-props` 8).
- Aroma redoslijed: Wood, Pepper, Grass, Fruit, Cream, Sweet, Nut, Chocolate, Coffee, Toast, Leather, Soil.
- HTTP urllib radi; brzi prolaz → **429** — treba `--sleep ~2`, `--resume`, backoff na 429.
- Radar **nije** tasting prose: tagovi OK, `profileEstimated` ostaje `true` dok nema shop teksta.
- Skripte: `app/scripts/scrape-cw-famous-quick.py`, `convert-cw-famous-raw.py`, `merge-flavor-enrichment.py --batch 2`.

## Famous Smoke

- Search / brand listing / urllib često **Client Challenge** (CAPTCHA).
- Cursor IDE browser session: `fetch(..., {credentials:'include'})` s brand ili product URL-a **radi** bez challengea.
- URL obrasci: `brand-{slug}`, fallback Magento `catalogsearch/result/?q=`.
- Soft 404: HTML 200 + naslov `PAGE NOT FOUND` — ne tretirati kao OK.
- Match filter: brand + ≥50% tokena linije u title/URL; odbaci krive hitove (npr. Benchmade→VSG, Project 40→1600).
- Exa search radi kad MCP nije na rate limitu; DDG HTML često blokiran.
- Pipeline: browser scrape → `famous_browser_scrape.json` → `merge-famous-browser.py` → convert → merge.
- Famous tasting prose **pobjeđuje** CW aroma-bitove u `description`; wrapper leaf s shopa pobjeđuje slabe/country placeholdere.

## Honesty

- Ne izmišljati notes; heuristika ostaje `profileEstimated: true`.
- Shop prose (Famous/CW tekst) → smije `profileEstimated: false` za ta polja.
- `wrapper_label()` mapira broadleaf→Maduro za tagove — za **prikaz** zadrži konkretan leaf (Broadleaf, Cameroon…).

## Stanje (2026-07-25)

| Izvor | Rezultat |
|-------|----------|
| CW quick (120) | ~117 OK (resume nakon 429) |
| Famous browser | 22 pouzdanih linija u korpusu |
| Vitest cigars.data | 36/36 |

## Related

- Spec: `docs/superpowers/specs/2026-07-24-flavor-enrichment-design.md`
- Plan: `docs/superpowers/plans/2026-07-24-flavor-enrichment.md`
