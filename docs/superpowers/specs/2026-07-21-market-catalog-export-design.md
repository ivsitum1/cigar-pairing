# Market catalog export (hybrid)

**Datum:** 2026-07-21  
**Status:** approved by continuation (“Da”)  
**Cilj:** jedan JSON koji spaja pairing podatke iz `cigars.json` s shop ponudama iz raw scrape-a, i označi / spoji duplikate među izvorima.

## Pristup

**Hibrid:**
- `catalog[]` — mapirano na naše cigare/vitole
- `unmappedShopItems[]` — shop artikli koji se nisu poklopili (već skupljeni po `dedupeKey`)
- `unmappedCrossShopDuplicates[]` — unmapped grupe s ponudama iz ≥2 shopa

## Matching / dedupe (postojeći procesi projekta)

Jedan shared modul: `app/scripts/cigar_shop_match.py` (izvučen iz `sync-hr-shops.py` + `dedupe-data.py`):

1. `norm_product_url` — URL match (uključujući `/hr/` ↔ `/en/`)
2. `BRAND_ALIASES` + `detect_brand` — isti proizvod pod dva naziva brenda
3. `LINE_RULES` + fuzzy `find_existing_cigar` — linija
4. `vitola_from_product` + ring ±8mm (`enrich-cigars`) + `uniqueVitolas` / `vitola_name_key`
5. `merge_duplicate_cigar_lines` — spoji `brand|line` duplikate (npr. Montecristo No.4)
6. `shop_dedupe_key` — kao `merge_shop_rows` za unmapped cross-shop

## Duplikati

- Catalog vitola: `isDuplicateAcrossSources` kad `offers` dolaze iz ≥2 `sourceShopId`
- Unmapped: jedna stavka po `brand|vitola|line`, s `offers[]` iz svih shopova

## Output

`app/scripts/output/cigar_market_catalog.json` (gitignored).

```bash
python3 app/scripts/dedupe-data.py
python3 app/scripts/build-market-catalog.py
```
