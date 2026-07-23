/**
 * Exhaustive pairing-score audit: all CIGARS × pairable ALL_DRINKS.
 * Writes JSON/CSV under scripts/output/pairing-audit/ and a HR report to
 * ../01_work/output/PAIRING-SCORE-AUDIT.md
 *
 * Run: npx vite-node scripts/audit-pairing-distribution.mts
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { ALL_DRINKS, CIGARS } from "../src/data/index";
import { scorePairing } from "../src/engine/pairing";
import { WEIGHTS } from "../src/engine/rules";
import type { Cigar, Drink, PairingReason } from "../src/types";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(__dirname, "output", "pairing-audit");
const REPORT_PATH = join(__dirname, "..", "..", "01_work", "output", "PAIRING-SCORE-AUDIT.md");

const drinks = ALL_DRINKS.filter((d) => d.pairable);

type PairHit = {
  cigarId: string;
  drinkId: string;
  cigarLabel: string;
  drinkLabel: string;
  score: number;
  rules: string[];
};

function qualityNudge(drink: Drink): number {
  if (drink.qualityScore == null) return 0;
  return (drink.qualityScore - 7) * WEIGHTS.qualityNudge;
}

/** Reconstruct raw score before round/clamp from engine side-effects we can see. */
function reconstructRaw(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
): { rawFromParts: number; unexplainedBodyDiff1: number } {
  const bodyDiff = Math.abs(cigar.body - drink.body);
  // bodyDiff===1 applies penalty with no reason entry
  const silentBody =
    bodyDiff === 1 ? bodyDiff * WEIGHTS.bodyPerStep : 0;
  const reasonSum = reasons.reduce((s, r) => s + r.score, 0);
  const rawFromParts =
    WEIGHTS.base + reasonSum + qualityNudge(drink) - silentBody;
  return { rawFromParts, unexplainedBodyDiff1: silentBody };
}

function erf(x: number): number {
  // Abramowitz & Stegun 7.1.26
  const sign = x < 0 ? -1 : 1;
  const ax = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * ax);
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const y =
    1 -
    ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * Math.exp(-ax * ax);
  return sign * y;
}

function normalCdf(x: number, mu: number, sigma: number): number {
  if (sigma <= 0) return x < mu ? 0 : 1;
  return 0.5 * (1 + erf((x - mu) / (sigma * Math.SQRT2)));
}

function percentile(sorted: number[], p: number): number {
  if (sorted.length === 0) return NaN;
  const idx = (p / 100) * (sorted.length - 1);
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sorted[lo];
  const w = idx - lo;
  return sorted[lo] * (1 - w) + sorted[hi] * w;
}

function main() {
  mkdirSync(OUT_DIR, { recursive: true });
  mkdirSync(dirname(REPORT_PATH), { recursive: true });

  const t0 = Date.now();
  const nPairs = CIGARS.length * drinks.length;
  const hist = new Array<number>(101).fill(0);
  const ruleHits: Record<string, number> = {};
  const byCategory: Record<string, { n: number; sum: number }> = {};
  const byBodyDiff: Record<string, { n: number; sum: number }> = {};

  let sum = 0;
  let minScore = 101;
  let maxScore = -1;
  let nAt0 = 0;
  let nAt100 = 0;
  let nGe80 = 0;
  let nLe45 = 0;
  let invariantFail = 0;
  let nonInteger = 0;
  let additivityMismatch = 0;
  let tagCapViolation = 0;
  let rawMin = Infinity;
  let rawMax = -Infinity;
  let clampedLow = 0;
  let clampedHigh = 0;

  const top: PairHit[] = [];
  const bottom: PairHit[] = [];
  const TOP_K = 50;

  const insertTop = (hit: PairHit) => {
    top.push(hit);
    top.sort((a, b) => b.score - a.score || a.cigarId.localeCompare(b.cigarId));
    if (top.length > TOP_K) top.length = TOP_K;
  };
  const insertBottom = (hit: PairHit) => {
    bottom.push(hit);
    bottom.sort((a, b) => a.score - b.score || a.cigarId.localeCompare(b.cigarId));
    if (bottom.length > TOP_K) bottom.length = TOP_K;
  };

  // Theoretical bounds (no personal prefs)
  const theoMaxUnclamped =
    WEIGHTS.base +
    WEIGHTS.bodyBonus +
    3 * WEIGHTS.tagOverlap +
    3 * WEIGHTS.tagComplement +
    WEIGHTS.contrastSweetMaduro +
    WEIGHTS.wrapperMatch +
    WEIGHTS.strengthPowerMatch +
    (10 - 7) * WEIGHTS.qualityNudge; // qualityScore max assumed 10
  const theoMinUnclamped =
    WEIGHTS.base -
    4 * WEIGHTS.bodyPerStep -
    WEIGHTS.overwhelmPenalty -
    WEIGHTS.strengthPowerMismatch +
    (1 - 7) * WEIGHTS.qualityNudge; // qualityScore min assumed 1

  let i = 0;
  for (const cigar of CIGARS) {
    for (const drink of drinks) {
      const { score, reasons } = scorePairing(cigar, drink);
      const { rawFromParts, unexplainedBodyDiff1 } = reconstructRaw(
        cigar,
        drink,
        reasons,
      );
      // Actual raw before round/clamp: base + visible + quality - silent body
      // (same as rawFromParts). Empirically track round+clamp effects.
      const rounded = Math.round(rawFromParts);
      if (rounded < 0) clampedLow += 1;
      if (rounded > 100) clampedHigh += 1;
      rawMin = Math.min(rawMin, rawFromParts);
      rawMax = Math.max(rawMax, rawFromParts);

      if (score < 0 || score > 100) invariantFail += 1;
      if (!Number.isInteger(score)) nonInteger += 1;

      const expectedClamped = Math.max(0, Math.min(100, rounded));
      if (expectedClamped !== score) additivityMismatch += 1;

      for (const r of reasons) {
        if (r.rule === "flavor-shared" && r.score > 3 * WEIGHTS.tagOverlap) {
          tagCapViolation += 1;
        }
        if (r.rule === "flavor-complement" && r.score > 3 * WEIGHTS.tagComplement) {
          tagCapViolation += 1;
        }
        ruleHits[r.rule] = (ruleHits[r.rule] ?? 0) + 1;
      }
      // silence tracking for report
      void unexplainedBodyDiff1;

      hist[score] += 1;
      sum += score;

      if (score < minScore) minScore = score;
      if (score > maxScore) maxScore = score;
      if (score === 0) nAt0 += 1;
      if (score === 100) nAt100 += 1;
      if (score >= 80) nGe80 += 1;
      if (score <= 45) nLe45 += 1;

      const cat = drink.category;
      const bc = (byCategory[cat] ??= { n: 0, sum: 0 });
      bc.n += 1;
      bc.sum += score;

      const bd = String(Math.abs(cigar.body - drink.body));
      const bb = (byBodyDiff[bd] ??= { n: 0, sum: 0 });
      bb.n += 1;
      bb.sum += score;

      const hit: PairHit = {
        cigarId: cigar.id,
        drinkId: drink.id,
        cigarLabel: `${cigar.brand} ${cigar.line}`,
        drinkLabel: drink.name,
        score,
        rules: reasons.map((r) => r.rule),
      };
      if (top.length < TOP_K || score >= top[top.length - 1].score) insertTop(hit);
      if (bottom.length < TOP_K || score <= bottom[bottom.length - 1].score) {
        insertBottom(hit);
      }

      i += 1;
    }
  }

  const n = nPairs;
  const mean = sum / n;
  // Second pass for accurate central moments via histogram (memory-cheap)
  let m2 = 0;
  let m3 = 0;
  let m4 = 0;
  for (let s = 0; s <= 100; s++) {
    const c = hist[s];
    if (!c) continue;
    const d = s - mean;
    m2 += c * d * d;
    m3 += c * d * d * d;
    m4 += c * d * d * d * d;
  }
  const variance = m2 / n;
  const sd = Math.sqrt(variance);
  const skewness = sd > 0 ? m3 / n / (sd * sd * sd) : 0;
  const excessKurtosis = sd > 0 ? m4 / n / (variance * variance) - 3 : 0;

  // Expand sorted scores from histogram for percentiles / mode
  const sorted: number[] = [];
  let mode = 0;
  let modeCount = 0;
  for (let s = 0; s <= 100; s++) {
    if (hist[s] > modeCount) {
      mode = s;
      modeCount = hist[s];
    }
    for (let k = 0; k < hist[s]; k++) sorted.push(s);
  }

  const p5 = percentile(sorted, 5);
  const p25 = percentile(sorted, 25);
  const p50 = percentile(sorted, 50);
  const p75 = percentile(sorted, 75);
  const p95 = percentile(sorted, 95);
  const iqr = p75 - p25;

  // Jarque–Bera
  const jb =
    (n / 6) * (skewness * skewness + (excessKurtosis * excessKurtosis) / 4);
  // χ² df=2 critical ~ 5.991 (α=0.05), ~9.210 (α=0.01)
  const jbReject005 = jb > 5.991;
  const jbReject001 = jb > 9.21;

  // χ² goodness-of-fit vs N(mean, sd²) on bins of width 5 (merge thin tails)
  const binWidth = 5;
  type Bin = { lo: number; hi: number; obs: number; exp: number };
  const rawBins: Bin[] = [];
  for (let lo = 0; lo < 100; lo += binWidth) {
    const hi = lo + binWidth - 1;
    let obs = 0;
    for (let s = lo; s <= hi; s++) obs += hist[s];
    // continuity: P(lo-0.5 < X < hi+0.5) for discrete scores
    const exp =
      n *
      (normalCdf(hi + 0.5, mean, sd) - normalCdf(lo - 0.5, mean, sd));
    rawBins.push({ lo, hi, obs, exp });
  }
  // last point 100 alone merged into last bin
  rawBins[rawBins.length - 1].obs += hist[100];
  rawBins[rawBins.length - 1].hi = 100;
  rawBins[rawBins.length - 1].exp =
    n * (normalCdf(100.5, mean, sd) - normalCdf(rawBins[rawBins.length - 1].lo - 0.5, mean, sd));

  // Merge bins with expected < 5
  const bins: Bin[] = [];
  let acc: Bin | null = null;
  for (const b of rawBins) {
    if (!acc) {
      acc = { ...b };
      continue;
    }
    if (acc.exp < 5 || b.exp < 5) {
      acc.hi = b.hi;
      acc.obs += b.obs;
      acc.exp += b.exp;
    } else {
      bins.push(acc);
      acc = { ...b };
    }
  }
  if (acc) {
    if (bins.length && acc.exp < 5) {
      const last = bins[bins.length - 1];
      last.hi = acc.hi;
      last.obs += acc.obs;
      last.exp += acc.exp;
    } else {
      bins.push(acc);
    }
  }

  let chi2 = 0;
  for (const b of bins) {
    if (b.exp > 0) chi2 += ((b.obs - b.exp) ** 2) / b.exp;
  }
  const chi2Df = Math.max(bins.length - 1 - 2, 1); // estimate μ,σ
  // Rough p-value via Wilson–Hilferty approximation for χ²
  const chi2P = chi2SurvivalApprox(chi2, chi2Df);

  // Local maxima for multimodality (smooth with window 3)
  const smooth = hist.map((_, s) => {
    const a = hist[Math.max(0, s - 1)] ?? 0;
    const b = hist[s];
    const c = hist[Math.min(100, s + 1)] ?? 0;
    return (a + b + c) / 3;
  });
  const localMaxima: number[] = [];
  for (let s = 1; s < 100; s++) {
    if (smooth[s] > smooth[s - 1] && smooth[s] >= smooth[s + 1] && hist[s] > n * 0.005) {
      localMaxima.push(s);
    }
  }

  // Body monotonicity spot-check: same cigar, drinks differing only by body
  // (use synthetic clone of first drink with varied body, same tags)
  let bodyMonoViolations = 0;
  let bodyMonoChecks = 0;
  const sampleCigars = CIGARS.filter((_, idx) => idx % 40 === 0);
  for (const cigar of sampleCigars) {
    const proto = drinks[0];
    const scoresByBody: number[] = [];
    for (let body = 1; body <= 5; body++) {
      const synthetic: Drink = { ...proto, body, id: `synth-body-${body}` };
      scoresByBody.push(scorePairing(cigar, synthetic).score);
    }
    // As |Δbody| increases from cigar.body, score should not increase
    const ideal = cigar.body;
    for (let b1 = 1; b1 <= 5; b1++) {
      for (let b2 = 1; b2 <= 5; b2++) {
        const d1 = Math.abs(b1 - ideal);
        const d2 = Math.abs(b2 - ideal);
        if (d2 > d1) {
          bodyMonoChecks += 1;
          if (scoresByBody[b2 - 1] > scoresByBody[b1 - 1]) bodyMonoViolations += 1;
        }
      }
    }
  }

  const elapsedMs = Date.now() - t0;

  const summary = {
    meta: {
      cigars: CIGARS.length,
      drinks: drinks.length,
      pairs: n,
      elapsedMs,
      prefs: false,
      generatedAt: new Date().toISOString(),
    },
    moments: {
      mean,
      variance,
      sd,
      skewness,
      excessKurtosis,
      min: minScore,
      max: maxScore,
      mode,
      modeCount,
      p5,
      p25,
      median: p50,
      p75,
      p95,
      iqr,
    },
    edges: {
      nAt0,
      nAt100,
      share0: nAt0 / n,
      share100: nAt100 / n,
      nGe80,
      shareGe80: nGe80 / n,
      nLe45,
      shareLe45: nLe45 / n,
    },
    gauss: {
      fitMu: mean,
      fitSigma: sd,
      jarqueBera: jb,
      jbRejectAlpha005: jbReject005,
      jbRejectAlpha001: jbReject001,
      chi2,
      chi2Df,
      chi2PApprox: chi2P,
      chi2Bins: bins.length,
      localMaxima,
      unimodalHint: localMaxima.length <= 1,
    },
    theory: {
      weights: WEIGHTS,
      theoMinUnclamped,
      theoMaxUnclamped,
      empiricRawMin: rawMin,
      empiricRawMax: rawMax,
      clampedLow,
      clampedHigh,
      shareClampedLow: clampedLow / n,
      shareClampedHigh: clampedHigh / n,
    },
    logic: {
      invariantFail,
      nonInteger,
      additivityMismatch,
      tagCapViolation,
      bodyMonoChecks,
      bodyMonoViolations,
      notes: [
        "qualityNudge ulazi u score ali nema PairingReason",
        "bodyDiff===1 kaznjava score bez PairingReason (samo >=2 dobiva reason)",
        "score = clamp(round(raw), 0, 100)",
      ],
    },
    byCategory: Object.fromEntries(
      Object.entries(byCategory).map(([k, v]) => [
        k,
        { n: v.n, mean: v.sum / v.n },
      ]),
    ),
    byBodyDiff: Object.fromEntries(
      Object.entries(byBodyDiff)
        .sort(([a], [b]) => Number(a) - Number(b))
        .map(([k, v]) => [k, { n: v.n, mean: v.sum / v.n }]),
    ),
    ruleHits,
    ruleHitShare: Object.fromEntries(
      Object.entries(ruleHits).map(([k, v]) => [k, v / n]),
    ),
  };

  writeFileSync(join(OUT_DIR, "summary.json"), JSON.stringify(summary, null, 2));
  writeFileSync(
    join(OUT_DIR, "histogram.csv"),
    ["score,count,share", ...hist.map((c, s) => `${s},${c},${(c / n).toFixed(8)}`)].join(
      "\n",
    ),
  );
  writeFileSync(join(OUT_DIR, "top50.json"), JSON.stringify(top, null, 2));
  writeFileSync(join(OUT_DIR, "bottom50.json"), JSON.stringify(bottom, null, 2));
  writeFileSync(join(OUT_DIR, "chi2-bins.json"), JSON.stringify(bins, null, 2));

  const report = renderReport(summary, hist, top, bottom, bins, n);
  writeFileSync(REPORT_PATH, report, "utf8");

  console.log(
    JSON.stringify(
      {
        ok: true,
        pairs: n,
        mean: +mean.toFixed(3),
        median: p50,
        sd: +sd.toFixed(3),
        jb,
        chi2: +chi2.toFixed(1),
        elapsedMs,
        report: REPORT_PATH,
      },
      null,
      2,
    ),
  );
}

function chi2SurvivalApprox(x: number, k: number): number {
  // Wilson–Hilferty → standard normal, then erfc tail
  if (k <= 0) return NaN;
  const h = 2 / (9 * k);
  const z = ((x / k) ** (1 / 3) - (1 - h)) / Math.sqrt(h);
  // P(Z > z)
  return 0.5 * erfc(z / Math.SQRT2);
}

function erfc(x: number): number {
  return 1 - erf(x);
}

function fmt(n: number, d = 3): string {
  if (!Number.isFinite(n)) return "n/a";
  return n.toFixed(d);
}

function pct(n: number): string {
  return `${(100 * n).toFixed(2)}%`;
}

function renderReport(
  summary: ReturnType<typeof Object> & Record<string, unknown>,
  hist: number[],
  top: PairHit[],
  bottom: PairHit[],
  bins: { lo: number; hi: number; obs: number; exp: number }[],
  n: number,
): string {
  const s = summary as {
    meta: { cigars: number; drinks: number; pairs: number; elapsedMs: number; generatedAt: string };
    moments: Record<string, number>;
    edges: Record<string, number>;
    gauss: Record<string, unknown>;
    theory: Record<string, number | Record<string, number>>;
    logic: Record<string, unknown>;
    byCategory: Record<string, { n: number; mean: number }>;
    byBodyDiff: Record<string, { n: number; mean: number }>;
    ruleHits: Record<string, number>;
    ruleHitShare: Record<string, number>;
  };

  const histLines = hist
    .map((c, score) => {
      if (c === 0) return null;
      const bar = "█".repeat(Math.round((c / n) * 200));
      return `| ${score} | ${c} | ${pct(c / n)} | ${bar} |`;
    })
    .filter(Boolean)
    .join("\n");

  // collapse histogram display: only every score with count, but for readability
  // also provide 5-wide summary
  const coarse: string[] = [];
  for (let lo = 0; lo <= 100; lo += 5) {
    const hi = Math.min(100, lo + 4);
    let c = 0;
    for (let x = lo; x <= hi; x++) c += hist[x] ?? 0;
    coarse.push(`| ${lo}–${hi} | ${c} | ${pct(c / n)} |`);
  }

  const catRows = Object.entries(s.byCategory)
    .sort((a, b) => b[1].mean - a[1].mean)
    .map(([k, v]) => `| ${k} | ${v.n} | ${fmt(v.mean, 2)} |`)
    .join("\n");

  const bodyRows = Object.entries(s.byBodyDiff)
    .map(([k, v]) => `| ${k} | ${v.n} | ${fmt(v.mean, 2)} |`)
    .join("\n");

  const ruleRows = Object.entries(s.ruleHits)
    .sort((a, b) => b[1] - a[1])
    .map(([k, v]) => `| ${k} | ${v} | ${pct(s.ruleHitShare[k])} |`)
    .join("\n");

  const topRows = top
    .slice(0, 20)
    .map(
      (h, i) =>
        `| ${i + 1} | ${h.score} | ${h.cigarLabel} (\`${h.cigarId}\`) | ${h.drinkLabel} (\`${h.drinkId}\`) | ${h.rules.join(", ")} |`,
    )
    .join("\n");

  const botRows = bottom
    .slice(0, 20)
    .map(
      (h, i) =>
        `| ${i + 1} | ${h.score} | ${h.cigarLabel} (\`${h.cigarId}\`) | ${h.drinkLabel} (\`${h.drinkId}\`) | ${h.rules.join(", ")} |`,
    )
    .join("\n");

  const chiRows = bins
    .map(
      (b) =>
        `| ${b.lo}–${b.hi} | ${b.obs} | ${fmt(b.exp, 1)} | ${fmt(b.obs - b.exp, 1)} |`,
    )
    .join("\n");

  const m = s.moments;
  const e = s.edges;
  const g = s.gauss;
  const t = s.theory;
  const L = s.logic;

  const nSci = n >= 1e6 ? `${(n / 1e6).toFixed(1)}×10⁶` : `${(n / 1e5).toFixed(1)}×10⁵`;
  const gaussVerdict = g.jbRejectAlpha005
    ? `Formalni Jarque–Bera **odbacuje** normalnost (α=0.05). To je očekivano pri n≈${nSci} zbog diskretnih scoreova, clampa, multimodalnosti (body-diff mješavina) i rule-mješavine.`
    : "Jarque–Bera ne odbacuje normalnost na α=0.05.";

  const shapeNote =
    (g.localMaxima as number[]).length > 1
      ? `Detektirano ${(g.localMaxima as number[]).length} lokalnih maksimuma (nakon glatke): ${(g.localMaxima as number[]).join(", ")} → distribucija nije strogo unimodalna.`
      : "Nakon blagog glađenja histogram je približno unimodalan.";

  return `# Audit ocjena sparivanja (cigara × piće)

**Generirano:** ${s.meta.generatedAt}  
**Engine:** \`scorePairing\` bez osobnih preferencija (\`prefs\` isključeno)  
**Trajanje:** ${s.meta.elapsedMs} ms

## 1. Opseg

| Veličina | Vrijednost |
|----------|------------|
| Cigare (dedupe) | ${s.meta.cigars} |
| Pairable pića | ${s.meta.drinks} |
| Parova (N) | **${s.meta.pairs}** |

## 2. Deskriptivna statistika scorea (0–100)

| Stat | Vrijednost |
|------|------------|
| Mean (μ) | ${fmt(m.mean, 4)} |
| Median | ${fmt(m.median, 2)} |
| Mode | ${m.mode} (n=${m.modeCount}) |
| SD (σ) | ${fmt(m.sd, 4)} |
| Variance | ${fmt(m.variance, 4)} |
| Skewness | ${fmt(m.skewness, 4)} |
| Excess kurtosis | ${fmt(m.excessKurtosis, 4)} |
| Min | ${m.min} |
| Max | ${m.max} |
| P5 | ${fmt(m.p5, 2)} |
| P25 | ${fmt(m.p25, 2)} |
| P75 | ${fmt(m.p75, 2)} |
| P95 | ${fmt(m.p95, 2)} |
| IQR | ${fmt(m.iqr, 2)} |

### Rubovi i pragovi kuriranih poruka

| Event | n | udio |
|-------|---|------|
| score = 0 | ${e.nAt0} | ${pct(e.share0)} |
| score = 100 | ${e.nAt100} | ${pct(e.share100)} |
| score ≥ 80 (pohvala) | ${e.nGe80} | ${pct(e.shareGe80)} |
| score ≤ 45 (upozorenje) | ${e.nLe45} | ${pct(e.shareLe45)} |

## 3. Gaussova pretpostavka

Fit: **N(μ=${fmt(m.mean, 4)}, σ²=${fmt(m.variance, 4)})** s empirijskim momentima.

| Test | Rezultat |
|------|----------|
| Jarque–Bera | ${fmt(g.jarqueBera as number, 2)} |
| JB reject α=0.05 (krit. 5.991) | ${g.jbRejectAlpha005 ? "DA" : "NE"} |
| JB reject α=0.01 (krit. 9.210) | ${g.jbRejectAlpha001 ? "DA" : "NE"} |
| χ² vs N(μ,σ) (binovi širine 5, spojeni E<5) | ${fmt(g.chi2 as number, 2)} (df≈${g.chi2Df}) |
| Približni p (Wilson–Hilferty) | ${fmt(g.chi2PApprox as number, 4)} |

**Interpretacija:** ${gaussVerdict}

${shapeNote}

Za rule-based aditivni score **nije** razumno očekivati strogi Gaus: baza 36, kazne u koracima od 12, capovi tagova i \`clamp\` stvaraju diskretnu mješavinu. „Bell-like“ oblik (unimodalnost, umjerena širina) može se pojaviti, ali formalni normalitet pri ovom N gotovo uvijek pada.

### χ² binovi (opaženo vs očekivano pod N)

| Raspon | Obs | Exp | Obs−Exp |
|--------|-----|-----|---------|
${chiRows}

### Histogram (grubo, korak 5)

| Raspon | n | udio |
|--------|---|------|
${coarse.join("\n")}

<details><summary>Puni histogram po scoreu (0–100)</summary>

| Score | n | udio | bar |
|-------|---|------|-----|
${histLines}

</details>

## 4. Matematika i logika mehanizma

### Teoretski vs empirijski raspon (raw prije clamp)

| | Vrijednost |
|--|------------|
| Teoretski min (neclamp, pretpostavke) | ${fmt(t.theoMinUnclamped as number, 1)} |
| Teoretski max (neclamp, pretpostavke) | ${fmt(t.theoMaxUnclamped as number, 1)} |
| Empirijski raw min | ${fmt(t.empiricRawMin as number, 1)} |
| Empirijski raw max | ${fmt(t.empiricRawMax as number, 1)} |
| Parova s round(raw) < 0 (clamp dolje) | ${t.clampedLow} (${pct(t.shareClampedLow as number)}) |
| Parova s round(raw) > 100 (clamp gore) | ${t.clampedHigh} (${pct(t.shareClampedHigh as number)}) |

Težišta (\`WEIGHTS\`): base=${WEIGHTS.base}, bodyBonus=${WEIGHTS.bodyBonus}, bodyPerStep=${WEIGHTS.bodyPerStep}, overwhelm=${WEIGHTS.overwhelmPenalty}, tagOverlap=${WEIGHTS.tagOverlap}, tagComplement=${WEIGHTS.tagComplement}, contrastSweetMaduro=${WEIGHTS.contrastSweetMaduro}, wrapperMatch=${WEIGHTS.wrapperMatch}, powerMatch=${WEIGHTS.strengthPowerMatch}, powerMismatch=${WEIGHTS.strengthPowerMismatch}, qualityNudge=${WEIGHTS.qualityNudge}.

### Invarijante (puna populacija)

| Provjera | Rezultat |
|----------|----------|
| Score izvan [0,100] | ${L.invariantFail} |
| Ne-cjelobrojni score | ${L.nonInteger} |
| Neslaganje reconstruktcije (base+reasons+quality−silentBodyDiff1 → clamp∘round) | ${L.additivityMismatch} |
| Cap shared/complement > 3×težina | ${L.tagCapViolation} |
| Body-monotonija (sintetički body 1–5, uzorak cigara) | ${L.bodyMonoViolations} kršenja / ${L.bodyMonoChecks} usporedbi |

### Dokumentirane asimetrije (nisu nužno bugovi)

1. **\`qualityNudge\`** ulazi u broj, ali **nema** \`PairingReason\` — UI zbroj razloga ≠ score.
2. **\`bodyDiff === 1\`**: kazna −12 bez reason; reason tek za \`bodyDiff >= 2\`.
3. **\`clamp(round(raw), 0, 100)\`**: saturacija na 0/100 skraćuje repove (anti-Gauss).
4. **Wrapper affinity**: samo prvi matching profil (\`break\`).
5. **Complement** zahtijeva \`dt !== ct\`, pa self-unosi u \`COMPLEMENTS\` ne double-countaju isti tag s \`flavor-shared\`.

## 5. Breakdown

### Mean score po kategoriji pića

| Kategorija | n parova | mean |
|------------|----------|------|
${catRows}

### Mean score po |Δbody|

| \\|Δbody\\| | n | mean |
|---------|---|------|
${bodyRows}

### Frekvencija pravila (udio parova u kojima se rule pojavio)

| Rule | n | udio parova |
|------|---|-------------|
${ruleRows}

## 6. Ekstremi (top / bottom 20)

### Najbolji spojevi

| # | Score | Cigara | Piće | Rules |
|---|-------|--------|------|-------|
${topRows}

### Najslabiji spojevi

| # | Score | Cigara | Piće | Rules |
|---|-------|--------|------|-------|
${botRows}

## 7. Zaključak

- Engine je **deterministički aditivni rule-sustav** s diskretnim koracima i clampom, ne probabilistički generator iz normale.
- Empirijska distribucija na punom katalogu: μ≈${fmt(m.mean, 1)}, σ≈${fmt(m.sd, 1)}, median≈${fmt(m.median, 0)}.
- Stroga Gaussova hipoteza: **${g.jbRejectAlpha005 ? "odbijena" : "nije odbijena"}** (JB); χ² p≈${fmt(g.chi2PApprox as number, 4)}.
- Logičke invarijante ([0,100], integer, tag capovi) ${
    Number(L.invariantFail) + Number(L.nonInteger) + Number(L.tagCapViolation) + Number(L.additivityMismatch) === 0
      ? "**prolaze** na punoj populaciji"
      : "**imaju odstupanja** — vidi tablicu u §4"
  }.

### Artefakti

- \`app/scripts/output/pairing-audit/summary.json\`
- \`app/scripts/output/pairing-audit/histogram.csv\`
- \`app/scripts/output/pairing-audit/top50.json\`
- \`app/scripts/output/pairing-audit/bottom50.json\`
- \`app/scripts/output/pairing-audit/chi2-bins.json\`
`;
}

main();
