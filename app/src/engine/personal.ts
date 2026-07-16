// Lokalna personalizacija iz dnevnika sparivanja — sve ostaje na uređaju.
// Iz ocijenjenih zapisa (1-10) gradi afinitete po stilu pića i brendu cigare;
// engine ih koristi kao blagi nudge s objašnjenjem, nikad kao presudu.
import type { PairingReason } from "../types";
import { WEIGHTS } from "./rules";

export interface RatedPairing {
  rating: number | null;
  drinkStyle?: string;
  cigarBrand?: string;
}

export interface PersonalPrefs {
  drinkStyle: Record<string, number>; // -1..1 prosjecno odstupanje od neutralne ocjene
  cigarBrand: Record<string, number>;
  entries: number;
}

export const EMPTY_PREFS: PersonalPrefs = { drinkStyle: {}, cigarBrand: {}, entries: 0 };

// ocjena 1-10 -> odstupanje od neutralnog 6, ograniceno na [-1, 1]
const deviation = (rating: number) => Math.max(-1, Math.min(1, (rating - 6) / 4));

export function buildPrefs(rated: RatedPairing[]): PersonalPrefs {
  const style: Record<string, { sum: number; n: number }> = {};
  const brand: Record<string, { sum: number; n: number }> = {};
  let entries = 0;
  for (const r of rated) {
    if (r.rating == null) continue;
    entries += 1;
    const d = deviation(r.rating);
    if (r.drinkStyle) {
      const s = (style[r.drinkStyle] ??= { sum: 0, n: 0 });
      s.sum += d;
      s.n += 1;
    }
    if (r.cigarBrand) {
      const b = (brand[r.cigarBrand] ??= { sum: 0, n: 0 });
      b.sum += d;
      b.n += 1;
    }
  }
  // shrinkage n/(n+1): jedna usamljena ocjena vuce upola slabije od prosjeka
  // vise ocjena, pa personalizacija jaca tek s navikom
  const collapse = (m: Record<string, { sum: number; n: number }>) =>
    Object.fromEntries(
      Object.entries(m).map(([k, v]) => [k, (v.sum / v.n) * (v.n / (v.n + 1))]),
    );
  return { drinkStyle: collapse(style), cigarBrand: collapse(brand), entries };
}

const nudgePoints = (affinity: number) => Math.round(affinity * WEIGHTS.personal);

export function personalStyleReason(
  prefs: PersonalPrefs,
  drinkStyle: string,
): PairingReason | null {
  const affinity = prefs.drinkStyle[drinkStyle];
  if (!affinity) return null;
  const pts = nudgePoints(affinity);
  if (pts === 0) return null;
  return {
    rule: "personal-style",
    score: pts,
    text:
      pts > 0
        ? {
            hr: "Pića ovog stila su ti po dnevniku dobro sjela.",
            en: "Drinks of this style scored well in your journal.",
          }
        : {
            hr: "Pića ovog stila su ti po dnevniku slabije sjela.",
            en: "Drinks of this style scored poorly in your journal.",
          },
  };
}

export function personalBrandReason(
  prefs: PersonalPrefs,
  cigarBrand: string,
): PairingReason | null {
  const affinity = prefs.cigarBrand[cigarBrand];
  if (!affinity) return null;
  const pts = nudgePoints(affinity);
  if (pts === 0) return null;
  return {
    rule: "personal-brand",
    score: pts,
    text:
      pts > 0
        ? {
            hr: "Cigare ovog brenda su ti po dnevniku dobro sjele.",
            en: "This brand's cigars scored well in your journal.",
          }
        : {
            hr: "Cigare ovog brenda su ti po dnevniku slabije sjele.",
            en: "This brand's cigars scored poorly in your journal.",
          },
  };
}
