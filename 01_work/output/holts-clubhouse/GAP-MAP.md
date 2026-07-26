# Holts Clubhouse → app gap map

**Scraped:** 2026-07-26 · 34 Clubhouse articles (`01_work/output/holts-clubhouse/`)  
**Scope:** `/clubhouse/pairings/*` and `/clubhouse/cigar-101/*` only (no Magento catalog).

## Already covered in Club (facts / 101)

- Relative humidity ~65–72%, over/under humidification, seasoning
- Tunneling / canoeing / uneven burn / hard draw
- Wrapper effect on taste (general)
- Cognac / whisky / rum / port as pairing categories (rule engine + some facts)

## Gaps filled this pass (Club facts)

- Boveda named explicitly for new-humidor seasoning
- RH pack levels 62 / 65 / 69 / 72 and typical use
- Wine cork horizontal vs spirits upright
- Highball serve meaning (and that it is not for every drink)
- Tunneling wording: “redovito povlačenje” (aligned with Holts 30–60 s)
- Quiz: Traži online meta → Boveda 72% seasoning

## Pairing editorial (validation only — no score boost)

| Holts pair | Engine expectation |
|---|---|
| Courvoisier XO + Oliva Serie V Melanio (full Habano) | score > mild Connecticut |
| Martell Cordon Bleu + Rocky Patel Vintage 1990 (Broadleaf, medium-full) | score > ultra-mild body-1 |
| Dark rum (Zacapa / Brugal style) + Maduro | score > Connecticut mild |
| Cognac XO + Opus X / full Dominican | body/wrapper affinity, not mistaking for agricole |

## Not ingested as app product data

- Pumpkin beer / cider / Mardi Gras cocktail listicles (out of catalog)
- $100 cigar shopping guides, photography tips
- Product SKU pages under holts.com shop

## Script

`app/scripts/scrape-holts-clubhouse.py` — re-run to refresh corpus.
