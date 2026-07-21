# Cigar index cleanup — handoff

Context for continuing the cigar-catalog cleanup. Read this first, then work
through the **Davidoff pass** below.

## What this is

`app/src/data/cigars.json` (and `brands.json`) accumulated duplicates and
messy records from spreadsheet imports and an "Additional Vitolas → named
lines" remap. We've been cleaning it brand by brand. This doc records the
conventions, what's already done, and the remaining Davidoff plan.

## Repo conventions & gotchas (IMPORTANT)

- **JSON formatting must round-trip exactly** or you get a 50k-line diff.
  - `cigars.json`: `json.dump(data, fh, ensure_ascii=False, indent=2)` then append a trailing `"\n"`.
  - `brands.json`: same but `indent=1`.
  - Verify with: `json.dumps(json.load(open(f)), ensure_ascii=False, indent=N)+"\n" == open(f).read()`.
  - Prefer **targeted `Edit`** for 1–2 line changes; use a Python round-trip only for bulk edits, matching the indent above.
- **Never say "boca"** (bottle) for cigars — use *cigara / vitola / linija / brend*. ("Piće" is for drinks.)
- **Tests**: `cd app && npx vitest run` (expect 125 passing), `npx tsc -b`, `npx vite build`. All must stay green.
  - Key guards in `app/src/data/cigars.data.test.ts` and `integrity.test.ts`: unique ids, brands↔cigars 1:1 coverage, no `?s=`/`post_type=product` URLs, shop URL shares a token with brand/line/vitola, body/strength in 1–5, every cigar has ≥1 vitola, every drink `pairable:true`.
- **Runtime dedupe**: `app/src/lib/cigarVitola.ts` `uniqueVitolas()` dedupes vitolas by lowercased name at render time; `resolveDefaultVitola()` picks the priced/HR product vitola. `index.ts` `dedupeCigars()` keeps one record per id. So fixes belong in the **data**, not just runtime.
- **Display**: cigar shows `brand + line`; vitola picker lists `vitolas[]`. Country via `cn()`, region via `rgn()` (`app/src/i18n/`). HR shows the raw data string; EN via `COUNTRY_LABELS`/`REGION_LABELS`.
- **Ids are stable identifiers** — changing `brand`/`line`/`vitola.name` is fine; avoid changing `id` (saved user collections key off it). Removing a duplicate entry is fine.

## Git / PR workflow

- Work on branch **`claude/linkovi-pretrazivanje-boca-n3rhht`**.
- Each change: restart from latest master —
  `git fetch origin master && git checkout -B claude/linkovi-pretrazivanje-boca-n3rhht origin/master`,
  make the change, then **force-push with lease**:
  `REMOTE=$(git ls-remote origin refs/heads/<branch> | cut -f1); git push --force-with-lease=<branch>:$REMOTE origin <branch>`.
- Open a PR to `master`; merging auto-deploys to GitHub Pages (`.github/workflows/deploy.yml`). PWA caches — hard-refresh to see changes.
- Commit trailer used this session:
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` and a `Claude-Session:` line.

## Already done (merged to master)

- **#18** buy/search links bulletproof (drinks): dropped `site:` search fallback (empty-result fix), stronger name↔URL matcher, 43 wrong `priceUrl`s nulled.
- **#19** country name: `Dominikana` → `Dominikanska Republika` (HR) / `Dominican Republic` (EN) across data, i18n maps, geo, notes.
- **#20** Cusano line `"18 / Dominican"` → `"Bundle Selection"`.
- **#21** Warped brand merge; index-wide **placeholder-vitola dedupe** (removed 76 `"X <ring>"` vitolas that duplicated the real named vitola, redirected 58 default `vitola` fields); Cohiba Siglo consolidation; line-name artifacts.
- **#22** Foundation + "Foundation Cigar Company" brand merge (Tabernacle + Charter Oak merged).
- **#23** Davidoff **Signature** (8 clean vitolas, SKU dupes collapsed, dims → `format`) + **Primeros** (6 fragments → 1 line, 5 blends).
- **#24** vitola-name normalization (dims → `format`), roman-numeral casing (Plasencia).
- **#25** audit: nulled 3 cross-brand contamination URLs (Cohiba→La Galera, Davidoff→1502, Perdomo→Aganorsa); removed 3 exact ASCII/unicode-fraction duplicate entries.

Index went ~543 → 529 cigars. `Signature` and `Primeros` Davidoff lines are already clean.

## THE DAVIDOFF PASS (to do)

Davidoff still has 26 entries with cross-line contamination and duplicate
sub-line entries. Target: one clean entry per real line, no vitola that
belongs to another line.

### 1. Nicaragua (`cig-davidoff-nicaragua`) — remove contamination + dupes
Currently 13 vitolas. **Remove** (they belong to Primeros, already in `cig-davidoff-primeros-by-davidoff-dominican`):
- `Primeros Nicaragua`, `Nicaragua Maduro`, `Davidoff Nicaragua`
**Remove** no-URL duplicates of a URL'd sibling:
- `Nicaragua Robusto` (dup of `Robusto`), `Box-Pressed` (dup of `Box Pressed`), `Nicaragua Toro` (dup of `Toro`)
**Keep**: `Corona`, `Diadema`, `Anni Le`, `Robusto`, `Robusto Tubos`, `Box Pressed`, `Toro`. Set a sensible default (`Robusto`).

### 2. Yamasa (`cig-davidoff-yamasa`) — remove contamination
**Remove** (belong to Escurio / Nicaragua / Late Hour):
- `Escurio Robusto Tubos 4 ½ x 54`, `Nicaragua Robusto Tubos`, `Nicaragua Toro 5 ½ x 54`, `WSC The Late Hour Robusto`, `WSC The Late Hour Churchill`
**Keep**: `Toro`, `Robusto`, `Yamasa Piramides`, `Churchill`.

### 3. Winston Churchill / The Late Hour / WSC — consolidate 6 entries → 2
"WSC" = Winston Churchill. Base line + a scotch-cask sub-line "The Late Hour".
- **Winston Churchill** (`cig-davidoff-davidoff-winston`): keep `Robusto`, `Toro`, `Churchill`; **fold in** `Belicoso` (from `cig-davidoff-wsc-belicoso`) and `Petit Panetela` (from `cig-davidoff-wsc-petit-panetela`). Note: base entries currently have no URLs — pull the URLs from the wsc-* entries.
- **Winston Churchill The Late Hour** (`cig-davidoff-wsc-the-late-hour`): keep `Robusto`, `Churchill` (late-hour URLs); **fold in** `Le 2025` (from `cig-davidoff-wsc-le-2025`); **remove** its `Belicoso` (that's base WSC, moved above).
- **Remove**: `cig-davidoff-winston-churchill` (dup of Late Hour), `cig-davidoff-wsc-belicoso`, `cig-davidoff-wsc-petit-panetela`, `cig-davidoff-wsc-le-2025`.
- Judgment call for the owner: keep "The Late Hour" as its own line (recommended) vs. a vitola set under Winston Churchill.

### 4. Escurio — consolidate 3 fragments → 1 "Escurio"
`cig-davidoff-escurio-gran` (Robusto, Toro, Gran Perfecto), `cig-davidoff-escurio-petit` (Robusto), `cig-davidoff-escurio-robusto-tubos` (Robusto, Robusto Tubos, + a no-URL `Escurio Robusto` dup).
- Merge into one **Escurio** line: `Petit Robusto`, `Robusto`, `Robusto Tubos`, `Toro`, `Gran Perfecto` (rename to disambiguate the two "Robusto"s by format/size). Drop the no-URL `Escurio Robusto` dup. Remove the two extra entries.

### 5. Millennium — merge 2 entries, fix spelling
`cig-davidoff-millenium` ("Millenium": Short Robusto, Robusto, Petit Corona, Le 2023, Robusto Tubos — `Robusto` and `Robusto Tubos` share URL `millenium-robusto-tubos-3` → dup) and `cig-davidoff-davidoff-millennium` ("Millennium Blend": Millennium Robusto/Piramides/Toro, no URLs).
- Merge into one **Millennium** line (correct spelling). Dedup `Robusto`/`Robusto Tubos`. Combine the distinct sizes (Short Robusto, Petit Corona, Robusto, Robusto Tubos, Piramides, Toro, Le 2023).

### 6. Small dupes
- **Demi Tasse** (`cig-davidoff-demi-tasse-4-x-25`): `Demi Tasse` listed twice (identical) → keep one. Consider line rename `"Demi Tasse 4 X 25"` → `"Demi Tasse"` (format already `25 x 102mm`).
- **Aniversario** (`cig-davidoff-aniversario`): `Short Perfecto` and `Perfecto` share URL `aniversario-short-perfecto-4` → keep one; `Special R` and `R Tubos` overlap (`special-r-tubos`) → verify/dedup.
- **Grand Cru**: `Diadema` URL is actually `grand-cru-diademas-finas-le-2024` (a Le 2024 limited) — relabel or move to a limited line.

## Update — Davidoff pass DONE

The whole Davidoff plan above is complete (merged): Nicaragua, Yamasa,
Winston Churchill / The Late Hour / WSC, Escurio, Millennium, plus the small
dupes. Davidoff is now 19 clean lines with no URL shared across lines.
Also merged: Joya de Nicaragua dup lines (Joya Red, Numero Uno Le Premier,
Rosalones) and the Arturo Fuente "Don Carlos 6 1/2 X 50" dimension-dup line.

### Still open — needs owner judgment (not auto-fixable)
1. **Arturo Fuente "Chateau & Cubans" vs "Chateau Fuente"** — heavy vitola
   overlap (Chateau Fuente, Fuente Pyramids, King T, T Rosado in both).
   Decide: merge into one "Chateau Fuente" line, or keep "& Cubans" for the
   small cuban-sized Fuentes (Exquisitos, Petit Corona, Cubanitos)?
2. **Lazy fallback URLs** — one shop URL reused across many distinct vitolas,
   so clicking (say) "Petit Upmann" or "Opus X" opens the wrong product:
   - H. Upmann: `h-upmann-half-corona` on ~13 Classic/Connossieur/Reserva vitolas.
   - Arturo Fuente: `cuban-corona` across Chateau/Gran Reserva/Hemingway/Opus X.
   Decision: null the URL on non-matching vitolas (they fall back to brand
   search) vs. leave. Recommend nulling.
3. **La Aurora dimension-named lines** (107 Robusto/Belicoso/Nicaragua…, 1903
   Edition Toro) share URLs with base lines but the "twin" is sometimes a
   *different* line (contamination), so they can't be removed blindly —
   check each against its base 107/1903/ADN/Family Reserve line.

## Other brands flagged by the audit (after Davidoff)

Shared fallback URLs across distinct lines — review case by case (some are
legit size fallbacks, some are contamination):
- **H. Upmann**: `half-corona` URL shared by Half Corona / Reserva & Churchill / Classic / Connossieur.
- **La Aurora**: `107` lines share URLs with Family Reserve / ADN / 1903 Edition.
- **Joya de Nicaragua**: Antaño 1970 Churchill uses a `1502-nicaragua-churchill` URL (contamination).
- **Arturo Fuente**: `cuban-corona` URL shared across Chateau & Cubans / Gran Reserva / Hemingway / Opus X (likely a fallback, not real).
- Ordinal casing artifacts in some line names (`20Th`, `5Th`, `71St`) — cosmetic.

## How to verify a Davidoff change

```
cd app && npx vitest run && npx tsc -b && npx vite build
```
Then re-dump Davidoff to eyeball structure:
```
python3 -c "import json;c=json.load(open('app/src/data/cigars.json'));[print(d['id'],'|',d['line'],'|',[v['name'] for v in d['vitolas']]) for d in c if d['brand']=='Davidoff']"
```
