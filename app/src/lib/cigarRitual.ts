// Ritam/trajanje: hint prema očekivanom vremenu pušenja. Bez bodovanja —
// samo pomaže korisniku uskladiti tempo pijenja s duljinom cigare.

import type { Lang } from "../types";

export interface RitualHint {
  icon: string;
  text: string;
}

/**
 * Hint o ritmu prema trajanju pušenja (min). `null` kad trajanje nije poznato.
 * Granice: ≤30 kratko, ≥75 dugo, između srednje.
 */
export function ritualHint(
  smokeTimeMin: number | null | undefined,
  lang: Lang,
): RitualHint | null {
  if (!smokeTimeMin || smokeTimeMin <= 0) return null;
  const m = Math.round(smokeTimeMin);
  if (m >= 75) {
    return {
      icon: "⏳",
      text:
        lang === "hr"
          ? `Duga cigara (~${m}′): odaberi piće za sporo pijuckanje ili planiraj drugu turu.`
          : `Long cigar (~${m}′): pick a drink to sip slowly, or plan a second pour.`,
    };
  }
  if (m <= 30) {
    return {
      icon: "⚡",
      text:
        lang === "hr"
          ? `Kratka cigara (~${m}′): brz ritam, jedno dobro nalijevanje je dovoljno.`
          : `Short cigar (~${m}′): a quick pace — one good pour is enough.`,
    };
  }
  return {
    icon: "⏱",
    text:
      lang === "hr"
        ? `Srednje trajanje (~${m}′): ugodan tempo za jednu čašu.`
        : `Medium length (~${m}′): an easy pace for a single glass.`,
  };
}
