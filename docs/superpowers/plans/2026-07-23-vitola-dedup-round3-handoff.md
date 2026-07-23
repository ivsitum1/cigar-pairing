# Plan: vitola / line corpus cleanup — Round 3 handoff

Date: 2026-07-23  
Audience: second agent (Cursor / local) continuing after Streams A–G + Holts-H + serie-I + Oliva-J sample  
Corpus (working tree after Oliva J): **3104 cigars / 5581 vitolas**  
Worklist source of truth: `app/scripts/output/vitola_dedup_audit.json`  
Measured summary: `app/scripts/output/corpus-worklist-summary.json`  
J/C pattern sketch: `app/scripts/output/corpus-j-c-classify.json`

## Already shipped (do not redo)

| Stream | What | Where |
|---|---|---|
| **A** | Locale-twin + sampler collapse | `normalize-vitolas.py`; engine tail |
| **E/F** | `uniqueVitolas` URL net + integrity tests | `cigarVitola.ts`, `integrity.test.ts` |
| **G** | Semantic within-line dedup; chosen-vitola-only UI | #51 |
| **H Holts** | Demote `holts.com/.../all-cigar-brands/*.html` from vitola → line; `exact:false` | `demote_holts_listings`, `index.ts` — **`shared_region_urls` = 0** |
| **I serie scrub** | `priceUrl` whose serie letter ≠ line serie → real `/proizvod/` from own vitolas | Oliva Serie V / Melanio fixed; **serie mismatch residual = 0** |
| **J Oliva sample** | Monticello Double→Monticello; Melanio relocate; keep Serie V / Flor de / Gilberto | `line_merge_decisions.json` (may still be local WIP — confirm committed before extending) |

Residuals after that pass: **0** locale twins, **0** sampler multi-vitola, **0** shared region URLs, **2** leftover semantic name groups (`cig-la-galera-85th`, `cig-rocky-patel-rp-sixty`).

**Structural line work beyond shipping J** → [`2026-07-23-cigar-taxonomy-brand-line-vitola.md`](2026-07-23-cigar-taxonomy-brand-line-vitola.md); do not extend `line_merge_decisions.json` past the J ship gate (taxonomy owns further merges).

## Guiding rules (same as Round 1)

1. Deterministic + idempotent. Prefer decision JSON → `normalize-vitolas.py`, not hand-edits of `cigars.json`.
2. Never invent URLs, dims, or merges. Skip + list what you cannot verify.
3. Own distinct files (table below). Parallel agents must not touch the same file.
4. After decisions land: `python scripts/normalize-vitolas.py` then `--check`; `tsc` / `vitest` / `build` if you touch TS.

## File ownership

| File | Writer | Reader |
|---|---|---|
| `app/scripts/data/vitola_dedup_decisions.json` | **C** | A / F |
| `app/scripts/data/dimension_fixes.json` | **D** | A |
| `app/scripts/data/line_merge_decisions.json` | **J** (append only; keep Oliva keys) | A |
| `app/scripts/data/vitola_lexicon.json` | **B** (add `slugs` map; do not delete existing `vitolas`) | A |
| raw/unified catalog (engine input) | **H residual / I network** | engine |
| `cigars.json` | only via normalize / engine | app |

Do **not** create parallel corrected copies of `cigars.json`.

---

## Remaining work (measured)

### Stream C — prefix / name adjudication · **48** audit rows · no/light network

| Shape | N | Meaning | Default action |
|---|---:|---|---|
| `prefix-pair` | **13** | same dims+price, name prefix/superset | decide **merge** or **keep** |
| `dim-conflict-same-name` | **35** | same display name, **different** ring×length | **do not merge** — rename one (or fix dims via D) |

By brand range: A–F 19 · G–M 13 · N–Z 16.

**All 13 prefix-pairs (complete list — small enough for one agent):**

| id | a | b | note |
|---|---|---|---|
| `cig-aganorsa-aniversario` | Connecticut/Corojo/Maduro Robusto; Corojo Toro | Robusto / Toro | bare size likely twin of one wrapper SKU — verify shop |
| `cig-aganorsa-la-validacion` | * Gran Robusto (4 wrappers) | Robusto | same |
| `cig-davidoff-primeros-by-davidoff-dominican` | Dominican / Nicaragua | * Maduro | often **keep** (wrapper) |
| `cig-rocky-patel-rp-sixty` | Sixty Toro | Sixty | likely semantic twin |
| `cig-romeo-y-julieta-ryj-classic` | No. 3 / No. 2 | Cedros de Luxe No. 3 / Fabuloso No. 2 | likely **keep** (factory names) |

Emit:

```json
{
  "<cigarId>": {
    "merge": [["Connecticut Robusto", "Robusto"]],
    "keep": [["Dominican", "Dominican Maduro"]],
    "rename": [["Corona", "Corona Extra", "46 x 142mm"]]
  }
}
```

(`rename` optional if normalize does not yet consume it — if unsupported, put dim-conflict renames in a `_notes` list and extend normalize only with approval.)

### Stream D — missing dimensions · **279** vitolas / **207** cigars · network

- `format: "—"`; **268 have a product URL**, **11 do not** (skip those).
- By range: A–F 136 · G–M 45 · N–Z 98.
- Heaviest brands: Davidoff 40, Arturo Fuente 24, Plasencia 22, Montecristo 17, Oscar Valladares 16, Cohiba 15, …

Emit `dimension_fixes.json`:

```json
{ "<cigarId>::<vitolaName>": { "ring": 50, "lmm": 130, "source": "<product-url>" } }
```

Never guess. Prefer HR `/proizvod/` page dimensions when present.

### Stream J — duplicate-line adjudication · **614** pairs · judgement + light network

By range: A–F **266** · G–M **162** · N–Z **178** · other(1502) **8**.

Heuristic pre-class (not ground truth — agent must still judge):

| Pattern | ~N | Typical verdict |
|---|---:|---|
| size-as-line (`Emerald` ⊂ `Emerald Robusto 5 X 50`) | ~153 | **MERGE** size-line → parent; fold vitola |
| wrapper-variant (`…` ⊂ `… Maduro` / Connecticut) | ~97 | **KEEP DISTINCT** unless shop proves one page |
| needs-judgment (Wide, Grande, Conquistador, Sampler, …) | ~364 | open shop / brand knowledge |

Oliva sample already in `line_merge_decisions.json` — **append**, do not overwrite `_keep_distinct` / `_relocate_vitolas` / Monticello absorb.

Shape:

```json
{
  "<canonicalId>": {
    "absorb": ["<otherId>"],
    "rename_absorbed_vitolas": { "Toro": "Double Toro" },
    "reason": "…"
  },
  "_keep_distinct": [{ "ids": ["…", "…"], "reason": "…" }],
  "_relocate_vitolas": [{ "from": "…", "to": "…", "names": ["…"], "reason": "…" }]
}
```

Split agents by brand range (A–F / G–M / N–Z). Each agent commits **only** decisions for its brands into the same file via careful merge, or writes `line_merge_decisions_{range}.json` for a core agent to fold.

Top volume brands (pairs): Perdomo 29, Gurkha 14, Marca 14, Vegas 13, Cavalier 12, Casdagli / Drew Estate / Villiger 11, …

### Stream B — lexicon · optional polish

Existing `vitola_lexicon.json` is a **generic vitola synonym table** (`vitolas`), not the Stream-A slug map. Normalize reads `lexicon["slugs"]` when present.

Add without deleting `vitolas`:

```json
{
  "slugs": {
    "la-galera-connecticut-half-corona-…": "Half Corona"
  }
}
```

Priority: only brands where display names still oscillate after A/G. Not blocking C/D/J.

### Stream H residual · network (optional)

`shared_region_urls` is **0** after Holts demotion. Remaining value: find **real per-size Holts SKU URLs** where they exist (upgrade line-level listing → exact). Split by brand. Do not invent.

### Stream I residual · network (optional, large)

Serie-letter scrub done. Still **~4932** vitolas without a real product URL and **~2673** cigars with no product URL at all (search fallback). Do **not** try to fill all. Prioritize:

1. User-reported wrong search hits.
2. Lines with `strength`/price shown but wrong shop landing.
3. Brand range only when a concrete mis-hit list exists.

### Tiny leftovers (core or any agent)

- Semantic: `cig-la-galera-85th` (`Anniversary Toro` / `Toro`), `cig-rocky-patel-rp-sixty` (`Sixty Toro` / `Sixty`) — fold into C decisions or one-line normalize guard.

---

## Suggested agent split (parallel, no file clash)

| Agent | Scope | Writes |
|---|---|---|
| **C-all** | 13 prefix-pairs + flag 35 dim-conflicts | `vitola_dedup_decisions.json` |
| **D A–F** | dash dims brands A–F | `dimension_fixes_AF.json` → fold |
| **D G–M** | … | `dimension_fixes_GM.json` |
| **D N–Z** | … | `dimension_fixes_NZ.json` |
| **J A–F** | 266 line pairs | append `line_merge_decisions` (or ranged file) |
| **J G–M** | 162 | … |
| **J N–Z** | 178 + 1502 | … |
| **Core** | merge ranged files, run normalize `--check`, ship PR | code + `cigars.json` via script |

---

## Ready-to-paste prompts

### C (one agent — full list is only 13 pairs)

> Repo cigar-pairing. Open `app/scripts/output/vitola_dedup_audit.json` → `prefix_suspects`.
> 1) For every object with `a`/`b` (13 rows): decide merge vs keep. Verify on the shop URL when unsure. Write `app/scripts/data/vitola_dedup_decisions.json`.
> 2) For every object with `conflict` (same name, different format): do **not** merge. List them under `_dim_conflicts` with a proposed distinct name or “needs D”.
> Do not edit `cigars.json` or code. Commit only the decisions file.

### D (brand range __A–F__ / __G–M__ / __N–Z__)

> Repo cigar-pairing. Find vitolas with `format:"—"` in `app/src/data/cigars.json` for brands in {RANGE} (see `corpus-worklist-summary.json` stream_D). Open the vitola product URL; record ring × length mm. Write `app/scripts/data/dimension_fixes.json` entries `"<cigarId>::<vitolaName>": {"ring":N,"lmm":N,"source":"url"}`. Never guess — skip and list unverified. Do not edit cigars.json/code.

### J (brand range __A–F__ / __G–M__ / __N–Z__)

> Repo cigar-pairing. Work `vitola_dedup_audit.json` → `duplicate_line_suspects` for brands in {RANGE}.
> For each pair (`line_a`/`id_a` vs `line_b`/`id_b`):
> - MERGE when `line_b` is the same commercial line with a size stuck in the title (e.g. Emerald ⊂ Emerald Robusto 5×50) → absorb id_b into id_a (or the richer multi-vitola parent), rename vitola if needed.
> - KEEP when wrapper/series differs (Maduro, Connecticut, Melanio, Flor de *, …).
> - RELOCATE vitolas only when a SKU clearly sits on the wrong line id.
> Append to `app/scripts/data/line_merge_decisions.json` without removing existing Oliva keys. Every entry needs a one-line `reason`. No cigars.json / code edits.

### Core integrate (after C/D/J files exist)

> Merge any ranged decision/fix files into the canonical paths. Run:
> `python scripts/normalize-vitolas.py` then `python scripts/normalize-vitolas.py --check`.
> Confirm audit counters and that Oliva + Connecticut still look correct. Open PR with decisions + script output only.

---

## Verification checklist

- [x] `normalize-vitolas.py --check` clean (idempotent) — 2026-07-23 Core
- [x] La Galera Connecticut still 6 vitolas (Half Corona / No.4 distinct; no twin collapse)
- [x] locale twins / sampler multi-vitola still 0 after Core
- [x] `line_merge_decisions.json` still contains Oliva Monticello absorb + Serie V keep
- [x] No invented Holts/CigarWorld product URLs (decisions-only; normalize applied absorbs)
- [ ] vitest + build green if TS touched — not required (no TS this pass)

### Core apply note (2026-07-23)

After C + J (incl. deferred): **2758 cigars / 5537 vitolas**. Audit: `line_merges` 277, `keep_distinct` 173, `duplicate_line_suspects` ~84 residual, `prefix_suspects` 44, `shared_region_urls` 0. Deferred list cleared (0).

### Stream D note (2026-07-23)

- Fetcher: `app/scripts/fetch-dimension-fixes.py` (Havana via WC Store API `?slug=`).
- `dimension_fixes.json`: **239** fixes. After re-normalize: **28** dash left (17 with URL unverified). Do not invent.

### Residual J + tiny leftovers (2026-07-23)

- Re-applied residual 84 + prefix leftovers + La Galera 85th absorb (note `residual-J reapply` in decisions `_meta`).
- Rocky Patel Sixty: three distinct sizes kept (`Sixty Robusto` / `Sixty Toro 6 ½ x 52` / `Sixty`).
- Corpus: **2729 / 5528**. Audit: `line_merges` 280, `keep_distinct` 239, `duplicate_line_suspects` **0**, alive unhandled prefix **0**. `--check` clean.

### Stream B note (2026-07-23)

- `vitola_lexicon.json` → `slugs` (**36**); existing `vitolas` table untouched.

### H / I residual

- H: `shared_region_urls` **0**; exact Holts per-size still **0** — no invent. I: mass URL fill out of scope.

## Out of scope for this handoff

- Pairing-score / drink catalog work (`PAIRING-SCORE-AUDIT.md`)
- Filling all 2673 URL-less cigars
- Scholarly / research pipelines
