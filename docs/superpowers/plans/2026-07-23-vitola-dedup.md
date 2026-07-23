# Plan: iron out duplicate / wrong vitolas (multi-agent)

Date: 2026-07-23
Trigger: La Galera Connecticut shows `No.4` **and** `Connecticut No.4`, `Pegador`
**and** `Connecticut Pegador`, `Churchill` **and** `Churchill Tabaquero
Presidente`, plus `Half Corona` and `Corona` with **identical** dimensions
(46×89mm). Samplers show both `Robusto` and `Robusto Sampler` (and `Toro` /
`Toro Sampler`) — a needless split pointing at the same SKU.

## Root cause (verified in data)

These are **not** distinct vitolas. They are the **same shop product ingested
twice** — once from the `/en/` page and once from the `/hr/` page of
humidor.hr — with the vitola name parsed differently each time:

| vitola A (en) | vitola B (hr) | product URL (after locale strip) |
|---|---|---|
| `No.4` | `Connecticut No.4` | `…/proizvod/la-galera-connecticut-bonchero-no-4-…` |
| `Pegador` | `Connecticut Pegador` | `…/proizvod/la-galera-connecticut-pegador` |
| `Churchill Tabaquero Presidente` | `Churchill` | `…/proizvod/la-galera-connecticut-churchill-tabaquero-…` |
| `Half Corona` | `Corona` | `…/proizvod/la-galera-connecticut-half-corona-3-…` |

The `Corona` row is not a real Corona — it is the hr twin of **Half Corona**,
which is why the dimensions are identical. There is no separate Corona SKU.

Why dedup misses them: the engine keys a vitola on `(vitola_name, ring, lmm)`
(`build-market-cigars.py:407`). The en/hr titles yield different
`vitola_name`, so the twins get different keys and both survive. The app-side
`uniqueVitolas` also dedups by **name**, so it can't catch them either.

These duplicate entries live in the **base catalog** (`catalogSource != "market"`)
as well as in engine output, so the fix must run over the **whole** `cigars.json`
(base + market), idempotently.

## Scope (measured on cigars.json, 3105 cigars / 5680 vitolas)

- **Locale-twin extra vitolas: 78 across 60 cigars.** Deterministic to detect
  (URL identical after locale strip). Highest-leverage, zero-network fix.
- **Name-prefix dupes at identical dims+price: 74.** e.g. `Gran Robusto` vs
  `Robusto`. Some are real different sizes, some are twins — need adjudication.
- **Sampler self-splits: 3** (La Galera Robusto Sampler, La Galera Toro
  Sampler, Oliva Robusto Sampler).

## Guiding rules (all streams)

1. **Deterministic + idempotent.** Same input → byte-identical output. The
   normalize pass must be safe to re-run after every engine build.
2. **Never invent data.** Merging keeps real values; ambiguous cases are
   *flagged*, not auto-merged.
3. **Own distinct files.** Each stream writes its own data/decision file so
   agents run in parallel without collisions. Stream A consumes the others'
   outputs when present, and works standalone without them.
4. **Regression-guarded.** Integrity tests must fail if a locale-twin or
   sampler self-split reappears.

---

## Stream A — Deterministic vitola dedup pass  ·  no network  ·  owner: core agent (Claude)

Build `app/scripts/normalize-vitolas.py`, idempotent, run after the engine
(`build-market-cigars.py --phase all && normalize-vitolas.py`). It rewrites
`cigars.json` in place and emits `app/scripts/output/vitola_dedup_audit.json`.

Responsibilities (only the deterministic, no-data-needed parts):

1. **Locale-twin collapse.** Group a cigar's vitolas by locale-normalized
   product URL: strip `/(hr|en)/proizvod/` → `/proizvod/`, `cigarworld.de/(en|de)/`
   → `cigarworld.de/`, trailing slash. Vitolas sharing a normalized URL are one
   vitola → merge: union `regionLinks`, prefer a real (non-`—`) `format`, keep
   `burnTime`-derived `smokeTimeMin`, prefer the HR product URL/price.
2. **Canonical name choice** for a merged group: pick the candidate name with
   the most token overlap with the product **slug tail** (slug minus brand+line
   tokens); tiebreak = shorter name. (Verified: yields `Half Corona`,
   `Churchill Tabaquero Presidente`, `No.4`, `Pegador`.) If Stream B's
   `vitola_lexicon` provides a canonical for the slug, that wins.
3. **Sampler self-vitola collapse.** For a line whose name/vitola contains
   `Sampler`/`Gift`, collapse to a single representative vitola (drop the row
   whose name just repeats the line, e.g. `Robusto Sampler`). Contents already
   live in `lineup`.
4. **Consume adjudications** (when present): apply Stream C
   `vitola_dedup_decisions.json` (merge/keep) and Stream D
   `dimension_fixes.json` (corrected ring×length).
5. **Audit + flag.** Write every merge and every *unresolved* prefix-dup
   suspect to the audit file for Streams C/D to pick up.

Deliverable: script + wiring + `vitola_dedup_audit.json`. Fixes the 78 twins
and 3 samplers immediately, no external input.

## Stream B — Vitola name lexicon / canonicalization  ·  data  ·  split by brand range

Curate `app/scripts/data/vitola_lexicon.json` additions: slug-token → canonical
vitola display name, and a locale-title alias list, so names come out
consistent across en/hr and across brands. Feeds Stream A step 2. Divide by
brand range (A–F / G–M / N–Z). Output: lexicon entries only — no code.

## Stream C — Prefix-dup adjudication  ·  data + light network  ·  split by brand range

Work the 74 `same-dims+price, name is prefix/superset` pairs from the audit.
For each, decide **merge** (twin) or **keep-both** (genuinely different size —
verify against the shop page). Emit `app/scripts/data/vitola_dedup_decisions.json`:
`{ "<cigarId>": { "merge": [["Gran Robusto","Robusto"]], "keep": [...] } }`.
Split by brand range. Consumed by Stream A step 4.

## Stream D — Wrong / missing dimensions  ·  network scrape  ·  split by brand range

Re-validate vitolas with `format:"—"` (e.g. La Galera `Connecticut Chaveta`) or
dimensions that look copied/implausible. Pull correct ring×length from the shop
product page. Emit `app/scripts/data/dimension_fixes.json`:
`{ "<cigarId>::<vitolaName>": { "ring": 50, "lmm": 130 } }`. Consumed by Stream
A step 4. This is the only stream that needs live network (Cursor/local agent).

## Stream E — App-side safety net + display  ·  frontend  ·  one agent

- Harden `app/src/lib/cigarVitola.ts::uniqueVitolas` to also dedup by
  locale-normalized URL and by `(ring,lmm,price)` as a runtime guard.
- Ensure sampler cards never render a self-repeating vitola row.
- No data edits; pure defensive UI so a stray twin never reaches the screen.

## Stream F — Regression guard  ·  tests  ·  fold into E or standalone

Add to `app/src/data/integrity.test.ts`:
- No cigar has two vitolas with the same locale-normalized product URL.
- A `Sampler`/`Gift` line has exactly one vitola.
- No two vitolas share `(format, priceEUR)` **and** a prefix/superset name
  unless whitelisted in `vitola_dedup_decisions.json` `keep`.

---

## Sequencing

1. **A ships first** (locale-twin + sampler) — fixes the screenshot cases with
   zero external input; add F guards in the same PR.
2. **B, C, D run in parallel** (independent files). As each lands, re-run A to
   fold results in — output stays deterministic.
3. **E** any time (independent, defensive).

## Interfaces (collision-free file ownership)

| File | Writer | Reader |
|---|---|---|
| `app/scripts/normalize-vitolas.py` | A | pipeline |
| `app/scripts/output/vitola_dedup_audit.json` | A | C, D |
| `app/scripts/data/vitola_lexicon.json` | B | A |
| `app/scripts/data/vitola_dedup_decisions.json` | C | A, F |
| `app/scripts/data/dimension_fixes.json` | D | A |
| `app/src/lib/cigarVitola.ts`, `integrity.test.ts` | E/F | app |

---

## Ready-to-paste agent prompts

### Stream B (Cursor / data agent — brand range __A–F__ / __G–M__ / __N–Z__)
> Repo cigar-pairing. Goal: make vitola display names consistent so en/hr
> scrapes of the same product resolve to ONE name. For brands in range {RANGE},
> read `app/src/data/cigars.json` and, for each vitola, propose a canonical
> display name keyed by the product-URL slug tail. Add entries to
> `app/scripts/data/vitola_lexicon.json` (slug-token → canonical name, plus
> locale-title aliases). Do NOT edit cigars.json or any code. Keep names as the
> shop lists them (e.g. `Half Corona`, `Churchill Tabaquero Presidente`, `No.4`,
> `Pegador`). Commit only the lexicon file. Note any brand where you're unsure.

### Stream C (data + light network — brand range __A–F__ / __G–M__ / __N–Z__)
> Repo cigar-pairing. Open `app/scripts/output/vitola_dedup_audit.json` (section
> `prefix_suspects`). For brands in range {RANGE}, decide for each flagged pair
> whether the two vitolas are the SAME SKU (merge) or genuinely different sizes
> (keep) — verify against the shop product page when unsure. Write decisions to
> `app/scripts/data/vitola_dedup_decisions.json` as
> `{ "<cigarId>": { "merge": [["Gran Robusto","Robusto"]], "keep": [["A","B"]] } }`.
> Do NOT edit cigars.json or code. Commit only the decisions file.

### Stream D (network scrape — brand range __A–F__ / __G–M__ / __N–Z__)
> Repo cigar-pairing. In `cigars.json`, find vitolas with `format:"—"` or
> dimensions that look copied/implausible, for brands in range {RANGE}. Look up
> the real ring gauge × length (mm) on the shop product page (URL is on the
> vitola / regionLinks). Write `app/scripts/data/dimension_fixes.json`:
> `{ "<cigarId>::<vitolaName>": { "ring": 50, "lmm": 130 } }`. Never guess — skip
> what you can't verify and list it. Commit only the fixes file.

### Stream E (frontend safety net)
> Repo cigar-pairing. Harden `app/src/lib/cigarVitola.ts::uniqueVitolas` to dedup
> vitolas by locale-normalized product URL and by `(ring,lmm,priceEUR)`, and make
> sampler/gift cards never render a vitola row that just repeats the line name.
> Add integrity tests (Stream F). No data edits. `tsc`, `vitest`, `build` green.
