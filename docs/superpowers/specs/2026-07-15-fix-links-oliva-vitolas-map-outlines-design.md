## Context

The app is a Vite + React + TypeScript PWA. Prices are stored in JSON (`app/src/data/*.json`) and rendered in list views (`CatalogPage.tsx`) and detail sheets (`DetailSheet.tsx`). Cigar per-vitola pricing is sourced from Croatian shops (Humidor/Havana); drink prices are curated (Excel → JSON) and sometimes accompanied by shop URLs.

This change set targets three user-visible issues:

- Rum catalog “sort by price”: users report that the top few rums show a price that does not match the opened “buy” link.
- Cigars: `Oliva` → `Additional Vitolas` currently includes a `Paperboy` product URL and price, which makes the entire Oliva “Additional Vitolas” entry look incorrectly cheap and links to the wrong product.
- Club map: flags render correctly; user wants coastline/landmass outlines in the SVG map as additional context.

## Goals (verifiable)

- **Drinks**: When a drink displays a price and offers a “Buy” link, the link should not systematically point to a different shop/product than the stated price source; if a consistent link cannot be guaranteed, fall back to a clearly “search online” behaviour (not a misleading direct shop link).
- **Cigars**: `cig-oliva-oliva-extra` must no longer contain the `paperboy-petite-corona...` URL as a vitola nor as `priceUrl`, and its `priceEUR` must reflect the cheapest remaining Oliva vitola in that entry.
- **Map**: Club map SVG should show landmass outlines behind the graticule/markers in both “world” and “carib” views, without adding heavy dependencies.

## Non-goals

- Live price scraping or price freshness guarantees for drink shops.
- A full GIS-accurate world coastline dataset or interactive map controls.
- Adding new cigar brands/lines beyond fixing the incorrect Oliva/Paperboy attribution (possible future enhancement).

## Options

### Option A — Data-only fixes

- Manually edit `rums.json` URLs and `cigars.json` Oliva vitolas.
- Pros: fastest UI-impact.
- Cons: hard to do correctly for rums without the source Excel/catalog; fragile (regeneration may reintroduce).

### Option B — Runtime safeguards (recommended) + minimal data correction

- **Drinks**: compute a “safe buy URL” at runtime:
  - If `priceUrl` exists but `shopHR` suggests a different source (e.g. `Lidl`, `Vivat`, `Vrutak`), do not show a direct shop link; use a search query that includes the shop hint.
  - If `priceUrl` exists and `shopHR` matches the domain, keep it.
- **Cigars**: correct the specific corrupted entry in `cigars.json` (remove Paperboy vitola + recompute `priceEUR`/`priceUrl` from remaining priced vitolas).
- Pros: fixes the reported mismatch deterministically without needing Excel; prevents future misleading links even if fuzzy URL matching is imperfect.
- Cons: some drinks will show “search” rather than a direct link (but this is preferable to a wrong direct link).

### Option C — Improve pipeline matching and regenerate

- Adjust `scripts/excel-to-json.py` fuzzy URL matching (tokenization + numeric handling) and regenerate `rums.json`.
- Pros: links become more accurate.
- Cons: requires `Rum_Kolekcija_Checklist.xlsx` in the environment; not guaranteed available in CI/agent runs.

## Design (selected: Option B)

### 1) Drink “buy link” semantics

- Introduce a helper that chooses the “buy href” based on `drink.priceUrl` **and** `drink.shopHR`.
- Rule:
  - If `drink.priceUrl` is missing → Google search: `"${drink.name}" cijena kupnja ${drink.shopHR}` (shopHR appended only when meaningful).
  - If `drink.priceUrl` exists:
    - Keep direct link only if `drink.shopHR` indicates that same shop/domain (e.g. contains `allez` for an `allez.hr` URL; contains `ecuga` for an `ecuga.com` URL).
    - Otherwise fall back to search (to avoid price/link mismatch).
- UI label:
  - Direct link → current “Buy”.
  - Fallback → current “Search online”.

This keeps behaviour consistent with the editorial stance: no invented precision, and avoid misleading “direct” links when the price source is elsewhere.

### 2) Oliva “Additional Vitolas” data correction

- Edit `app/src/data/cigars.json` entry with id `cig-oliva-oliva-extra`:
  - Remove the `Connecticut Petit Corona` vitola pointing at `paperboy-petite-corona...`.
  - Recompute:
    - `priceEUR` = min priced vitola among remaining vitolas (expected: `Serie G Robusto` at `8.3`).
    - `priceUrl` = URL of that cheapest priced remaining vitola.
  - Preserve other vitolas (Nub/Serie V/Melanio etc.) as-is unless they are clearly wrong.

### 3) Map landmass outlines

- Add lightweight outline paths (very low-resolution) rendered behind markers in `ClubPage.tsx`.
- Store outlines as a small array of lon/lat polylines and project them using the existing `X()` / `Y()` functions, producing SVG `path` data.
- Styling: stroke-only (`text-dim/35`), no fill, thin stroke width so it doesn’t overpower flags/markers.

## Verification

- Add a small automated check (unit test) for the corrected Oliva record to ensure `priceUrl` does not include `paperboy` and that no vitola URL contains `paperboy`.
- Locally (non-visual):
  - Assert `getBuyHref(drink)` returns search when `shopHR` and `priceUrl` do not align.
- Locally (manual):
  - Open Club map and confirm outlines appear in both views and do not interfere with clicking markers.

