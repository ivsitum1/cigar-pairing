import type { Cigar, Vitola } from "../types";
import { cigarsByBrand } from "../data";
import { applyVitola, resolveDefaultVitola, uniqueVitolas } from "./cigarVitola";

// Sadržaj samplera je opisni tekst ("Connecticut Robusto ×2"). Ovdje ga
// razlučujemo u pravu cigaru istog brenda da se chip može otvoriti.

const strip = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();

// generički tokeni koji ne razlikuju proizvod
const GENERIC = new Set(["cigar", "cigars", "the", "no"]);

// tokeni bez količine (×2), dimenzija (5 x 50), razlomaka i čistih brojeva
function toks(s: string): string[] {
  return strip(s)
    .replace(/[×x]\s*\d+\b/g, " ") // ×2 / x2
    .replace(/\d+\s*[⁄/]\s*\d+/g, " ") // razlomci "6 1/8"
    .replace(/[^a-z0-9]+/g, " ")
    .split(/\s+/)
    .filter((t) => t.length >= 2 && !/^\d+$/.test(t) && !GENERIC.has(t));
}

function signature(c: Cigar): { line: Set<string>; all: Set<string> } {
  const line = new Set(toks(c.line));
  const all = new Set(line);
  for (const t of toks(c.vitola)) all.add(t);
  for (const v of c.vitolas ?? []) for (const t of toks(v.name)) all.add(t);
  return { line, all };
}

// odaberi vitolu koja se najbolje poklapa s oznakom (npr. "…Robusto" → Robusto).
// Tokeni koji nisu već u nazivu linije (npr. "robusto" kod linije "Connecticut")
// najviše razlikuju vitolu, pa nose puno veću težinu.
function pickVitola(c: Cigar, want: string[]): Cigar {
  const vs = uniqueVitolas(c);
  if (vs.length === 0) return c;
  if (vs.length === 1) return applyVitola(c, vs[0]);
  const lineTokens = new Set(toks(c.line));
  const residual = want.filter((t) => !lineTokens.has(t));
  let bestV: Vitola | null = null;
  let bestScore = 0;
  for (const v of vs) {
    const vt = toks(v.name);
    const score =
      vt.filter((t) => residual.includes(t)).length * 10 +
      vt.filter((t) => want.includes(t)).length;
    if (score > bestScore) {
      bestScore = score;
      bestV = v;
    }
  }
  if (bestV) return applyVitola(c, bestV);
  const def = resolveDefaultVitola(c);
  return def ? applyVitola(c, def) : c;
}

/**
 * Nađi cigaru koju sampler-oznaka opisuje. Konzervativno: svi značajni
 * tokeni oznake moraju biti u potpisu kandidata; inače null (chip ostaje
 * običan, bez linka) da se izbjegne krivo otvaranje.
 */
export function resolveSamplerCigar(
  brand: string,
  label: string,
  selfId: string,
): Cigar | null {
  const want = toks(label);
  if (!want.length) return null;
  const cands = cigarsByBrand(brand).filter(
    (c) => c.id !== selfId && !(c.lineup && c.lineup.length),
  );
  let best: { c: Cigar; score: number; extra: number } | null = null;
  for (const c of cands) {
    const sig = signature(c);
    if (!want.every((t) => sig.all.has(t))) continue;
    const lineHits = want.filter((t) => sig.line.has(t)).length;
    const score = lineHits * 2 + want.length; // više pogodaka u liniji = bolje
    const extra = sig.all.size; // manje viška tokena = specifičnije
    if (
      !best ||
      score > best.score ||
      (score === best.score && extra < best.extra)
    ) {
      best = { c, score, extra };
    }
  }
  return best ? pickVitola(best.c, want) : null;
}
