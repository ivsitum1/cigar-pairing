# Enrich existing cigars: flavors (not years)

**Date:** 2026-07-24  
**Status:** batch 1–2 + CW HTTP scrape (2026-07-24/25) + Famous browser session (22 lines, 2026-07-25). Playwright CW deferred; Famous urllib blocked by CAPTCHA.  
**Approach:** A (targeted pass), refined

## Goal

Improve **flavour profiles** on existing catalogue cigars that are thin or only heuristic-estimated. Prefer shop-published descriptors (CigarWorld first; Famous Smoke via authenticated browser session; Neptune later) over inventing notes.

## Non-goals

- Adding many new SKUs / full-catalogue scrape
- Re-researching **`founded` years** — user confirms years are already good enough; leave `founded` alone unless a blank `"—"` is incidental while writing a blurb
- Fabricating tasting notes or brand histories without a cited source
- Bulk rewrite of all ~2231 `profileEstimated: true` rows in one pass

## Audit snapshot (2026-07-24)

| Item | Count |
|------|------:|
| Cigars | 2395 |
| `profileEstimated: true` | ~2231 |
| Thin notes (`notes.hr` &lt; ~40) or &lt; 2 `flavorTags` | ~56 |
| Brand placeholder blurbs (catalogue filler) | 16 (all used in catalogue) |
| Short brand blurbs | ~81 |

## Decisions

| Topic | Choice |
|-------|--------|
| Scope | **Flavors first** (tags + bilingual notes) |
| Years | **Do not** prioritise founded-year research |
| Brand stories | **Secondary / optional** this round — only if leftover capacity after flavor pass; still source-backed |
| Primary shop source | CigarWorld product pages via existing `regionLinks.EU` URLs |
| Secondary | Neptune (later), only where structured flavour fields exist and ToS allows |
| Honesty | Shop text → may clear `profileEstimated` for fields taken from shop; heuristic fill stays estimated |

## Worklist (cigars)

1. Build `app/scripts/output/flavor_enrich_worklist.json` from cigars where:
   - `len(notes.hr) < 40` OR `len(flavorTags) < 2`, **or**
   - optional stretch: `profileEstimated === true` **and** has `regionLinks.EU` CigarWorld URL (batch 2, after thin set).
2. Prefer rows that already have a CigarWorld product URL.

## Scrape / merge

### Phase 0 — probe

- Playwright + Chrome against a small sample of CigarWorld URLs (consent/age wall once, reuse storage state).
- Capture when present: wrapper, strength/body if rated, length/RG, published tasting text / flavour keywords.
- Raw: `app/scripts/output/cigarworld_flavor_raw.json`.

### Phase 1 — thin-set enrich

- Merge script maps shop fields → `wrapper`, `strength`/`body` (only if shop provides), `flavorTags` (normalised to existing tag vocabulary), `notes.{hr,en}`.
- Rules:
  - Never overwrite HR `priceEUR` / product URLs.
  - Do not invent tags not supported by shop text or existing wrapper heuristics.
  - If only wrapper is recovered → allow `profile-cigars.py`-style tag expansion but keep `profileEstimated: true`.
  - If tasting prose comes from shop → set `profileEstimated: false` (or a narrower flag if we later split “notes sourced” vs “scores sourced”).

### Phase 2 — optional brand blurbs

- Only placeholder / very short blurbs; web research with `source` URL; no fake years.
- Can be deferred without blocking flavor ship.

## Out of scope

- Cigars Daily (already removed; Famous Smoke search fallbacks)
- IP geo / affiliate
- Neptune 1–5 radar charts unless fields are explicit on page

## Success criteria

- Thin-set (~56) has usable `flavorTags` (≥2) and readable notes where a CW (or later Neptune) source existed
- No fabricated founded years
- Merge is idempotent; raw JSON kept for audit
- `npm test` still green after data merge

## Risks

- CigarWorld consent / rate limits
- Many thin rows may lack EU product URL → stay heuristic
- Shop flavour language is marketing copy — keep tone neutral when translating to HR/EN notes

## Progress (2026-07-25)

| Source | Outcome |
|--------|---------|
| CigarWorld HTTP quick scrape | ~117/120 OK (VariantInfo + aroma radar); 429 mitigated with resume/backoff |
| Famous Smoke | urllib CAPTCHA; Cursor browser session → **22** validated lines merged |
| Ops learning | `agent-brain-lite/knowledge/learnings/shop-flavor-scrape.md` |

Convert prefers Famous tasting prose over CW aroma digit strings; concrete wrapper leaf (e.g. Broadleaf) kept for display rather than family label Maduro.