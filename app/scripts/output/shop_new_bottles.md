# Nove boce u trgovinama

Scan: `2026-09-30T18:31:29Z` · trgovine: `ecuga`

- listinga: **2** (preskočeno 0 — minijature, setovi)
- **1** boca kojih nemamo (tier D)
- **0** mogućih novih izdanja postojećih (tier C, slabo poklapanje)
- tier A/B (već imamo; link/cijena se osvježava): 1 / 0

## Boce kojih nemamo

### Rum (1)

| Boca | Trgovina · cijena |
|---|---|
| Zzyzx Imaginary Cask Rum 2031 | [ecuga.com](https://ecuga.com/proizvod/zzyzx-2031) 61,90 € |

## Kako dodati

Lokalno, u `app/`: `python scripts/ingest-staged-drink-shops.py --apply` (tier D → stubovi, obogaćuje `enrich-shop-ingest-stubs.py`), pa `python scripts/audit_drink_shops_preship.py --check`. Nijedan drink id se ne briše bez aliasa.
