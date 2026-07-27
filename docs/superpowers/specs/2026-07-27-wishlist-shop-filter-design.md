# Wishlist filter by shop (Kupovina)

**Date:** 2026-07-27  
**Status:** approved  
**Scope:** filter wishlist items on Shopping page by shop; reuse existing shop summary row

## Goal

When the user stands in a shop, they can tap that shop’s summary chip under the wishlist and see only items available there — without a second control row above the list.

## Non-goals

- No persistence of the selected shop in `localStorage`
- No change to how wishlist membership is stored (`wishlist` / `owned`)
- No regrouping of the main list by shop (category grouping stays)
- No filter on gaps / segments / buffet sections

## Current state

- `ShoppingPage` shows starred drinks + cigars grouped by category (cigars first, then drink categories).
- Below the list: share chip, total €, and (when more than one shop) non-interactive pills from `groupWishlistByShop` (`shop: N× · ~X €`).
- Shop labels are normalized by stripping a trailing parenthetical (`allez.hr (rijetko)` → `allez.hr`); empty/missing shop → `shop.otherShops` label.

## Approach

Turn the existing shop summary pills into a single-select filter. Keep them under the full (or filtered) list. Add an explicit **Sve / All** chip to clear the filter.

## Behaviour

1. Default: no shop selected (`null`) → full wishlist as today.
2. Tap a shop pill → `selectedShop = that shop`; list above shows only items whose normalized shop matches.
3. Tap the same shop again, or tap **Sve** → clear filter.
4. **Ukupno** and **Podijeli / kopiraj** use the currently visible (filtered) set.
5. Shop pills always reflect the **unfiltered** wishlist (counts and totals per shop stay stable while filtered).
6. Show the shop row whenever there is at least one wishlist item and at least one distinct shop group (including a lone “ostalo” group so the user can still focus that bucket). Prefer showing the row when `wishlistShops.length >= 1` and the wishlist is non-empty; **Sve** remains useful even with a single shop.

## Matching

Export or reuse the same normalization as `groupWishlistByShop`:

- trim
- strip `\s*\(.*\)$`
- empty → `otherLabel` (`t("shop.otherShops")`)

Cigars: `availabilityHR?.[0]`. Drinks: `shopHR`.

## UI

- Location: under wishlist list, after share/total row (same place as today’s pills).
- Controls: `Chip` (or equivalent clickable pill matching existing Chip styling) for **Sve** + one per `wishlistShops` entry; active state on selected shop (or on **Sve** when unfiltered).
- List body: same category sections; empty categories omitted; if filter yields zero items (should be rare), show a short empty line or leave the list blank with total hidden — prefer a one-line i18n empty hint only if needed after implementation.

## i18n

- `shop.filterAll`: `{ hr: "Sve", en: "All" }`
- Optional empty-filter hint only if UI needs it.

## Tests

- Unit: shop-key helper (if extracted) — normalize + other-label cases already covered by `groupWishlistByShop` tests; extend if a shared `wishlistShopKey` is extracted.
- No new E2E required for this slice.

## Files

- `app/src/pages/ShoppingPage.tsx` — state, filter, clickable chips, filtered total/share
- `app/src/lib/shoppingPicks.ts` — optional extract `wishlistShopKey(raw, otherLabel)` used by `groupWishlistByShop` and the page filter
- `app/src/i18n/index.tsx` — `shop.filterAll`
- `app/src/lib/shoppingPicks.test.ts` — only if helper is extracted
