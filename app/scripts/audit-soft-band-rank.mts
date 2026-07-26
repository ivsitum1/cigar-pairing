/**
 * Soft-band ranking audit: baseline vs soft-band for drink→cigar and
 * cigar→drink (comparison only). Streams one anchor at a time (avoids OOM).
 *
 * Run: npx vite-node scripts/audit-soft-band-rank.mts
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { ALL_DRINKS, CIGARS } from "../src/data/index";
import { pairCigarsForDrink, pairDrinksForCigar } from "../src/engine/pairing";
import {
  diverseBy,
  softBand,
  softBandWindow,
  SOFT_BAND_MARGIN,
} from "../src/engine/softBandRank";
import type { PairingReason, PairingResult } from "../src/types";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPORT_PATH = join(
  __dirname,
  "..",
  "..",
  "01_work",
  "output",
  "SOFT-BAND-RANK-AUDIT.md",
);
const OUT_DIR = join(__dirname, "output", "soft-band-audit");

const drinks = ALL_DRINKS.filter((d) => d.pairable);
const cigars = CIGARS;

const DAY_KEYS = [
  "2026-07-20",
  "2026-07-21",
  "2026-07-22",
  "2026-07-23",
  "2026-07-24",
  "2026-07-25",
  "2026-07-26",
];
const CYCLES = [0, 1, 2];
const SCORE_GATE_PCT = 40;

type AnchorStats = {
  anchorId: string;
  anchorLabel: string;
  maxScore: number;
  bandSize: number;
  baselineTopId: string;
  baselineTopLabel: string;
  softTopIds: string[];
  softChanges: boolean;
  meanWindowScore: number;
};

/** Drop reasons to cut peak memory after scoring. */
function slim<T>(ranked: PairingResult<T>[]): PairingResult<T>[] {
  const empty: PairingReason[] = [];
  return ranked.map((r) => ({ item: r.item, score: r.score, reasons: empty }));
}

function bandBucket(size: number): "1" | "2-5" | "6+" {
  if (size <= 1) return "1";
  if (size <= 5) return "2-5";
  return "6+";
}

function pct(n: number, d: number): string {
  if (d === 0) return "0.0";
  return ((100 * n) / d).toFixed(1);
}

function analyzeOne<T>(
  anchorId: string,
  anchorLabel: string,
  ranked: PairingResult<T>[],
  keyOf: (item: T) => string,
  labelOf: (item: T) => string,
  idOf: (item: T) => string,
): AnchorStats | null {
  if (ranked.length === 0) return null;
  const diverse = diverseBy(ranked, keyOf);
  const band = softBand(diverse, SOFT_BAND_MARGIN);
  const baseline = diverse[0] ?? ranked[0];
  const softTopIds: string[] = [];
  let windowScoreSum = 0;
  let windowScoreN = 0;

  for (const dk of DAY_KEYS) {
    for (const cycle of CYCLES) {
      const { window } = softBandWindow(ranked, {
        anchorId,
        dayKey: dk,
        cycle,
        keyOf,
      });
      if (window[0]) softTopIds.push(idOf(window[0].item));
      for (const w of window) {
        windowScoreSum += w.score;
        windowScoreN++;
      }
    }
  }

  const uniqueSoft = new Set(softTopIds);
  return {
    anchorId,
    anchorLabel,
    maxScore: ranked[0].score,
    bandSize: band.length,
    baselineTopId: idOf(baseline.item),
    baselineTopLabel: labelOf(baseline.item),
    softTopIds: [...uniqueSoft],
    softChanges: uniqueSoft.size > 1,
    meanWindowScore: windowScoreN > 0 ? windowScoreSum / windowScoreN : NaN,
  };
}

function histogram(stats: AnchorStats[]): Record<"1" | "2-5" | "6+", number> {
  const h = { "1": 0, "2-5": 0, "6+": 0 };
  for (const s of stats) h[bandBucket(s.bandSize)]++;
  return h;
}

function stickyBaseline(stats: AnchorStats[], topN: number) {
  const counts = new Map<string, { label: string; n: number }>();
  for (const s of stats) {
    const cur = counts.get(s.baselineTopId) ?? {
      label: s.baselineTopLabel,
      n: 0,
    };
    cur.n++;
    counts.set(s.baselineTopId, cur);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1].n - a[1].n)
    .slice(0, topN)
    .map(([id, v]) => ({ id, label: v.label, n: v.n }));
}

function stickySoft(stats: AnchorStats[], topN: number) {
  const sticky = stats.filter((s) => !s.softChanges);
  const counts = new Map<string, { label: string; n: number }>();
  for (const s of sticky) {
    const id = s.softTopIds[0] ?? s.baselineTopId;
    const label = id === s.baselineTopId ? s.baselineTopLabel : id;
    const cur = counts.get(id) ?? { label, n: 0 };
    cur.n++;
    counts.set(id, cur);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1].n - a[1].n)
    .slice(0, topN)
    .map(([id, v]) => ({ id, label: v.label, n: v.n }));
}

function sectionMarkdown(
  title: string,
  stats: AnchorStats[],
  itemNoun: string,
): string {
  const n = stats.length;
  const h = histogram(stats);
  const changes = stats.filter((s) => s.softChanges).length;
  const meanBand =
    n > 0 ? stats.reduce((s, x) => s + x.bandSize, 0) / n : 0;
  const meanWin =
    n > 0
      ? stats.reduce((s, x) => s + (x.meanWindowScore || 0), 0) / n
      : 0;
  const gatePct = (100 * h["1"]) / Math.max(n, 1);
  const baseSticky = stickyBaseline(stats, 20);
  const softSticky = stickySoft(stats, 20);

  return [
    `## ${title}`,
    "",
    `| Metrika | Vrijednost |`,
    `|---------|------------|`,
    `| Anchora | ${n} |`,
    `| Mean bandSize | ${meanBand.toFixed(2)} |`,
    `| bandSize == 1 | ${h["1"]} (${pct(h["1"], n)}%) |`,
    `| bandSize 2–5 | ${h["2-5"]} (${pct(h["2-5"], n)}%) |`,
    `| bandSize ≥ 6 | ${h["6+"]} (${pct(h["6+"], n)}%) |`,
    `| Soft #1 mijenja se (≥1× u 7 dana × 3 cycle) | ${changes} (${pct(changes, n)}%) |`,
    `| Mean score u soft prozoru | ${meanWin.toFixed(2)} |`,
    `| Score follow-up gate (bandSize==1 > ${SCORE_GATE_PCT}%) | ${gatePct > SCORE_GATE_PCT ? "DA — razmotriti kalibraciju" : "NE"} (${gatePct.toFixed(1)}%) |`,
    "",
    `### Top-20 sticky baseline #1 (${itemNoun})`,
    "",
    `| # | Id | Label | Anchora |`,
    `|---|----|-------|---------|`,
    ...baseSticky.map(
      (r, i) =>
        `| ${i + 1} | \`${r.id}\` | ${r.label} | ${r.n} (${pct(r.n, n)}%) |`,
    ),
    "",
    `### Top-20 sticky soft-band #1 (nikad ne rotira)`,
    "",
    ...(softSticky.length === 0
      ? [
          `*(prazno — soft #1 rotira na ${pct(changes, n)}% anchora u ovom uzorku day/cycle)*`,
          "",
        ]
      : [
          `| # | Id | Label | Anchora |`,
          `|---|----|-------|---------|`,
          ...softSticky.map(
            (r, i) =>
              `| ${i + 1} | \`${r.id}\` | ${r.label} | ${r.n} (${pct(r.n, n)}%) |`,
          ),
          "",
        ]),
  ].join("\n");
}

function main() {
  const t0 = Date.now();
  console.log(
    `Soft-band audit: ${drinks.length} drinks × ${cigars.length} cigars…`,
  );

  const d2c: AnchorStats[] = [];
  for (let i = 0; i < drinks.length; i++) {
    const d = drinks[i];
    const ranked = slim(pairCigarsForDrink(d, cigars));
    const s = analyzeOne(
      d.id,
      d.name,
      ranked,
      (c) => c.brand,
      (c) => `${c.brand} ${c.line}`,
      (c) => c.id,
    );
    if (s) d2c.push(s);
    if ((i + 1) % 100 === 0 || i + 1 === drinks.length) {
      console.log(`drink→cigar ${i + 1}/${drinks.length} (${Date.now() - t0} ms)`);
    }
  }

  const c2d: AnchorStats[] = [];
  for (let i = 0; i < cigars.length; i++) {
    const c = cigars[i];
    const ranked = slim(pairDrinksForCigar(c, drinks));
    const s = analyzeOne(
      c.id,
      `${c.brand} ${c.line}`,
      ranked,
      (d) => d.category,
      (d) => d.name,
      (d) => d.id,
    );
    if (s) c2d.push(s);
    if ((i + 1) % 200 === 0 || i + 1 === cigars.length) {
      console.log(`cigar→drink ${i + 1}/${cigars.length} (${Date.now() - t0} ms)`);
    }
  }

  const d2cGate =
    (100 * histogram(d2c)["1"]) / Math.max(d2c.length, 1) > SCORE_GATE_PCT;
  const c2dRotate = pct(
    c2d.filter((s) => s.softChanges).length,
    c2d.length,
  );
  const d2cRotate = pct(
    d2c.filter((s) => s.softChanges).length,
    d2c.length,
  );

  const d2cMeanBand =
    d2c.reduce((s, x) => s + x.bandSize, 0) / Math.max(d2c.length, 1);
  const c2dMeanBand =
    c2d.reduce((s, x) => s + x.bandSize, 0) / Math.max(c2d.length, 1);

  const report = [
    `# Soft-band ranking audit`,
    "",
    `**Generirano:** ${new Date().toISOString()}`,
    `**Margin:** max − ${SOFT_BAND_MARGIN}`,
    `**Day keys:** ${DAY_KEYS.length}; **cycles:** ${CYCLES.join(", ")}`,
    `**Trajanje:** ${Date.now() - t0} ms`,
    "",
    `## Opseg`,
    "",
    `| | |`,
    `|--|--|`,
    `| Pairable pića | ${drinks.length} |`,
    `| Cigare | ${cigars.length} |`,
    "",
    `## Usporedba smjerova`,
    "",
    `| Smjer | % anchora gdje soft #1 rotira | Mean bandSize | bandSize==1 % |`,
    `|-------|-------------------------------|---------------|---------------|`,
    `| drink → cigara (ship) | ${d2cRotate}% | ${d2cMeanBand.toFixed(2)} | ${pct(histogram(d2c)["1"], d2c.length)}% |`,
    `| cigar → piće (samo usporedba) | ${c2dRotate}% | ${c2dMeanBand.toFixed(2)} | ${pct(histogram(c2d)["1"], c2d.length)}% |`,
    "",
    d2cMeanBand >= c2dMeanBand
      ? `Soft-band rotacija: drink→cigara ${d2cRotate}%, cigar→piće ${c2dRotate}%. Drink→cigara ima **širi** pojas (mean ${d2cMeanBand.toFixed(2)} vs ${c2dMeanBand.toFixed(2)}) — mehanizam je primjereniji za shipani smjer; cigar→piće UI ostaje stari.`
      : `Soft-band rotacija: drink→cigara ${d2cRotate}%, cigar→piće ${c2dRotate}%. UI cigar→piće ostaje stari mehanizam.`,
    "",
    `Napomena: kad je \`bandSize < 3\`, UI pada na brand-diverse listu; day seed i cycle tada rotiraju taj širi pool.`,
    "",
    d2cGate
      ? `**Score gate:** drink→cigara ima bandSize==1 iznad ${SCORE_GATE_PCT}% — razmotriti laganu kalibraciju formule.`
      : `**Score gate:** drink→cigara bandSize==1 ispod ${SCORE_GATE_PCT}% — formula ostaje netaknuta.`,
    "",
    sectionMarkdown("Drink → cigara (proizvod)", d2c, "cigara"),
    sectionMarkdown(
      "Cigar → piće (usporedba; diversity key = category)",
      c2d,
      "piće",
    ),
  ].join("\n");

  mkdirSync(dirname(REPORT_PATH), { recursive: true });
  writeFileSync(REPORT_PATH, report, "utf8");

  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(
    join(OUT_DIR, "summary.json"),
    JSON.stringify(
      {
        drinks: drinks.length,
        cigars: cigars.length,
        drinkToCigar: {
          n: d2c.length,
          histogram: histogram(d2c),
          rotatePct: Number(d2cRotate),
          scoreGate: d2cGate,
        },
        cigarToDrink: {
          n: c2d.length,
          histogram: histogram(c2d),
          rotatePct: Number(c2dRotate),
        },
        elapsedMs: Date.now() - t0,
      },
      null,
      2,
    ),
    "utf8",
  );

  console.log(`Wrote ${REPORT_PATH}`);
  console.log(`Score gate (drink→cigar): ${d2cGate ? "FIRE" : "ok"}`);
}

main();
