/** OCR catalog candidates for cigars — expand every multi-vitola line. */
import type { Cigar } from "../types";
import { vitolaKeySlug } from "./cigarItemId";
import { uniqueVitolas } from "./cigarVitola";
import type { OcrCandidate } from "./ocrMatch";

/**
 * Receipt lines often end with vitola (`… Robusto/16`, `… Churchill`).
 * Without vitola-scoped candidates, different sizes of the same line collapse
 * to one catalog id and Imam gets only the line default vitola.
 *
 * Applies to all brands (Oliva, Don Tomas, Perdomo, Cusano, …) — any line
 * with `uniqueVitolas(c).length > 1`.
 */
/**
 * Build OCR label for a vitola without repeating line tokens
 * ("Serie V" + "Serie V Lancero" → "Oliva Serie V Lancero").
 */
function vitolaOcrLabel(brand: string, line: string, vitolaName: string): string {
  const lineN = line.trim().toLowerCase();
  const vitN = vitolaName.trim();
  if (!lineN) return `${brand} ${vitN}`.trim();
  if (vitN.toLowerCase().startsWith(lineN)) {
    return `${brand} ${vitN}`.trim();
  }
  return `${brand} ${line} ${vitN}`.trim();
}

export function buildCigarOcrCandidates(
  cigars: Cigar[],
  brandLabel: (brand: string) => string = (b) => b,
): OcrCandidate[] {
  return cigars.flatMap((c) => {
    const brand = brandLabel(c.brand);
    const base: OcrCandidate = {
      id: c.id,
      label: `${brand} ${c.line}`,
      brand: c.brand,
    };
    const vitolas = uniqueVitolas(c);
    if (vitolas.length <= 1) return [base];
    return [
      base,
      ...vitolas.map((v) => ({
        id: `${c.id}@${vitolaKeySlug(v.name)}`,
        label: vitolaOcrLabel(brand, c.line, v.name),
        brand: c.brand,
      })),
    ];
  });
}
