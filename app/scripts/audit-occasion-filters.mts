/**
 * Simulacija prilike: sve cigare × pairable pića × jutro/poslijepodne/večer/any.
 * Soft-only: occasionKeep je no-op; soft occasion u pairDrinksForCigar
 * (par > doba dana; |occasion| < bodyPerStep).
 *
 * Run: npx vite-node scripts/audit-occasion-filters.mts
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { ALL_DRINKS, CIGARS } from "../src/data/index";
import { pairDrinksForCigar } from "../src/engine/pairing";
import {
  occasionKeep,
  rankByOccasion,
  type OccasionFilter,
} from "../src/engine/occasion";
import type { Cigar, Drink, DrinkCategory } from "../src/types";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(__dirname, "output", "occasion-audit");
const REPORT_PATH = join(
  __dirname,
  "..",
  "..",
  "01_work",
  "output",
  "OCCASION-FILTER-AUDIT.md",
);

const CATEGORIES: DrinkCategory[] = [
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
];

const OCCASIONS: OccasionFilter[] = ["any", "morning", "afternoon", "evening"];

type TopSlot = { drinkId: string; score: number; body: number; name: string };

type CigarTops = Record<
  OccasionFilter,
  Partial<Record<DrinkCategory, TopSlot>>
>;

function cigarLabel(c: Cigar): string {
  return `${c.brand} ${c.line}`;
}

function drinkLabel(d: Drink): string {
  return d.name;
}

function topsForCigar(
  cigar: Cigar,
  reasonTally?: { fit: number; clash: number },
): CigarTops {
  const out = {} as CigarTops;
  for (const occ of OCCASIONS) {
    const pool = ALL_DRINKS.filter(
      (d) => d.pairable && occasionKeep(occ, cigar.body)(d),
    );
    const scored = pairDrinksForCigar(
      cigar,
      pool,
      undefined,
      occ === "any" ? undefined : occ,
    );
    // isti izbor kao u UI-u: pojas izjednacenih po kategoriji, pa doba dana
    const ranked = CATEGORIES.flatMap((cat) =>
      rankByOccasion(
        scored.filter((r) => r.item.category === cat),
        cigar,
        occ === "any" ? undefined : occ,
      ),
    );
    if (reasonTally && occ !== "any") {
      // broji reason na top-1 po kategoriji (vidljive kartice)
      for (const cat of CATEGORIES) {
        const hit = ranked.find((r) => r.item.category === cat);
        if (!hit) continue;
        if (hit.reasons.some((r) => r.rule === "occasion-fit")) reasonTally.fit++;
        if (hit.reasons.some((r) => r.rule === "occasion-clash"))
          reasonTally.clash++;
      }
    }
    const slots: Partial<Record<DrinkCategory, TopSlot>> = {};
    for (const cat of CATEGORIES) {
      const hit = ranked.find((r) => r.item.category === cat);
      if (hit) {
        slots[cat] = {
          drinkId: hit.item.id,
          score: hit.score,
          body: hit.item.body,
          name: drinkLabel(hit.item),
        };
      }
    }
    out[occ] = slots;
  }
  return out;
}

function anyCategoryDiff(
  a: Partial<Record<DrinkCategory, TopSlot>>,
  b: Partial<Record<DrinkCategory, TopSlot>>,
): boolean {
  for (const cat of CATEGORIES) {
    const idA = a[cat]?.drinkId;
    const idB = b[cat]?.drinkId;
    if (idA && idB && idA !== idB) return true;
    if (!!idA !== !!idB) return true;
  }
  return false;
}

function main() {
  mkdirSync(OUT_DIR, { recursive: true });
  mkdirSync(dirname(REPORT_PATH), { recursive: true });

  const t0 = Date.now();
  // dedupe po id (isti ID ne broji se dvaput)
  const seen = new Set<string>();
  const cigars: Cigar[] = [];
  for (const c of CIGARS) {
    if (seen.has(c.id)) continue;
    seen.add(c.id);
    cigars.push(c);
  }

  const drinks = ALL_DRINKS.filter((d) => d.pairable);
  let morningEveningDiff = 0;
  let morningAfternoonDiff = 0;
  const reasonTally = { fit: 0, clash: 0 };

  const samplePool = [...cigars]
    .sort(
      (a, b) =>
        a.strength - b.strength ||
        a.body - b.body ||
        a.id.localeCompare(b.id),
    )
    .filter((_, i, arr) => {
      // 10 uzoraka raspoređenih po strength/body
      const step = Math.max(1, Math.floor(arr.length / 10));
      return i % step === 0;
    })
    .slice(0, 10);

  const sampleRows: {
    cigarId: string;
    label: string;
    strength: number;
    body: number;
    rum: Record<OccasionFilter, string>;
  }[] = [];

  const allTops: Record<string, CigarTops> = {};
  let done = 0;

  for (const cigar of cigars) {
    const tops = topsForCigar(cigar, reasonTally);
    allTops[cigar.id] = tops;

    if (anyCategoryDiff(tops.morning, tops.evening)) morningEveningDiff++;
    if (anyCategoryDiff(tops.morning, tops.afternoon)) morningAfternoonDiff++;

    done++;
    if (done % 200 === 0) {
      console.error(`… ${done}/${cigars.length} cigara`);
    }
  }

  const occasionFitHits = reasonTally.fit;
  const occasionClashHits = reasonTally.clash;

  for (const cigar of samplePool) {
    const tops = allTops[cigar.id];
    const rum: Record<OccasionFilter, string> = {
      any: tops.any.rum
        ? `${tops.any.rum.name} (${tops.any.rum.score})`
        : "—",
      morning: tops.morning.rum
        ? `${tops.morning.rum.name} (${tops.morning.rum.score})`
        : "—",
      afternoon: tops.afternoon.rum
        ? `${tops.afternoon.rum.name} (${tops.afternoon.rum.score})`
        : "—",
      evening: tops.evening.rum
        ? `${tops.evening.rum.name} (${tops.evening.rum.score})`
        : "—",
    };
    sampleRows.push({
      cigarId: cigar.id,
      label: cigarLabel(cigar),
      strength: cigar.strength,
      body: cigar.body,
      rum,
    });
  }

  // pool sizes
  // pool sizes (referentno za cigaru body 3 — stvarni pool ovisi o cigari)
  const poolSizes = Object.fromEntries(
    OCCASIONS.map((o) => [
      o,
      drinks.filter(occasionKeep(o, 3)).length,
    ]),
  );

  const n = cigars.length;
  const pctME = (100 * morningEveningDiff) / n;
  const pctMA = (100 * morningAfternoonDiff) / n;
  const passME = pctME >= 50;
  const passMA = pctMA >= 25;

  const summary = {
    meta: {
      cigars: n,
      drinks: drinks.length,
      poolSizes,
      elapsedMs: Date.now() - t0,
      generatedAt: new Date().toISOString(),
    },
    metrics: {
      morningVsEveningDiffPct: pctME,
      morningVsAfternoonDiffPct: pctMA,
      morningEveningDiffCount: morningEveningDiff,
      morningAfternoonDiffCount: morningAfternoonDiff,
      occasionFitProbeHits: occasionFitHits,
      occasionClashProbeHits: occasionClashHits,
      passMorningEvening50: passME,
      passMorningAfternoon25: passMA,
    },
    sample: sampleRows,
  };

  writeFileSync(
    join(OUT_DIR, "summary.json"),
    JSON.stringify(summary, null, 2),
    "utf8",
  );

  const md = `# Audit filtera doba dana (hibrid)

**Generirano:** ${summary.meta.generatedAt}  
**Trajanje:** ${summary.meta.elapsedMs} ms  
**Engine:** soft occasion nudge u \`pairDrinksForCigar\` + \`rankByOccasion\` (izbor unutar pojasa izjednacenih po kategoriji)

## 1. Opseg

| Veličina | Vrijednost |
|----------|------------|
| Cigare (dedupe) | ${n} |
| Pairable pića | ${drinks.length} |
| Pool any (ref. body 3) | ${poolSizes.any} |
| Pool jutro (ref. body 3) | ${poolSizes.morning} |
| Pool poslijepodne (ref. body 3) | ${poolSizes.afternoon} |
| Pool večer (ref. body 3) | ${poolSizes.evening} |

## 2. Metrike razlike top-prijedloga

Udio cigara gdje se **barem jedna** kategorija (rum/whisky/brandy/wine/coffee/tequila/gin) razlikuje u top-1:

| Usporedba | n | udio | Prag | Status |
|-----------|---|------|------|--------|
| jutro vs večer | ${morningEveningDiff} | ${pctME.toFixed(1)}% | ≥ 50% | ${passME ? "PASS" : "FAIL"} |
| jutro vs poslijepodne | ${morningAfternoonDiff} | ${pctMA.toFixed(1)}% | ≥ 25% | ${passMA ? "PASS" : "FAIL"} |

### Occasion reasoni na top karticama

Broj top-1 slotova (kategorija × cigara × prilika) koji nose reason:

| Reason | pogodaka |
|--------|----------|
| occasion-fit | ${occasionFitHits} |
| occasion-clash | ${occasionClashHits} |

## 3. Uzorak — top rum po prilici

| Cigara | str/body | any | jutro | poslijepodne | večer |
|--------|----------|-----|-------|--------------|-------|
${sampleRows
  .map(
    (r) =>
      `| ${r.label} | ${r.strength}/${r.body} | ${r.rum.any} | ${r.rum.morning} | ${r.rum.afternoon} | ${r.rum.evening} |`,
  )
  .join("\n")}

## 4. Kako prilika djeluje

Nista se ne rezi iz poola (\`occasionKeep\` je no-op). Dva sloja:

1. **Soft nudge** u scoreu — \`|delta| ≤ occasionFit + occasionMild < bodyPerStep\`,
   pa doba dana ne moze pretvoriti los par u dobar.
2. **Izbor unutar izjednacenih** — medju kandidatima iste kategorije koji su
   unutar \`OCCASION_BAND_MARGIN\` bodova od najboljeg presudjuje \`occasionAffinity\`
   (kategorija + stil + relativno tijelo + zestina).

JSON sažetak: \`app/scripts/output/occasion-audit/summary.json\`
`;

  writeFileSync(REPORT_PATH, md, "utf8");
  console.log(md);
  console.log(`\nWrote ${REPORT_PATH}`);
  console.log(`Wrote ${join(OUT_DIR, "summary.json")}`);
  if (!passME || !passMA) {
    process.exitCode = 1;
  }
}

main();
