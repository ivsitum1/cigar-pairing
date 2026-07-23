# Plan: Brand → Line → Vitola taxonomy for the whole cigar corpus

Date: 2026-07-23
Owner of this doc: core agent (Claude). Executors: local Cursor agents, one per brand batch.
Supersedes the *structural* parts of `2026-07-23-vitola-dedup.md` (that plan stays valid
for locale-twin / link work; this one is the layer above it).

---

## 0. The goal, stated as product behaviour

Three levels, three different answers:

| User taps | App shows |
|---|---|
| **Brand** | The story behind the brand + the list of its **lines** (nothing else) |
| **Line** | What that line is + **every vitola** in that line |
| **Vitola** | Info for **that one size only** — its dimensions, price, buy link |

That is the whole spec. Everything below exists to make the data actually support it.

---

## 1. Why it is broken today (measured, not guessed)

Run on `app/src/data/cigars.json` @ 5bb58cc — **3105 records, 462 brands, 5584 vitola rows.**

**The root cause: there is no line level in the data.** A record is *supposed* to be a
line, but there are **3105 records and 3105 distinct `(brand, line)` pairs** — every
record minted its own line. 1972 of them (**63 %**) carry exactly one vitola. The
ingest created a pseudo-line per shop product, so the real lines are shattered.

Measured symptom classes:

| # | Class | Count | Example |
|---|---|---|---|
| A | Brand name truncated at the first token | **64 brands** | `Roma` (→ RoMa Craft), `Black Label` (→ Black Label Trading Co.), `Laura` (→ Laura Chavin), `Cavalier` (→ Cavalier Genève), `Marca` (→ Marca Fina), `Man O. War` vs `Man O' War` |
| B | Line name carries the dimensions | **93 lines / 15 brands** | `1502 · Aniversario 10 Toro 6 X 50` → line `Aniversario 10`, vitola `Toro`, 50×152 |
| C | Line name ends with the vitola | **58 lines / 40 brands** | `La Galera · Habano Robusto Chaveta` → line `Habano`, vitola `Chaveta` |
| D | Line is really a *vitola of a sibling line* | inside the **627** prefix-overlap pairs | `Oliva · Monticello Double` is the Double Toro of `Monticello`; `Rocky Patel · Gold Label Half` is the Half Corona of `Gold Label` |
| E | Same line spelled two ways | **9 exact** + a share of the 627 | `Master Blends 3` / `Master Blends III`, `Fifty Five` / `Fifty-Five`, `PILÓN` / `Pilon`, `Serie V` / `Serie V / Melanio` |
| F | Vitola name repeats brand/line tokens | **419 rows / 276 lines** | `Serie V Melanio Robusto` → `Robusto`; `Decade Robusto` → `Robusto` |
| G | Proprietary vitola names flattened to generic shapes | brand-wide | La Galera's real vitolas are `Chaveta`, `El Lector`, `Pilón`, `Pegador`, `Bonchero No.4`, `Cabeza de Caracol` — the data shows `Robusto`, `Toro`, `Gordo`, `Corona` |
| H | Line name == brand name | **61 lines** | legitimate for single-line brands, wrong for the rest |
| I | Truncated / mangled names | seen in A | `Craft C gnon Aquitaine Cranium` — `CroMagnon` lost characters |
| J | Samplers / gift packs modelled as lines | **15** | `La Galera · Robusto Sampler` |
| K | One product URL serving several lines | **129 URLs** | listing pages passed off as per-vitola links |
| L | Vitola without real dimensions | **280 rows** | `format: "—"` |

Worked example — **La Galera has 48 records today.** It should have roughly **6 lines**
(`1936`, `Anemoi`, `Imperial Jade`, `La Instructora`, `85th Anniversary`, plus the
wrapper lines `Connecticut` / `Habano` / `Corojo` / `Maduro`), each with its own vitolas.
Same story for `Rocky Patel` (64 records), `Oscar Valladares` (64), `Perdomo` (60).

---

## 2. Target model

**Keep the record shape. Change what a record means.** A `Cigar` record stays flat —
the engine, pairing, OCR, collection and shopping all key off it, so restructuring the
JSON into nested brands would touch 24 files for no data gain.

The change is an **invariant**, enforced by tests:

> **One record = one LINE.** `(brand, line)` is unique across the corpus.
> Every size of that line lives in `vitolas[]`. Nothing else creates a record.

Field contract after the repair:

```jsonc
{
  "id": "cig-<brandSlug>-<lineSlug>",   // derived, never hand-written
  "brand": "La Galera",                 // full brand name, canonical
  "line":  "Habano",                    // line only — no vitola, no dimensions
  "vitola": "Chaveta",                  // DEFAULT vitola for the line card
  "vitolas": [
    { "name": "Chaveta",   "shape": "Robusto", "format": "50 x 127mm", ... },
    { "name": "El Lector", "shape": "Toro",    "format": "54 x 152mm", ... }
  ],
  "lineup": [ ... ]                     // only for sampler/gift packs
}
```

Two additions to `Vitola` in `app/src/types.ts`:

- `shape?: string` — the generic family (`Robusto`, `Toro`, `Churchill`…), used for
  sorting and for the "what size is this" hint. **`name` keeps the maker's own name**
  (`Chaveta`), `shape` carries the generic one. When a maker uses the generic name,
  `name === shape`.
- `ring?: number`, `lengthMM?: number` — parsed numbers alongside the display `format`,
  so sorting and validation stop re-parsing strings.

Sort order, everywhere, deterministic:

- **brands** — locale-aware A→Z on the canonical brand name
- **lines within a brand** — A→Z, except a line equal to the brand name sorts first (it
  is the core line)
- **vitolas within a line** — by `ring` ascending, then `lengthMM` ascending, then name.
  Vitolas without dimensions sort last.

---

## 3. The execution rule that keeps agents from getting lost

This is the part that failed last time. Fix it structurally:

> **No agent ever edits `cigars.json`.**
> An agent edits exactly one file: `app/scripts/data/taxonomy/<brand-slug>.json`.
> A deterministic script folds every taxonomy file into `cigars.json`.

Consequences:
- Two agents can never conflict — one file each, no shared file, no merge hell.
- An agent's work unit is **one brand**, small enough to hold in context.
- Re-running the apply script on unchanged inputs is a **byte-identical no-op**, so the
  order agents finish in does not matter.
- A wrong brand can be re-done by rewriting one small file, without re-running anything else.
- Progress is countable: *N of 462 brand files reviewed.*

---

## 4. Phase 0 — tooling (core agent, must ship first)

Nothing else can start until these exist. All under `app/scripts/`.

### 4.1 `taxonomy-audit.py`
Reads `cigars.json`, writes `app/scripts/output/taxonomy_audit.json` **and** one
worklist stub per brand at `app/scripts/data/taxonomy/_worklist/<brand-slug>.json`.

Per brand it reports, so the agent does not have to re-derive it:
- current records: `line`, `vitola`, `vitolas[]`, `format`, `priceUrl`, `regionLinks`
- flags per record: `has_dimensions_in_line`, `ends_with_shape`, `line_eq_brand`,
  `single_vitola`, `is_sampler`, `vitola_repeats_line_tokens`, `format_missing`
- brand-level flags: `brand_truncated` (≥ 80 % of lines share a first token),
  `prefix_overlap_pairs`, `normalized_duplicate_lines`
- suggested split for classes B and C (deterministic proposal, agent confirms or overrides)

### 4.2 `apply-taxonomy.py`
Reads every `app/scripts/data/taxonomy/*.json` (sorted by filename), applies to
`cigars.json` in a fixed order, writes `app/scripts/output/taxonomy_apply_report.json`.
Supports `--check` (exit 1 if the file would change) for CI.

Pass order — must be exactly this:

1. **Brand canonicalization.** `renameBrand` maps the current brand key to the canonical
   name. Several source brands may map to one canonical name → they merge.
2. **Line remap.** For each record, look up its raw `line` in the file's `lines` map →
   `{ line, vitola?, shape?, drop? }`. When `vitola` is given, the extracted vitola name
   is applied to that record's single vitola row (error out, do not guess, if the record
   has > 1 vitola and no explicit per-vitola mapping).
3. **Record merge.** Records that now share `(brand, line)` collapse into one:
   union `vitolas[]` (by name, then by locale-normalized URL), union `markets`,
   union `regionLinks` preferring HR-exact links, keep the longest `notes.hr`/`notes.en`,
   keep `min` price, OR the boolean flags (`flavoured`, `strengthFromShop`), average
   `strength`/`body` only when they differ by ≤ 1 — otherwise keep the curated record's
   value and log the conflict.
4. **Vitola rename + shape.** Apply `vitolaRenames` and `shapes`; strip leading
   brand/line token runs (existing Stream-G logic).
5. **Dimension parse.** `format` → `ring` / `lengthMM`. Normalize `6 1⁄4 X 52` style
   fractions to millimetres. Never invent a missing dimension.
6. **Derive.** Recompute `id`, default `vitola`, record-level `format`, sort vitolas per
   §2, sort records by `(brand, line)`.
7. **Id aliases.** Append every `oldId → newId` to `app/src/data/cigarIdAliases.json`
   (append-only, never rewritten) so saved collections and deep links keep resolving.
8. **Hand off** to `normalize-vitolas.py` (locale twins, samplers) — it runs last so the
   two passes compose.

### 4.3 `taxonomy-report.py --brand "La Galera"`
Prints the resulting tree for eyeballing. This is what an agent pastes back as proof:

```
La Galera  (Dominican Republic, 1936)
├── 1936                     6 vitolas   Chaveta · El Lector · Pilón · Pegador · …
├── 85th Anniversary         7 vitolas   Half Corona · Robusto Chaveta · …
├── Anemoi                   4 vitolas   Boreas · Eurus · Zephyrus · Notus
├── Connecticut              6 vitolas   Half Corona · Chaveta · Bonchero No.4 · …
├── Imperial Jade            4 vitolas   Chiquito · Perfecto · Pirámide · Robusto
└── La Instructora           3 vitolas   Perfección · Petite · Royal
```

### 4.4 Integrity guards → `app/src/data/integrity.test.ts`
Add, and they must go red on regression:

- `(brand, line)` is unique across the corpus
- no `line` contains a dimension pattern (`\d+\s*[x×]\s*\d+`, `mm`, `"`)
- no `line` ends with a bare shape word from `vitola_lexicon.json`
- no `vitola.name` starts with a token that is also the first token of its `line`
- for any two lines of the same brand, neither normalized name is a strict prefix of the
  other **unless** the pair is whitelisted in that brand's taxonomy file under `keepSeparate`
- every brand in `cigars.json` has an entry in `brands.json`
- `cigarIdAliases.json` resolves: every alias target exists
- vitolas within a line are sorted per §2

### 4.5 Wiring
`build-market-cigars.py --phase all` → `apply-taxonomy.py` → `normalize-vitolas.py`.
Add the chain to `scripts/pipeline.py` under the `cigars` category, and to CI as
`apply-taxonomy.py --check && normalize-vitolas.py --check`.

**Deliverable of Phase 0:** the three scripts, the tests, the wiring, and 462 worklist
stubs. No data judgement yet.

---

## 5. Phase 1 — deterministic auto-pass (core agent, no judgement)

Fold into `apply-taxonomy.py` as pre-passes, applied to **all** brands before any
hand-written taxonomy file:

| Pass | Rule | Est. effect |
|---|---|---|
| P1 | Strip a trailing dimension group from `line`; parse it into the vitola's `format` when the vitola has none | 93 lines |
| P2 | When `line` ends with a shape word **and** the record has exactly one vitola whose name is that same shape → move the shape out of the line | 58 lines |
| P3 | Collapse lines equal after normalization (case, diacritics, `-`/space, roman↔arabic numerals) | 9 lines |
| P4 | Strip a leading run of brand/line tokens from vitola names, guarded: single-char tokens are kept (`Siglo I` ≠ `Siglo V`), never merge when real dimensions conflict | 419 rows |
| P5 | Normalize fraction glyphs (`1⁄4`, `⅜`) and `X`→`x` in every format string | corpus-wide |

Each pass writes what it did to the apply report. **A hand-written taxonomy file always
wins over an auto-pass result** — the auto-pass is the floor, not the ceiling.

---

## 6. Phase 2 — brand repair (one agent, ~64 brands, do before Phase 3)

Brand names must be right before lines can be judged, because a truncated brand pushes
its tail token into every line name.

Work the `brand_truncated` list from the audit. For each, verify the real brand name with
the maker's own site, then write the brand's taxonomy file with only:

```json
{ "brand": "Roma", "renameBrand": "RoMa Craft Tobac", "status": "brand-only" }
```

Known from the audit (verify each, do not trust this list blindly):
`Roma` → RoMa Craft · `Black Label` → Black Label Trading Company · `Laura` → Laura Chavin ·
`Cavalier` → Cavalier Genève · `Marca` → Marca Fina · `Gh` → G.H. … · `Black Works` →
Black Works Studio · `El Viejo` → El Viejo Continente · `Maria` → Maria Mancini ·
`Karen` → Karen Berger · `Valentino` → Valentino Siesto · `Hr` → H.R. · `Leon` → Leon Jimenes ·
`Leaf` → Leaf by Oscar · `Man O. War` + `Man O' War` → one brand · `Toraño` / `Torano` → one brand ·
`Jose` → José L. Piedra (check against the Habanos invariant in `integrity.test.ts`).

Also fix class I here: `Craft C gnon` → `CroMagnon` (character loss in ingest — check the
raw catalog to see whether the loss is upstream and needs a scraper fix too).

Every renamed brand needs a `brands.json` entry under the new name (story, country,
founded). Merge the two entries when two brands collapse; keep the richer blurb.

**Deliverable:** ~64 taxonomy files with `renameBrand`, plus `brands.json` updates,
plus a note in the plan for anything unverifiable.

---

## 7. Phase 3 — per-brand taxonomy review (the bulk; parallel agents)

### 7.1 The file an agent writes

`app/scripts/data/taxonomy/<brand-slug>.json` — the slug is of the **current** brand key,
so the filename never moves.

```jsonc
{
  "brand": "La Galera",              // current key in cigars.json
  "renameBrand": null,               // canonical name, or null to keep
  "status": "done",                  // "todo" | "partial" | "done"
  "reviewedAt": "2026-07-24",
  "sources": [
    "https://lagaleracigars.com/our-cigars",
    "https://humidor.hr/hr/proizvod/la-galera-connecticut-pegador"
  ],

  // raw line string in cigars.json  ->  what it really is
  "lines": {
    "Habano Robusto Chaveta 5 X 50":   { "line": "Habano",      "vitola": "Chaveta",    "shape": "Robusto" },
    "Habano Toro 6 X 54":              { "line": "Habano",      "vitola": "El Lector",  "shape": "Toro"    },
    "Habano Half Corona 3 1⁄2 X 46":   { "line": "Habano",      "vitola": "Half Corona","shape": "Petit Corona" },
    "Corojo Chaveta":                  { "line": "Corojo",      "vitola": "Chaveta",    "shape": "Robusto" },
    "Connecticut":                     { "line": "Connecticut" },
    "Rojo Gift Pack":                  { "line": "Rojo Gift Pack", "sampler": true },
    "Anemoi Anemoi":                   { "line": "Anemoi" },
    "Anemoi 6 3⁄8 X 52":               { "line": "Anemoi",      "vitola": "Toro" }
  },

  // per-vitola renames inside a line: "<line>::<current vitola name>" -> new name
  "vitolaRenames": {
    "Connecticut::No.4": "Bonchero No.4",
    "Connecticut::Corona": "Half Corona"
  },

  // generic family per vitola, when name is proprietary
  "shapes": {
    "1936::Chaveta": "Robusto",
    "1936::El Lector": "Toro",
    "1936::Pilón": "Gordo"
  },

  // lines that LOOK like duplicates but are genuinely distinct — silences the guard
  "keepSeparate": [
    ["Flor de Connecticut", "Flor de Corojo"],
    ["Imperial Jade", "Imperial Jade Reserva"]
  ],

  // line-level story, hr + en; short, factual, no marketing copy
  "lineNotes": {
    "1936": {
      "hr": "Jezgrena linija imenovana po godini osnutka tvornice; vitole nose imena zanata iz tabaquerije.",
      "en": "The core line, named for the factory's founding year; vitolas are named after tabaquería crafts."
    }
  },

  // anything the agent could NOT verify — never guess, always list
  "unresolved": [
    "Anemoi Notus: no shop lists dimensions; format left as '—'"
  ]
}
```

Rules for the agent, non-negotiable:

1. **Never invent.** A line name, vitola name or dimension that cannot be verified goes
   into `unresolved`, unchanged in the data.
2. **The maker's site is the authority** for line and vitola names; shops only for price,
   availability and dimensions.
3. **Wrapper variants are lines, not vitolas** (`Connecticut`, `Habano`, `Maduro`,
   `Corojo` are separate lines when the maker sells them as such).
4. **A size variant is a vitola, not a line** (`Monticello Double` → vitola of
   `Monticello`; `Gold Label Half` → vitola of `Gold Label`).
5. **Keep the maker's vitola name** in `name`; put the generic family in `shapes`.
6. **Samplers stay one line, one vitola**, contents go in `lineup`.
7. Edit **only** your own brand file. Never `cigars.json`, never another brand's file,
   never a script.

### 7.2 Definition of done, per brand

The agent runs and pastes the output:

```bash
python app/scripts/apply-taxonomy.py && python app/scripts/taxonomy-report.py --brand "<Brand>"
```

Accepted when: the tree reads like the maker's own catalogue, no line contains a size,
no vitola repeats its line, `npm test` is green, and `unresolved` is honest.

### 7.3 Waves

Do them in this order — each wave is independently shippable.

| Wave | Brands | Records | Who |
|---|---|---|---|
| **W1** | 39 brands with ≥ 20 lines | 1276 (41 %) | 4–6 agents, ~7 brands each |
| **W2** | 135 brands with 5–19 lines | 1250 (40 %) | 6–8 agents, ~18 brands each |
| **W3** | 165 brands with 2–4 lines | 456 (15 %) | 3–4 agents |
| **W4** | 123 single-line brands | 123 (4 %) | 1 agent — mostly confirming `line == brand`, class H |

W1 first: 39 brands buy 41 % of the corpus and contain every hard case.
W1 brand list (by record count): Oscar Valladares, Rocky Patel, Perdomo, Gurkha, Villiger,
E.P. Carrillo, La Galera, Drew Estate, Davidoff, Alec Bradley, Arturo Fuente, La Aurora,
My Father, Padilla, Kristoff, Tatuaje, Black Label, Padrón, Roma, Aganorsa Leaf, PDR,
Casdagli, Caldwell, CAO, Ashton, Joya de Nicaragua, Montecristo, Oliva, Camacho, Eiroa,
Flor de Selva, Plasencia, 1502, Artista, Casa Turrent, Cavalier, La Aroma de Cuba, Laura,
Leonel.

Habanos brands (Cohiba, Montecristo, Partagás, …) carry hard invariants in
`integrity.test.ts` — country must stay `Kuba`, wrapper must stay Cuban. Their lines are
also the best-documented in the corpus; treat them as reference examples.

---

## 8. Phase 4 — three-level UI (one frontend agent, can run in parallel with Phase 3)

Data derivations, `app/src/data/index.ts`:

```ts
export interface BrandNode { brand: string; info?: BrandInfo; lines: Cigar[]; vitolaCount: number; minPriceEUR: number | null }
export const BRAND_INDEX: BrandNode[]                    // sorted per §2
export const linesByBrand: (brand: string) => Cigar[]    // sorted per §2
export const vitolaSlug: (v: Vitola) => string
export const resolveCigarId: (id: string) => Cigar | undefined  // follows cigarIdAliases.json
```

Screens:

- **`BrandSheet`** — brand story on top, then **lines only**. Each row: line name,
  wrapper, `N vitola`, price range `from X €`. It must not show vitola names any more
  (it currently shows `c.vitola` when there is one vitola — that is the level leak).
- **`LineSheet`** (new, `app/src/components/LineSheet.tsx`) — line name + `lineNotes`
  story + strength/body meters + the **full vitola table**: name, shape, `ring × length`,
  smoke time, price, buy link. Tapping a row opens the vitola.
- **`DetailSheet`** — already shows a single chosen vitola (Stream G). Keep that; add a
  breadcrumb `Brand › Line › Vitola` where each crumb navigates up.
- **`VitolaPicker`** — becomes redundant for browse (the LineSheet *is* the picker); keep
  it for the pairing flow where a vitola must be chosen without leaving the screen.

Routing, `app/src/store/route.ts` — deep links for all three levels:

```
#/catalog/brand/<brandSlug>
#/catalog/line/<cigarId>
#/catalog/vitola/<cigarId>/<vitolaSlug>
```

Search must hit all three levels and say which it hit — a query matching a vitola name
should offer the vitola, its line, and its brand as three distinct results.

---

## 9. Phase 5 — guards so this cannot rot again

- CI: `apply-taxonomy.py --check` and `normalize-vitolas.py --check` must be clean.
- CI: `npm test` includes the §4.4 invariants.
- `taxonomy-audit.py --fail-on-new` — a new brand or line entering the corpus without a
  taxonomy file fails the build. **This is what stops the next bulk import from silently
  re-shattering the tree.**
- The ingest itself (`build-market-cigars.py`) keeps minting raw lines — that is fine and
  intended. It just cannot reach `cigars.json` without passing through `apply-taxonomy.py`.

---

## 10. File ownership (collision-free)

| File | Writer | Reader |
|---|---|---|
| `app/scripts/taxonomy-audit.py` | core | everyone |
| `app/scripts/apply-taxonomy.py` | core | pipeline, CI |
| `app/scripts/taxonomy-report.py` | core | brand agents |
| `app/scripts/data/taxonomy/<brand>.json` | **exactly one brand agent** | apply-taxonomy |
| `app/scripts/output/taxonomy_audit.json` | taxonomy-audit | brand agents |
| `app/scripts/output/taxonomy_apply_report.json` | apply-taxonomy | review |
| `app/src/data/cigars.json` | **apply-taxonomy only** | app |
| `app/src/data/cigarIdAliases.json` | apply-taxonomy (append-only) | app |
| `app/src/data/brands.json` | Phase-2 agent | app |
| `app/src/types.ts`, `index.ts`, `components/*`, `store/route.ts` | frontend agent | app |
| `app/src/data/integrity.test.ts` | core (Phase 0), frontend agent may add | CI |

---

## 11. Sequencing

```
Phase 0 (core)  ──►  Phase 1 (core)  ──►  Phase 2 (brands)  ──►  Phase 3 W1 ─► W2 ─► W3 ─► W4
                                     └──►  Phase 4 (frontend, parallel)
Phase 5 lands with Phase 0 and tightens after each wave.
```

Phase 4 can start as soon as Phase 0 defines the derivations — it reads the shape, not
the content.

---

## 12. Ready-to-paste Cursor prompts

### Phase 2 — brand repair
> Repo cigar-pairing, branch off master. Open `app/scripts/output/taxonomy_audit.json`
> and take the `brand_truncated` list. For each brand, find the real full brand name on
> the maker's own site (not a shop). Write **one file per brand** at
> `app/scripts/data/taxonomy/<brand-slug>.json` containing only
> `{ "brand": "<current>", "renameBrand": "<canonical>", "status": "brand-only", "sources": [...] }`.
> If two current brands are the same maker, give both the same `renameBrand` — they will
> merge. Add or merge the `brands.json` entry for every new canonical name (country,
> founded, hr+en blurb). Do NOT touch `cigars.json` or any script. If you cannot verify a
> brand name, leave its file out and list it in your summary. Then run
> `python app/scripts/apply-taxonomy.py && npm test` from `app/` and paste the result.

### Phase 3 — per-brand taxonomy (one agent, brands `{LIST}`)
> Repo cigar-pairing. You own exactly these brands: **{LIST}**. For each one:
> 1. Read its section in `app/scripts/output/taxonomy_audit.json` and run
>    `python app/scripts/taxonomy-report.py --brand "<Brand>"` to see the current tree.
> 2. Find the maker's real catalogue (maker's own site is the authority; shops only for
>    price/dimensions/availability) and work out the true **lines** and, inside each line,
>    the true **vitolas**.
> 3. Write `app/scripts/data/taxonomy/<brand-slug>.json` per the schema in
>    `docs/superpowers/plans/2026-07-23-cigar-taxonomy-brand-line-vitola.md` §7.1.
>
> Rules: a wrapper variant (Connecticut / Habano / Maduro / Corojo) is its own LINE; a
> size variant (`Monticello Double`, `Gold Label Half`) is a VITOLA of the parent line;
> keep the maker's own vitola name in `vitola` and put the generic family in `shapes`;
> never put a dimension in a line name; samplers stay one line with one vitola.
> **Never invent anything** — whatever you cannot verify goes into `unresolved` and the
> data stays as it is.
>
> You may edit ONLY your own brand files. Not `cigars.json`, not another brand's file,
> not any script. When done, from `app/` run
> `python scripts/apply-taxonomy.py && python scripts/taxonomy-report.py --brand "<Brand>" && npm test`
> and paste the tree for each brand plus the test result. One commit per brand,
> message `taxonomy(<brand>): lines + vitolas`.

### Phase 4 — frontend
> Repo cigar-pairing. Implement the three-level navigation from
> `docs/superpowers/plans/2026-07-23-cigar-taxonomy-brand-line-vitola.md` §8:
> `BRAND_INDEX` / `linesByBrand` / `resolveCigarId` derivations in `app/src/data/index.ts`,
> a new `LineSheet` component, `BrandSheet` reduced to lines only, a
> `Brand › Line › Vitola` breadcrumb in `DetailSheet`, deep-link routes for all three
> levels, and search that returns brand / line / vitola hits as distinct results.
> Add `shape`, `ring`, `lengthMM` to the `Vitola` type (all optional). No data edits.
> `tsc`, `vitest` and `build` must be green.

---

## 13. Acceptance — how we know it is fixed

1. `(brand, line)` is unique; the record count drops from 3105 to roughly the real number
   of lines (expect ~1200–1600).
2. No line name contains a dimension or ends with a bare shape word.
3. No vitola name repeats its line's tokens.
4. Every one of the 462 brands has a taxonomy file with `status: "done"`.
5. Opening a brand shows the story + lines. Opening a line shows the line + all its
   vitolas. Opening a vitola shows that vitola only.
6. `apply-taxonomy.py --check` and `normalize-vitolas.py --check` exit 0 on a fresh clone.
7. `npm test` green, including every §4.4 invariant.
8. Spot check: La Galera reads like §4.3, not like 48 flat rows.

---

## 14. Open questions for the owner

1. **Wrapper variants** — `Oliva Flor de Connecticut` / `Corojo` / `Maduro` / `Gold`:
   separate lines (assumed here), or one `Flor de Oliva` line with a wrapper facet?
   The assumption is "separate lines" because that is how makers and shops sell them.
2. **Record-count drop** — merging ~3105 records into ~1400 lines will change ids and
   shrink the catalogue count shown in the UI. The alias map keeps links working, but the
   headline number goes down. Assumed acceptable; say so if the count matters.
3. **Line stories** — `lineNotes` is optional per line. Filling ~1400 of them is a
   separate content pass; this plan only creates the slot. Assumed: fill W1 brands first.
