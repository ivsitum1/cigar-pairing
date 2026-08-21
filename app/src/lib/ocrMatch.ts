// Fuzzy matching OCR teksta na katalog. Dvofazno: prvo brend, pa linija
// unutar brenda; tolerira tipicne OCR zamjene znakova (0/O, q/g...).

export interface OcrCandidate {
  id: string;
  label: string;
  brand?: string; // omogucuje dvofazni matching (prvo brend, pa linija)
}

const GENERIC_VITOLA_TOKENS = new Set([
  "churchill",
  "robusto",
  "rothschild",
  "corona",
  "gordo",
  "gigante",
  "toro",
  "torpedo",
  "lancero",
  "belicoso",
  "perfecto",
  "figurado",
  "panatela",
  "lonsdale",
  "salomon",
]);

const normalize = (s: string) =>
  s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();

export const tokenize = (s: string) =>
  normalize(s)
    .split(/[^a-z0-9]+/)
    // keep single-letter series marks (Serie V / O / G) from shop receipts
    .filter((t) => t.length >= 3 || /^[a-z]$/.test(t));

export const STOP = new Set(["rum", "ron", "rhum", "whisky", "whiskey", "cigar", "cigars",
  "anos", "years", "old", "aged", "vol", "70cl", "700ml", "product", "the",
  // HR POS noise (avoids "TOTAL" → brand Total Flame)
  "total", "ukupno", "platiti", "pdv", "eur", "kom", "visa", "kartice", "kartica"]);

/** Levenshteinova udaljenost s ranim izlazom kad prijedje max. */
function levenshtein(a: string, b: string, max: number): number {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    let rowMin = i;
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
      rowMin = Math.min(rowMin, cur[j]);
    }
    if (rowMin > max) return max + 1;
    prev = cur;
  }
  return prev[b.length];
}

// kratki tokeni samo egzaktno; do 6 znakova 1 greska, dulji 2
const fuzzyEquals = (a: string, b: string): boolean => {
  if (a === b) return true;
  if (a.length < 4 || b.length < 4) return false;
  const max = Math.min(a.length, b.length) <= 6 ? 1 : 2;
  return levenshtein(a, b, max) <= max;
};

// egzaktan pogodak 2/1 boda (kao dosad), fuzzy pola vrijednosti
function scoreTokens(candTokens: string[], textTokens: string[]): number {
  const textSet = new Set(textTokens);
  const uniqueCand = [...new Set(candTokens)];
  let score = 0;
  for (const t of uniqueCand) {
    if (textSet.has(t)) {
      score += t.length >= 5 ? 2 : 1;
    } else if (textTokens.some((x) => fuzzyEquals(t, x))) {
      score += t.length >= 5 ? 1 : 0.5;
    }
  }
  return score;
}

const YEARISH = /^(?:\d+(?:st|nd|rd|th)|\d{2,4})$/;

/** "20th" in text must not promote a "10th Anniversary …" line via shared words. */
function anniversaryConflict(candTokens: string[], textTokens: string[]): boolean {
  const cY = candTokens.filter((t) => YEARISH.test(t));
  const tY = textTokens.filter((t) => YEARISH.test(t));
  if (cY.length === 0 || tY.length === 0) return false;
  return !cY.some((y) => tY.includes(y));
}

function countMatchedTokens(candTokens: string[], textTokens: string[]): number {
  const uniqCand = [...new Set(candTokens)];
  return uniqCand.filter(
    (t) => textTokens.includes(t) || textTokens.some((x) => fuzzyEquals(t, x)),
  ).length;
}

function hasMeaningfulNonVitolaHit(candTokens: string[], textTokens: string[]): boolean {
  return candTokens
    .filter((t) => !GENERIC_VITOLA_TOKENS.has(t))
    .some((t) => textTokens.includes(t) || textTokens.some((x) => fuzzyEquals(t, x)));
}

/** Nadji kandidata s najboljim (fuzzy) poklapanjem; prvo suzi po brendu. */
export function matchOcrText(
  text: string,
  candidates: OcrCandidate[],
): { candidate: OcrCandidate; score: number } | null {
  const textTokens = tokenize(text).filter((t) => !STOP.has(t));
  if (textTokens.length === 0) return null;

  const bestIn = (list: OcrCandidate[]) => {
    let best: OcrCandidate | null = null;
    let bestScore = 0;
    let bestCoverage = -1;
    for (const c of list) {
      const candTokens = tokenize(c.label).filter((t) => !STOP.has(t));
      if (candTokens.length === 0) continue;
      if (anniversaryConflict(candTokens, textTokens)) continue;
      if (!hasMeaningfulNonVitolaHit(candTokens, textTokens)) continue;
      const score = scoreTokens(candTokens, textTokens);
      // coverage prefers "Serie V" over "Serie V Melanio" when Melanio is absent
      const uniqCand = [...new Set(candTokens)];
      const matched = countMatchedTokens(candTokens, textTokens);
      const coverage = matched / uniqCand.length;
      if (
        score > bestScore ||
        (score === bestScore && coverage > bestCoverage) ||
        (score === bestScore &&
          coverage === bestCoverage &&
          uniqCand.length <
            (best
              ? new Set(tokenize(best.label).filter((t) => !STOP.has(t))).size
              : 999))
      ) {
        best = c;
        bestScore = score;
        bestCoverage = coverage;
      }
    }
    return { best, bestScore };
  };

  // faza 1: suzi pool na najbolje pogodjeni brend. Kod IZJEDNACENJA brend-skora
  // (npr. vise marki dijeli genericki token "habana") biraj brend cija linija
  // najbolje poklapa — tako "Partagás Serie D" pobjedjuje "La Perla Habana".
  let pool = candidates;
  const brands = [...new Set(candidates.map((c) => c.brand).filter((b): b is string => !!b))];
  if (brands.length > 1) {
    let bestBrandScore = 0;
    for (const b of brands) {
      const s = scoreTokens(tokenize(b).filter((t) => !STOP.has(t)), textTokens);
      if (s > bestBrandScore) bestBrandScore = s;
    }
    if (bestBrandScore >= 2) {
      const tied = brands.filter(
        (b) => scoreTokens(tokenize(b).filter((t) => !STOP.has(t)), textTokens) === bestBrandScore,
      );
      let bestBrand = tied[0];
      let bestBrandLine = -1;
      for (const b of tied) {
        const s = bestIn(candidates.filter((c) => c.brand === b)).bestScore;
        if (s > bestBrandLine) {
          bestBrandLine = s;
          bestBrand = b;
        }
      }
      pool = candidates.filter((c) => c.brand === bestBrand);
    }
  }

  // faza 2: najbolja linija unutar suzenog poola
  const { best, bestScore } = bestIn(pool);
  if (!best || bestScore < 2) return null;

  // Ako je pobjednik gola linija, a OCR eksplicitno spominje vitolu te linije,
  // podigni na cig-x@vitola (inače Imam dobije default vitolu — npr. Robusto).
  const upgraded = preferVitolaScoped(best, pool, textTokens);
  return { candidate: upgraded, score: bestScore };
}

/**
 * Upgrade bare `cig-x` → `cig-x@robusto` when OCR tokens include vitola-only words.
 */
export function preferVitolaScoped(
  best: OcrCandidate,
  pool: OcrCandidate[],
  textTokens: string[],
): OcrCandidate {
  if (best.id.includes("@")) return best;
  const prefix = `${best.id}@`;
  const scoped = pool.filter((c) => c.id.startsWith(prefix));
  if (scoped.length === 0) return best;

  const bareToks = new Set(tokenize(best.label).filter((t) => !STOP.has(t)));
  let pick: OcrCandidate | null = null;
  let bestExtra = 0;
  let bestCoverage = -1;

  for (const c of scoped) {
    const candToks = tokenize(c.label).filter((t) => !STOP.has(t));
    const extra = candToks.filter((t) => !bareToks.has(t));
    if (extra.length === 0) continue;
    const hit = extra.filter(
      (t) => textTokens.includes(t) || textTokens.some((x) => fuzzyEquals(t, x)),
    );
    if (hit.length === 0) continue;
    const coverage = hit.length / extra.length;
    if (
      hit.length > bestExtra ||
      (hit.length === bestExtra && coverage > bestCoverage)
    ) {
      bestExtra = hit.length;
      bestCoverage = coverage;
      pick = c;
    }
  }
  return pick ?? best;
}
