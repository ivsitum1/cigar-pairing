# Unified cigar catalog (ALL + region filters)

**Datum:** 2026-07-21  
**Cilj:** jedan JSON sa **svim cigarama** (app katalog + svi shop artikli), s filterom `ALL | HR | EU | USA`.

## Output

`app/scripts/output/cigar_unified_catalog.json`

```bash
python3 app/scripts/build-market-catalog.py
```

## Filter

Svaka stavka u `cigars[]` ima:

```json
"regions": ["HR", "EU"],
"filters": { "ALL": true, "HR": true, "EU": true, "USA": false }
```

Korištenje:

```js
const filter = "HR"; // ili ALL | EU | USA
const rows = data.cigars.filter((c) => c.filters[filter]);
```

Brojevi po filteru: `filters.counts` / `summary.countsByFilter`.

## Struktura

| Ključ | Sadržaj |
|-------|---------|
| `filters` | ALL/HR/EU/USA + counts + howToFilter |
| `shops[]` | meta po shopu |
| `cigars[]` | **sve** jedinstvene cigare/vitole |
| `unmappedCrossShopDuplicates[]` | isti proizvod u ≥2 shopa (van kataloga) |

`cigars[].kind`:
- `catalog` / `catalog-entry` — u `cigars.json` (+ pairing)
- `shop` — samo iz shop scrape-a

Svaki unos: brand/line/vitola, details (W/B/F), offers[], pricesByRegion, shops, pairing (ako postoji).
