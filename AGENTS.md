# AGENTS.md

## Cursor Cloud specific instructions

The shipped product is a **Vite + React + TypeScript + Tailwind PWA** for cigar/drink pairing, living entirely in `app/`. All user data (collection, ratings, pairing diary) is stored in the browser's `localStorage`, per device — there is no server-side account or database.

Two things sit outside `app/` and are **not** part of the deployed site:

- `backend/` — an **optional local FastAPI service** (`uvicorn app.main:app`, port 8787) for stronger receipt OCR (PaddleOCR) and cigar-band image matching. The PWA only calls it when `VITE_OCR_API_URL` is set; unset (the GitHub Pages default) the app uses the embedded `@paddleocr/paddleocr-js` and `tesseract.js` instead. Never required to lint, test, build, or run the app.
- `app/scripts/` — an **optional local data-regeneration pipeline** (scrape → Excel → JSON). Requires local Excel files that are git-ignored. The `--check` variants of these scripts *are* CI gates (see below) and are read-only.

Note that first OCR use fetches model assets from third-party CDNs (jsDelivr / HuggingFace / ModelScope) — the app is offline-first for its own data, but not for OCR models.

### Cloud Agent environment (`.cursor/environment.json`)

Repository-managed setup for Cursor Cloud Agents: `cd app && npm ci`, plus `pip install Pillow` for the product-image CI gate. A Vite dev terminal starts at `http://localhost:5173/cigar-pairing/`. Smoke path: Pairing → pick a cigar → view drink pairings → **Zabilježi večer** → confirm in Kolekcija diary.

### Commands (run inside `app/`)
Standard commands are defined in `app/package.json` and mirrored by `.github/workflows/ci.yml`:
- Typecheck (lint gate in CI): `npx tsc -b --noEmit`
- Test: `npm test` (Vitest, `vitest run`)
- Build: `npm run build` (`tsc -b && vite build`)
- Dev server: `npm run dev` (Vite, defaults to port 5173)

### CI gates (`ci.yml` runs on pushes to `master` and on PRs)
Beyond `tsc` / `npm test` / `npm run build`, Python gates guard the catalog. They are **read-only** — they never write to `scripts/output/`. Blocking:
```
python scripts/apply-taxonomy.py --check --skip-normalize
python scripts/normalize-vitolas.py --check
python scripts/apply-cigar-descriptions.py --check
python scripts/merge-leaf-details.py --check
python scripts/test_reconcile_hr.py
python scripts/test_taxonomy_lib.py
python scripts/test_merge_leaf_details.py
python scripts/test_product_image_lib.py   # traži Pillow; CI ga instalira za taj korak
```
`ci.yml` runs several more `--check` writers in the same blocking step (`derive-drink-brands`, `derive-drink-display-names`, `normalize-profile-axes`, `merge-cigarworld-aroma`, `apply-taste-reports`) plus `test_neptune_strength.py` and `test_taste_reports.py` — treat `ci.yml` as the source of truth, not this list.

**One gate is deliberately non-blocking** (`continue-on-error: true`) and fails on `master` today:
```
python scripts/taxonomy-audit.py --fail-on-new --check-only   # 925 violations
```
910 lines across 127 brands have no taxonomy entry, and 15 brands have no taxonomy file at all — a curation backlog from the import that grew the catalog from 2401 to 3701 records, worked down brand by brand. A red line here is expected; do **not** "fix" it by bulk-writing lines into `unresolved` (tried, rejected: it makes `apply-taxonomy` oscillate with period 2).

If `apply-taxonomy --check` reports `changed: true` with all `auto_pass_counts` at 0, the pending write is usually just record **order**: it sorts by a raw `.lower()` on brand+line, where accented letters sort after all of ASCII (`Clásica` belongs after `Classic Tempo`). Run the writer once (`python scripts/apply-taxonomy.py --skip-normalize`) and diff — if no record's content changed, it was only the sort.
A separate `backend` job runs `python -m unittest discover -s tests` in `backend/`.

### Price freshness (W3)
- Each price point in `cigars.json` carries an optional `fetchedAt` (ISO `YYYY-MM-DD`) set by the scraping scripts.
- **Quarterly refresh cadence (~every 3 months):** run `sync-hr-shops.py` (HR) and `enrich-region-links.py` (EU/USA) on Cursor locally. Both scripts now stamp `fetchedAt = today` automatically.
- Exchange rates (`USD_TO_EUR`, `GBP_TO_EUR`, `CHF_TO_EUR`) live in `app/scripts/shop_common.py` with a date comment. Update them together with each quarterly scrape.
- One-shot baseline stamp (offline, no network): `python scripts/stamp-fetched-at-baseline.py`. Sets `fetchedAt = 2026-07-01` on every price that lacks it. Run once after the W3 PR merges, then re-export with `export-indexes.py`.
- UI: the DetailSheet shows "Cijena preuzeta {date}." when `fetchedAt` is present; prices older than 90 days show an orange stale warning. When `fetchedAt` is absent the generic market note is shown instead.

### Stock freshness (weekly ping)
- Product-page stock (`inStock`, `stockFetchedAt`) is separate from quarterly price scrapes. It lives on the same JSON nodes as shop links (`regionLinks`, vitola `url`, drink `priceUrl`).
- **Weekly local refresh:** `python scripts/refresh-availability.py` pings known product URLs only — no catalogue recrawl. Use `--stale-days 14` to skip recently pinged links; `--hosts humidor.hr,allez.hr` for a targeted pass.
- **Windows Task Scheduler:** `powershell -File scripts/schedule-availability-refresh.ps1 -Install` registers Sunday 09:00; `-RunNow` for manual. The task does not commit — review `git diff` on catalog JSON before shipping.
- **Overlay merge:** after pulling master, re-apply saved pings with `python scripts/apply-stock-overlay.py` (`scripts/output/stock_overlay.json`).
- UI: DetailSheet buy buttons show "Na zalihi" / "Nema na zalihi" when `stockFetchedAt` is present; older than 14 days shows a stale hint. Missing fields → no stock claim.
- Distinct from **`hr-availability.yml`**: that workflow reconciles which cigars appear in HR at all (`availabilityHR` / `markets.HR`), not shelf stock on a known URL.

### Fotografije proizvoda
- **Dva popisa, i ne smiju se pomiješati.** `src/data/productImages.json` = adresa
  slike kod dućana (puni `attach-product-images.py`); `src/data/productImagesLocal.json`
  = obrađene slike u `public/img/products/` (puni `normalize-product-images.py`).
  Skripta za obradu **ne dira** prvi popis — pregazila bi ono čime app radi danas.
- `lib/productImage.ts` bira: obrađena ako postoji, inače dućanska. Zato obrada može
  stati na pola, a nijedna kartica ne ostaje bez slike.
- Lanac: `attach-product-images.py` (adrese) → `fetch-product-images.py` (preuzimanje,
  treba mrežu) → `normalize-product-images.py` (podloge, treba Pillow). Originali u
  `scripts/output/product-images/` su git-ignorirani.
- Podloga se **miče u prozirno**, ne prebojava. Fotografija bez jednolične podloge se
  ne reže nego dobiva `framed`. `ProductThumb` crta plohu iza slike samo kad ona
  **nije** `cutout`.

### Non-obvious notes
- The dev server serves the app under the base path **`/cigar-pairing/`**, not `/`. Open `http://localhost:5173/cigar-pairing/` — the bare root path will not render the app. This base is set in `app/vite.config.ts` to match the GitHub Pages repo name.
- Node 22 is expected (see CI). The package manager is **npm** (`app/package-lock.json`).
- Deploy is automatic after full CI passes on `master`: push/merge → `ci.yml` (Node + Python gates) → on success, `deploy.yml` (`workflow_run`) force-pushes `app/dist` to `gh-pages`. Manual `workflow_dispatch` on deploy is still available but skips the CI gate.
- **Never remove a drink or cigar id without an alias.** Collections and diaries live in `localStorage` and key on those ids; a removed id silently orphans the user's marks. Add the successor to `src/data/drinkIdAliases.json` / `cigarIdAliases.json`. `drinkIdRegistry.json` + `src/data/drinkIds.test.ts` enforce this.
- **A line name is brand → line → vitola; dimensions belong to the vitola.** Shop titles arrive lower-cased with the size glued on (`1502 XO Torpedo 6"1/2 * 52` → line `xo 61 2 52`). `apply-taxonomy.py`'s auto-pass undoes that: P0 re-cases the line, P1 lifts a trailing size into `vitolas[].format`, P2 moves a trailing shape word into the vitola *only* when the dimensions disprove the recorded one. P0 is slug-neutral by design — casing must never mint a new cigar id. `src/data/cigarNomenclature.test.ts` guards the corpus, `scripts/test_taxonomy_lib.py` the rules.
- **`keepSeparate` in `scripts/data/taxonomy/*.json` outranks `line_merge_decisions.json`.** A merge decision that contradicts it aborts `normalize-vitolas.py` — resolve by editing one of the two, not by suppressing the check.
- **A shop link belongs to a (vitola, region) pair, never to "the line".** `regionLinks` on the line carry ONE scraped product, and the scrape itself sometimes pins a sibling vitola's SKU (Robusto → Toro). `lib/vitolaLinkMatch.ts` decides: a slug that names a *different* vitola disqualifies the link (a slug that names no size at all does not — missing data is not proof of error). `sanitizeVitolaLinks` (`src/data/index.ts`) applies this once at import, swapping in the right `sourceUrls` product where one exists and **dropping the price with the URL** — the price belonged to the other product. What loses its link falls back to a shop search that carries the selected vitola's name.
- The OCR bundle (~10.9 MB) must stay a **lazy** chunk. Do not give it a `manualChunks` name: that dissolves the dynamic-import boundary and puts it in the entry's `modulepreload`. It is named via `output.chunkFileNames` instead, so `globIgnores` still matches.
- Since state is `localStorage`-only, a "hello world" smoke test is fully client-side: open the app → Pairing → pick a cigar → view scored drink pairings → "Zabilježi večer" to log an evening → confirm it appears under Kolekcija (Collection) diary.
