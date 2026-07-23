# Agent prompts — Streams H + I (after Oliva Stream J sample)

Date: 2026-07-23  
Depends on: `origin/master` (#51) + Stream J Oliva decisions in
`app/scripts/data/line_merge_decisions.json` (already consumed by
`normalize-vitolas.py`).

Worklist: `app/scripts/output/vitola_dedup_audit.json`  
- `shared_region_urls` → Stream H (~99 after Monticello Double absorb)  
- wrong search fallbacks → Stream I (start with Oliva Serie V / Melanio)

Do **not** invent product URLs. If a shop only has a category/listing page,
mark the link as line-level (not per-vitola) rather than guessing a SKU page.

After raw-catalog edits, re-run:
```powershell
cd app
python scripts/build-market-cigars.py --phase all
# ends with normalize-vitolas.py
python scripts/normalize-vitolas.py --check
```

---

## Stream H — per-product URL correctness

### H1 · Holt's (shared listing URLs)

You are fixing false per-vitola buy links. Work ONLY Holt's URLs in
`vitola_dedup_audit.json → shared_region_urls` (host contains `holts.com`).

For each reused URL:
1. Open the page. Decide: category/listing vs real product SKU page.
2. If listing: every vitola currently pointing at it is wrong as a
   “this size” link. Prefer a real per-size product URL when Holt's has one;
   otherwise keep the listing URL only at **line** level (cigar.regionLinks)
   and clear it from individual vitola.regionLinks / vitola.url.
3. Oliva Monticello is the reference case: one listing page covers Robusto,
   Toro, Churchill, Torpedo, Double Toro — not five product pages.
4. Edit the engine’s pinned raw/unified catalog input (not hand-edit
   `cigars.json` as the long-term source of truth). Re-run the pipeline.
5. Commit only catalog URL fixes + a short note in the PR of how many
   Holt's shared URLs were resolved vs left as line-level.

### H2 · CigarWorld

Same as H1, but only `cigarworld.de` URLs in `shared_region_urls`.
Prefer `/en/` product pages when available. Never invent SKUs.

### H3 · humidor.hr + havana-cigar-shop.com

Same as H1 for HR shops. Locale twins are already collapsed by normalize;
focus on URLs shared across **different cigars/lines**, not en/hr twins.

---

## Stream I — wrong search-fallback matches

### I1 · Oliva first (Serie V Melanio → Serie O)

Known bug: `cig-oliva-serie-v` (Serie V / Melanio) and/or
`cig-oliva-oliva-serie-v` (Serie V) still carry
`priceUrl` → `humidor.hr/.../oliva-serie-o-robusto-5-x-50/` (Serie **O**).

Tasks:
1. Confirm each Melanio / Serie V vitola’s correct product URL on
   humidor.hr, Havana, CigarWorld, Holt's (where stocked).
2. Write correct per-vitola URLs into the raw catalog; clear wrong Serie O
   fallbacks.
3. If no product page exists for a size, leave URL null (honest search
   fallback) and note it in the PR.
4. Re-run pipeline + `--check`. Spot-check in the app: Melanio Robusto must
   not open Serie O.

### I2 · Brand range A–F / G–M / N–Z

Scan lines whose only buy path is shop search (`?s=` or equivalent) and
spot-check the top result vs brand+line. Fix mis-hits the same way as I1.
Split by brand range so agents do not collide.

---

## Stream J — remaining brands (after Oliva sample)

Oliva is done. Continue `duplicate_line_suspects` by brand range.
Append to `line_merge_decisions.json` (do not remove Oliva entries).
Rules from the Oliva sample:
- Prefix overlap ≠ same line (Serie V ≠ Melanio).
- A “Double / Triple / …” suffix may be a **size** of the parent line
  (Monticello Double → Double Toro) OR a real sibling — verify on the shop.
- `Flor de *` style families are usually keep-distinct.

Then: `python scripts/normalize-vitolas.py` and `--check`.
