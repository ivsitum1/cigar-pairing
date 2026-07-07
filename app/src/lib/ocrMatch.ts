// Fuzzy matching OCR teksta na katalog. Dvofazno: prvo brend, pa linija
// unutar brenda; tolerira tipicne OCR zamjene znakova (0/O, q/g...).

export interface OcrCandidate {
  id: string;
  label: string;
  brand?: string; // omogucuje dvofazni matching (prvo brend, pa linija)
}

const normalize = (s: string) =>
  s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();

export const tokenize = (s: string) =>
  normalize(s)
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 3);

export const STOP = new Set(["rum", "ron", "rhum", "whisky", "whiskey", "cigar", "cigars",
  "anos", "years", "old", "aged", "vol", "70cl", "700ml", "product", "the"]);

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
  let score = 0;
  for (const t of candTokens) {
    if (textSet.has(t)) {
      score += t.length >= 5 ? 2 : 1;
    } else if (textTokens.some((x) => fuzzyEquals(t, x))) {
      score += t.length >= 5 ? 1 : 0.5;
    }
  }
  return score;
}

/** Nadji kandidata s najboljim (fuzzy) poklapanjem; prvo suzi po brendu. */
export function matchOcrText(
  text: string,
  candidates: OcrCandidate[],
): { candidate: OcrCandidate; score: number } | null {
  const textTokens = tokenize(text).filter((t) => !STOP.has(t));
  if (textTokens.length === 0) return null;

  // faza 1: ako kandidati nose brend, suzi pool na najbolje pogodjeni brend
  let pool = candidates;
  const brands = [...new Set(candidates.map((c) => c.brand).filter((b): b is string => !!b))];
  if (brands.length > 1) {
    let bestBrand: string | null = null;
    let bestBrandScore = 0;
    for (const b of brands) {
      const s = scoreTokens(tokenize(b).filter((t) => !STOP.has(t)), textTokens);
      if (s > bestBrandScore) {
        bestBrand = b;
        bestBrandScore = s;
      }
    }
    if (bestBrand && bestBrandScore >= 2) {
      pool = candidates.filter((c) => c.brand === bestBrand);
    }
  }

  // faza 2: najbolja linija unutar poola
  let best: OcrCandidate | null = null;
  let bestScore = 0;
  for (const c of pool) {
    const candTokens = tokenize(c.label).filter((t) => !STOP.has(t));
    if (candTokens.length === 0) continue;
    const score = scoreTokens(candTokens, textTokens);
    if (score > bestScore) {
      best = c;
      bestScore = score;
    }
  }
  return best && bestScore >= 2 ? { candidate: best, score: bestScore } : null;
}
