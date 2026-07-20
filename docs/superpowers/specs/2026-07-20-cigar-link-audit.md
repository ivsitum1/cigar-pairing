# Cigar link audit (2026-07-20)

Full-catalog check of `priceUrl` and vitola `url` after Additional Vitolas remaps + search-URL cleanup.

## Summary (after fix)

- Cigar entries: **543**
- Product URLs remaining: **1281**
- Entries without `priceUrl`: **129**
- Flagged URL rows: **11**

### Flags

- `brand_or_category_page`: **11**

## Actions taken

1. Cleared **522** Humidor search-only URLs (`?s=` / `post_type=product`) on entry + vitola fields.
2. Resynced **13** entry `priceUrl` values from remaining product vitola URLs.
3. Cleared dead product URL `liga-privada-no-9-tin-10` (HTTP 404; price kept).
4. Left **brand/category** Havana Shop pages as soft fallbacks on entry `priceUrl` only.

## HTTP note

A bulk HEAD/GET sweep of ~587 product URLs mostly returned **429** (rate limit) from humidor.hr.
Spot-check with browser UA confirmed real product pages (e.g. Liga Privada No.9 Toro = 200)
and the tin SKU as a true 404. Do not treat bulk 429 as dead links.

## Remaining soft fallbacks (brand pages)

| Brand | Line | URL |
|-------|------|-----|
| Cumpay | Cumpay | `https://havana-cigar-shop.com/en/product-brand/cumpay/` |
| E.P. Carrillo | Pledge / Encore | `https://havana-cigar-shop.com/en/product-brand/e-p-carrillo/` |
| Flor de Selva | Clásica | `https://havana-cigar-shop.com/en/product-brand/flor-de-selva/` |
| H. Upmann | Magnum | `https://havana-cigar-shop.com/en/product-brand/h-upmann/` |
| Hoyo de Monterrey | Petit Robustos | `https://havana-cigar-shop.com/en/product-brand/hoyo-de-monterrey/` |
| José L. Piedra | Petit Caballeros | `https://havana-cigar-shop.com/en/product-brand/jose-piedra/` |
| Nub | Maduro 460 | `https://havana-cigar-shop.com/en/product-brand/nub/` |
| Oscar Valladares | 2012 / The Oscar | `https://havana-cigar-shop.com/en/product-brand/oscar-valladares/` |
| Quai d'Orsay | No.50 / No.54 | `https://havana-cigar-shop.com/en/product-brand/quai-dorsai/` |
| Ramón Allones | Specially Selected | `https://havana-cigar-shop.com/en/product-brand/ramon-allones/` |
| Villa Zamorano | Reserva | `https://havana-cigar-shop.com/en/product-brand/villa-zamorano/` |

## Policy going forward

- Prefer `/proizvod/` product pages only.
- Never store Humidor search URLs.
- Brand pages allowed only as entry-level last resort.
- Vitest guard: no `?s=` / `post_type=product` in `cigars.json`.
