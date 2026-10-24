# Data layer v1

Generated catalog model (`product` / `vitola` / `shop` / `offer`). **Not wired into the UI yet** — the app still reads the legacy JSON via `src/data/index.ts`.

## Entities

| File | Role |
|------|------|
| `products.json` | Cigars + drinks. Stable `id` (same as legacy). Price/link live only on offers. |
| `vitolas.json` | Cigar formats only. `id` = `<productId>@<slug>` (same slug as `lib/cigarItemId`). |
| `shops.json` | Union of cigar `shops.ts` + drink `drinkShops.ts` (REF / wine-searcher excluded). Region ∈ {HR, EU, USA}. |
| `offers.json` | One row per distinct `(shopId, productId, vitolaId, url)`. Walk-in shops never carry a product `url`. |

## Regeneration

From `app/`:

```bash
python scripts/migrate_v1.py
```

Idempotent: second run must be byte-identical. Alias files (`cigarIdAliases.json`, `drinkIdAliases.json`, `drinkIdRegistry.json`) are left untouched.

## Freshness

Missing legacy `fetchedAt` → `fetchedAt: null` and `validUntil` = migration date (treat as expired / needs recheck).

## Aficionado

Shop `aficionado-zg`: `type: walkIn`, `source: manual`, `adapter: aficionado`. Manual CSV / web mode comes in a later phase.
