# Unified cigar catalog

**Datum:** 2026-07-21  
**Cilj:** jedan JSON sa **svim info vezanim uz naše cigare** — pairing iz `cigars.json` + shop cijene/linkovi/detalji (W/B/F) iz HR/EU/USA.

## Output

`app/scripts/output/cigar_unified_catalog.json`

```bash
python3 app/scripts/build-market-catalog.py
# opcionalno i unmapped shop artikle (veliki file):
python3 app/scripts/build-market-catalog.py --include-unmapped --compact
```

## Struktura

```json
{
  "generatedAt": "...",
  "schemaVersion": 1,
  "summary": { "cigars", "vitolas", "vitolasWithOffers", "vitolasWithFullWBF", "duplicateVitolas", "shops" },
  "shops": [{ "id", "name", "region", "itemCount", "withFullWBF", "scrapedAt" }],
  "cigars": [
    {
      "id", "brand", "line", "country",
      "wrapper", "binder", "filler", "origin", "details",
      "strength", "body", "flavorTags", "smokeTimeMin",
      "priceEUR", "priceUrl", "markets", "availabilityHR", "notes",
      "vitolas": [
        {
          "name", "format", "parsedSize", "smokeTimeMin", "priceEUR", "url",
          "details": { "wrapper", "binder", "filler", "ringGauge", "..." },
          "offers": [{ "sourceShopId", "region", "amount", "currency", "url", "details", "..." }],
          "pricesByRegion": { "HR": [...], "EU": [...], "USA": [...] },
          "isDuplicateAcrossSources", "duplicateSources"
        }
      ]
    }
  ]
}
```

## Matching

`cigar_shop_match.py` (isti proces kao `sync-hr-shops` / `dedupe-data`).
