# Market catalog export (hybrid)

**Datum:** 2026-07-21  
**Status:** approved by continuation (“Da”)  
**Cilj:** jedan JSON koji spaja pairing podatke iz `cigars.json` s shop ponudama iz raw scrape-a, i označi duplikate među izvorima.

## Pristup

**Hibrid:**
- `catalog[]` — strogo mapirano na naše cigare/vitole (URL match)
- `unmappedShopItems[]` — shop artikli koji se nisu poklopili s katalogom

## Duplikati

- `isDuplicateAcrossSources = true` kad ista catalog vitola ima `offers` iz ≥2 različita `sourceShopId`
- Unmapped: `heuristicDuplicate` nije u v1 (samo točni URL match u catalogu)

## Output

`app/scripts/output/cigar_market_catalog.json` (gitignored pattern već pokriva `cigar_shop_*_raw.json`; dodati i ovaj artefakt u ignore).
