/** OCR catalog candidates for cigars — expand multi-vitola lines (Cusano Robusto vs Figurado). */
import type { Cigar } from "../types";
import { vitolaKeySlug } from "./cigarItemId";
import { uniqueVitolas } from "./cigarVitola";
import type { OcrCandidate } from "./ocrMatch";

/**
 * Receipt lines often end with vitola (`… Cusano Robusto/16`). Without vitola-
 * scoped candidates both sizes collapse to one catalog id and only the line's
 * default vitola (often Robusto) is marked Imam.
 */
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
        label: `${brand} ${c.line} ${v.name}`,
        brand: c.brand,
      })),
    ];
  });
}
