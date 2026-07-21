# Market catalog export (hybrid)

**Datum:** 2026-07-21  
**Status:** approved by continuation (“Da”)  
**Cilj:** jedan JSON koji spaja pairing podatke iz `cigars.json` s shop ponudama iz raw scrape-a, i označi duplikate među izvorima.

## Pristup

**Hibrid:**
- `catalog[]` — mapirano na naše cigare/vitole (URL match + sekundarno normalizirano ime)
- `unmappedShopItems[]` — shop artikli koji se nisu poklopili s katalogom
- `unmappedCrossShopDuplicates[]` — unmapped artikli s istim normaliziranim imenom u ≥2 shopa

## Matching

1. Točan URL (normalized host+path)
2. Normalizirano ime: `brand line vitola`, `brand vitola`, `brand line`, `vitola`

## Duplikati

- `isDuplicateAcrossSources = true` kad ista catalog vitola ima `offers` iz ≥2 različita `sourceShopId`
- Unmapped cross-shop: grupe u `unmappedCrossShopDuplicates`

## Output

`app/scripts/output/cigar_market_catalog.json` (gitignored).

## Builder

```bash
python3 app/scripts/build-market-catalog.py
```
