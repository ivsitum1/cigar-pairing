# Digestifs Category + Club101 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a curated top-level `digestif` drink category (~12 bottles) with Shopping buffet segments and Pairing/Catalog chips, plus one Club101 Pića lesson (`d-digestif`).

**Architecture:** Hand-curated `digestifs.json` (same shape as coffee/wine curated catalogs), registered in `DRINKS` via `DrinkCategory`. Reuse existing body/sweetness pairing engine — no category-specific scoring rules in v1. Club101 card is content-only in `club101.json`.

**Tech Stack:** TypeScript, Vite React app, Vitest, static JSON catalogs, existing `shoppingPicks` / `pairing` / Club101 renderers.

## Global Constraints

- Spec: [`docs/superpowers/specs/2026-07-27-digestifs-regional-liqueurs-design.md`](../specs/2026-07-27-digestifs-regional-liqueurs-design.md)
- Audit shortlist: [`01_work/output/DIGESTIF-REGIONAL-AUDIT.md`](../../01_work/output/DIGESTIF-REGIONAL-AUDIT.md)
- Approach **A + C** only (no brandy `liqueur` dump; no vermouth)
- Category code: `digestif`; labels: HR **Biljni digestivi**, EN **Herbal digestifs**
- Exactly the 12 shortlist bottles; Agwa stays in `local-unique` with pelinkovac
- Verified `priceUrl` from AlleZ/Ecuga only — no fabricated prices; `priceApprox: true` when range is estimate
- No brand cigar rankings; notes from shop/style facts only
- Commit messages in English; do not `git config`
- Verify from `app/`: `npx tsc -b --noEmit`, `npm test -- src/lib/shoppingPicks.test.ts src/data/integrity.test.ts src/data/club101.test.ts`

## File map

| File | Responsibility |
|------|----------------|
| `app/src/types.ts` | Add `"digestif"` to `DrinkCategory` |
| `app/src/data/digestifs.json` | Curated catalog (12 drinks) |
| `app/src/data/index.ts` | Import + `DRINKS.digestif` + `ALL_DRINKS` |
| `app/src/lib/shoppingPicks.ts` | Five `BUCKETS.digestif` segments |
| `app/src/lib/shoppingPicks.test.ts` | Include `digestif` in `CATS` |
| `app/src/pages/ShoppingPage.tsx` | `CATEGORIES` includes `digestif` |
| `app/src/pages/CatalogPage.tsx` | `TABS` includes `digestif` |
| `app/src/pages/PairingPage.tsx` | `DRINK_TYPE_FILTERS` + `SUGGEST_CATEGORIES` |
| `app/src/i18n/index.tsx` | `cat.digestif` + `STYLE_LABELS` for new styles |
| `app/src/data/club101.json` | Append `d-digestif` to `tracks.drinks` |
| `app/src/data/club101.test.ts` | Assert id + content smoke |
| `app/src/data/integrity.test.ts` | Should pass via `ALL_DRINKS` / `DRINKS` (no edit unless fails) |

Do **not** change `brandy_shared.py` NON_PAIRABLE in this PR.

---

### Task 1: Extend `DrinkCategory` + failing category wiring tests

**Files:**
- Modify: `app/src/types.ts`
- Modify: `app/src/lib/shoppingPicks.test.ts`
- Test: `app/src/lib/shoppingPicks.test.ts`

**Interfaces:**
- Consumes: existing `DrinkCategory`, `DRINKS`, `buffetFive`
- Produces: `"digestif"` as a valid `DrinkCategory` member (catalog still empty until Task 2–3)

- [ ] **Step 1: Add failing assertion that `DRINKS` exposes digestif**

In `shoppingPicks.test.ts`, extend `CATS`:

```ts
const CATS: DrinkCategory[] = [
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
  "digestif",
];
```

Add a focused test (or extend the buffet loop) that will fail until JSON is wired:

```ts
  it("digestif ima pet buffet segmenata i barem jednu bocu po segmentu", () => {
    expect(BUCKETS.digestif?.length).toBe(5);
    const picks = buffetFive("digestif", DRINKS.digestif, nitko);
    expect(picks.length).toBe(5);
    const styles = new Set(picks.map((p) => p.bucket.id));
    expect(styles.size).toBe(5);
  });
```

- [ ] **Step 2: Run test — expect FAIL**

Run: `cd app && npm test -- src/lib/shoppingPicks.test.ts`

Expected: TypeScript/compile or runtime failure (`digestif` not in union / `DRINKS.digestif` missing / buckets missing).

- [ ] **Step 3: Add type member only**

In `app/src/types.ts`:

```ts
export type DrinkCategory =
  | "rum"
  | "whisky"
  | "brandy"
  | "wine"
  | "coffee"
  | "tequila"
  | "gin"
  | "digestif";
```

- [ ] **Step 4: Commit type + failing test**

```bash
git add app/src/types.ts app/src/lib/shoppingPicks.test.ts
git commit -m "test: require digestif category wiring for buffet five"
```

---

### Task 2: Curated `digestifs.json` (12 bottles)

**Files:**
- Create: `app/src/data/digestifs.json`
- Test: smoke via later integrity run

**Interfaces:**
- Consumes: audit shortlist + verified shop URLs
- Produces: `Drink[]` with `category: "digestif"` and styles matching Task 3 buckets

- [ ] **Step 1: Create JSON array with these 12 entries**

Use the same field set as curated spirits (see Grand Marnier / coffee entries). Required per bottle: `id`, `category`, `name`, `style`, `region`, `abv`, `body`, `sweetness`, `flavorTags`, `qualityScore`, `priceEUR` (or null), `shopHR`, `pairable: true`, `serving.best`, `notes` `{hr,en}`, `priceUrl` when known.

| id | name | style | region | abv | body | sweet | shopHR | priceUrl |
|----|------|-------|--------|-----|------|-------|--------|----------|
| `dg-becherovka` | Becherovka | `herbal-bitter-central` | Češka | 38 | 3 | 3 | ecuga.com | `https://ecuga.com/proizvod/becherovka` |
| `dg-unicum-zwack` | Unicum Zwack | `herbal-bitter-central` | Mađarska | 40 | 4 | 2 | ecuga.com | `https://ecuga.com/proizvod/unicum-zwack` |
| `dg-fernet-branca` | Fernet Branca | `fernet` | Italija | 35 | 4 | 2 | ecuga.com | `https://ecuga.com/proizvod/branca-fernet` |
| `dg-averna` | Averna Amaro | `herbal-bitter-italian` | Sicilija, Italija | 29 | 3 | 3 | ecuga.com | `https://ecuga.com/proizvod/averna-amaro` |
| `dg-nonino-amaro` | Nonino Amaro Quintessentia | `herbal-bitter-italian` | Italija | 35 | 3 | 3 | allez.hr | `https://allez.hr/shop/svi-proizvodi/amaro-nonino-quintessentia-liquore-35-vol-07l-u-poklon-kutiji` |
| `dg-chartreuse-verte` | Chartreuse Verte | `herbal-monastic` | Francuska | 55 | 4 | 3 | allez.hr | `https://allez.hr/shop/svi-proizvodi/chartreuse-liqueur-verte-55-vol-07l` (confirm slug from AlleZ scrape / live page) |
| `dg-chartreuse-jaune` | Chartreuse Jaune | `herbal-monastic` | Francuska | 43 | 3 | 4 | allez.hr / ecuga.com | AlleZ jaune URL or `https://ecuga.com/proizvod/chartreuse-yellow` |
| `dg-benedictine` | Dom Benedictine | `herbal-monastic` | Francuska | 40 | 3 | 4 | allez.hr | AlleZ Dom Benedictine product URL |
| `dg-strega` | Strega Liquore | `herbal-saffron-yellow` | Italija | 40 | 3 | 4 | allez.hr / ecuga.com | AlleZ or `https://ecuga.com/proizvod/strega` |
| `dg-galliano` | Galliano L'Autentico | `herbal-saffron-yellow` | Italija | 42.3 | 3 | 4 | allez.hr | AlleZ Galliano URL |
| `dg-aura-pelinkovac` | Aura Pelinkovac Gorki | `pelinkovac` | Istra, Hrvatska | 30.8 | 3 | 2 | ecuga.com | `https://ecuga.com/proizvod/aura-pelinkovac-gorki` |
| `dg-agwa` | Agwa de Bolivia | `specialty-botanical` | Bolivija / NL | 30 | 3 | 3 | ecuga.com | `https://ecuga.com/proizvod/agwa-de-bolivia` |

**Serving:** all `serving.best` ≈ `"Čisto, hladno"` / note cold neat in `notes` where style demands (Fernet, Becherovka).

**Tags (examples, evidence-based):**  
Becherovka → `cimet`, `klinčić`, `bilje`; Fernet → `menta`, `gorcina`, `bilje`; Pelinkovac → `pelin`, `gorcina`; Chartreuse → `bilje`, `zacini`; Strega → `safran`, `bilje`; Agwa → `menta`, `bilje`, `zeleni-caj`.

**qualityScore:** use 7–8 for classics (no fake luxury rankings).  
**priceEUR:** set from live page when known (e.g. Becherovka ~14, Fernet 1L ~24, Agwa ~24, Unicum ~20, Aura ~26, Chartreuse Yellow ~52); otherwise `{min,max}` with `priceApprox: true` or `null`.

**additiveStatus:** `"flavored"` + short `additiveDetail` that these are herbal liqueurs / bitters (EU spirit drink / liqueur), not whisky/brandy — honest labeling like Grand Marnier entry.

Confirm AlleZ Chartreuse/Benedictine/Galliano/Strega/Nonino slugs against [`01_work/output/digestif_allez_raw.json`](../../01_work/output/digestif_allez_raw.json) before commit.

- [ ] **Step 2: Spot-check JSON**

```bash
cd app && node -e "const d=require('./src/data/digestifs.json'); console.log(d.length, [...new Set(d.map(x=>x.style))])"
```

Expected: `12` and styles covering the six style ids above.

- [ ] **Step 3: Commit catalog**

```bash
git add app/src/data/digestifs.json
git commit -m "data: add curated digestif catalog shortlist"
```

---

### Task 3: Wire `DRINKS`, UI category lists, i18n

**Files:**
- Modify: `app/src/data/index.ts`
- Modify: `app/src/pages/ShoppingPage.tsx`
- Modify: `app/src/pages/CatalogPage.tsx`
- Modify: `app/src/pages/PairingPage.tsx`
- Modify: `app/src/i18n/index.tsx`

**Interfaces:**
- Consumes: `digestifs.json`
- Produces: `DRINKS.digestif`, visible chips in Catalog / Shopping / Pairing

- [ ] **Step 1: Register in `index.ts`**

```ts
import digestifs from "./digestifs.json";

export const DRINKS: Record<DrinkCategory, Drink[]> = {
  rum: rums as unknown as Drink[],
  whisky: whiskies as unknown as Drink[],
  brandy: brandies as unknown as Drink[],
  wine: wines as unknown as Drink[],
  coffee: coffees as unknown as Drink[],
  tequila: tequilas as unknown as Drink[],
  gin: gins as unknown as Drink[],
  digestif: digestifs as unknown as Drink[],
};

export const ALL_DRINKS: Drink[] = [
  ...DRINKS.rum,
  ...DRINKS.whisky,
  ...DRINKS.brandy,
  ...DRINKS.wine,
  ...DRINKS.coffee,
  ...DRINKS.tequila,
  ...DRINKS.gin,
  ...DRINKS.digestif,
];
```

- [ ] **Step 2: Append `"digestif"` to page category arrays**

- `ShoppingPage.tsx` `CATEGORIES`
- `CatalogPage.tsx` `TABS` (after `gin` or before coffee — prefer after `gin`)
- `PairingPage.tsx` `DRINK_TYPE_FILTERS` and `SUGGEST_CATEGORIES`

- [ ] **Step 3: i18n labels**

In `STRINGS`:

```ts
  "cat.digestif": { hr: "Biljni digestivi", en: "Herbal digestifs" },
```

In `STYLE_LABELS`:

```ts
  "herbal-bitter-central": { hr: "Srednjoeuropski biljni biter", en: "Central European herbal bitter" },
  "herbal-bitter-italian": { hr: "Talijanski amaro", en: "Italian amaro" },
  fernet: { hr: "Fernet", en: "Fernet" },
  "herbal-monastic": { hr: "Monastički biljni", en: "Monastic herbal" },
  "herbal-saffron-yellow": { hr: "Žuti biljni (šafran)", en: "Yellow herbal (saffron)" },
  pelinkovac: { hr: "Pelinkovac", en: "Pelinkovac" },
  "specialty-botanical": { hr: "Jedinstveni botanik", en: "Specialty botanical" },
```

- [ ] **Step 4: Typecheck**

Run: `cd app && npx tsc -b --noEmit`  
Expected: PASS (or only pre-existing errors unrelated to digestif).

- [ ] **Step 5: Commit wiring**

```bash
git add app/src/data/index.ts app/src/pages/ShoppingPage.tsx app/src/pages/CatalogPage.tsx app/src/pages/PairingPage.tsx app/src/i18n/index.tsx
git commit -m "feat: wire digestif category through catalog, shopping and pairing"
```

---

### Task 4: Shopping buffet buckets for digestif

**Files:**
- Modify: `app/src/lib/shoppingPicks.ts`
- Test: `app/src/lib/shoppingPicks.test.ts`

**Interfaces:**
- Consumes: digestif styles from Task 2
- Produces: `BUCKETS.digestif` length 5 so `buffetFive` covers the spectrum

- [ ] **Step 1: Add buckets**

```ts
  digestif: [
    {
      id: "central-bitter",
      label: { hr: "Središnja Europa", en: "Central Europe" },
      styles: ["herbal-bitter-central"],
    },
    {
      id: "italian-bitter",
      label: { hr: "Talijanski gorki", en: "Italian bitter" },
      styles: ["herbal-bitter-italian", "fernet"],
    },
    {
      id: "monastic",
      label: { hr: "Monastički", en: "Monastic" },
      styles: ["herbal-monastic"],
    },
    {
      id: "yellow-herbal",
      label: { hr: "Žuti biljni", en: "Yellow herbal" },
      styles: ["herbal-saffron-yellow"],
    },
    {
      id: "local-unique",
      label: { hr: "Lokalno / jedinstveno", en: "Local / unique" },
      styles: ["pelinkovac", "specialty-botanical"],
    },
  ],
```

- [ ] **Step 2: Run shoppingPicks tests**

Run: `cd app && npm test -- src/lib/shoppingPicks.test.ts`  
Expected: PASS, including the digestif buffet test from Task 1.

- [ ] **Step 3: Commit**

```bash
git add app/src/lib/shoppingPicks.ts app/src/lib/shoppingPicks.test.ts
git commit -m "feat: add digestif shopping buffet segments"
```

---

### Task 5: Club101 lesson `d-digestif` (approach C)

**Files:**
- Modify: `app/src/data/club101.json`
- Modify: `app/src/data/club101.test.ts`

**Interfaces:**
- Consumes: existing drinks-track card shape (`d-gin-pairing`)
- Produces: bilingual lesson ≥650 chars/lang with `•` bullets; no shopLinks required (Ecuga URLs are not in the shopLinks allowlist which only permits allez/humidor — skip shopLinks or use AlleZ category URL `https://allez.hr/shop/likeri` if linking)

- [ ] **Step 1: Failing test**

```ts
  it("pica 101 pokriva biljne digestive", () => {
    const ids = club101.tracks.drinks.map((c) => c.id);
    expect(ids).toContain("d-digestif");
    const card = club101.tracks.drinks.find((c) => c.id === "d-digestif");
    expect(card?.body.hr.toLowerCase()).toMatch(/becherovka|pelinkovac|chartreuse|fernet/);
    expect(card?.body.en.toLowerCase()).toMatch(/becherovka|pelinkovac|chartreuse|fernet/);
    expect(card!.body.hr.length).toBeGreaterThanOrEqual(650);
    expect(card!.body.en.length).toBeGreaterThanOrEqual(650);
  });
```

- [ ] **Step 2: Run — expect FAIL**

Run: `cd app && npm test -- src/data/club101.test.ts`

- [ ] **Step 3: Append card after last drinks entry**

Outline for `body.hr` / `body.en` (mirror gin lesson structure):

```
Intro: biljni digestiivi uz cigaru — gorčina čisti nepce; nisu rum/whisky/konjak.

SREDIŠNJA EUROPA
• Becherovka — …
• Unicum — …

TALIJANSKI GORKI
• Fernet — …
• Averna / Nonino Amaro — …

MONASTIČKI I ŽUTI BILJNI
• Chartreuse / Benedictine — …
• Strega / Galliano — …

LOKALNO I JEDINSTVENO
• Pelinkovac — …
• Agwa — …

UZ CIGARU
• Hladno, neat, mali gutljaji
• Gorči profili uz maduro / punije tijelo; slađi monastički uz srednje
• Ne zamijeniti s krem-likerima i punch bocama
```

Titles: `{ hr: "Biljni digestivi uz cigaru", en: "Herbal digestifs with a cigar" }`.

- [ ] **Step 4: Run club101 tests — PASS**

- [ ] **Step 5: Commit**

```bash
git add app/src/data/club101.json app/src/data/club101.test.ts
git commit -m "feat: add Club 101 lesson for herbal digestifs"
```

---

### Task 6: Full verification

**Files:** none new

- [ ] **Step 1: Integrity + typecheck + focused suites**

```bash
cd app
npx tsc -b --noEmit
npm test -- src/lib/shoppingPicks.test.ts src/data/integrity.test.ts src/data/club101.test.ts
```

Expected: all green. Fix any integrity failures (duplicate ids, missing notes, category mismatch).

- [ ] **Step 2: Manual smoke (optional if browser available)**

Open `http://localhost:5173/cigar-pairing/` → Catalog shows Biljni digestivi → Shopping buffet five for digestif → Pairing filter includes category → Club 101 Pića shows new lesson.

- [ ] **Step 3: Final commit only if fixes landed**

```bash
git status
# commit any integrity fixes if needed
```

---

## Spec coverage check

| Spec requirement | Task |
|------------------|------|
| New `DrinkCategory` `digestif` | 1, 3 |
| Curated ~12 bottles + shop URLs | 2 |
| Shopping buckets (5 segments), Agwa in local-unique | 4 |
| Pairing / Catalog / Shopping chips | 3 |
| i18n Biljni digestivi | 3 |
| Club101 companion | 5 |
| No brandy pipeline rewrite | (explicit non-touch) |
| No vermouth / cream / Cynar | Task 2 table |
| Reuse pairing engine | implicit (no engine edit) |

## Placeholder scan

No TBD steps; bottle URLs that need AlleZ slug confirmation are called out with the scrape JSON path.
