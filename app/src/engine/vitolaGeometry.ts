// Geometrija vitole (ring × duljina) → efektivna cigara za pairing.
// Tanji ring: toplije/brže, wrapper-forward. Deblji: hladnije/glađe.
// Kalibracija konzervativna — geometrija dotjeruje, ne preokreće body-match.

import type { Cigar, PairingReason } from "../types";

export const GEOMETRY = {
  thinRingMax: 42, // ≤42: panetela/corona/lonsdale/lancero — wrapper-forward, vruće
  thickRingMin: 54, // ≥54: toro gordo/60 — hladno, glatko, filler-forward
  longLenMin: 160, // ≥160mm: churchill/double corona — dim se hladi na putu
  thin: { strengthDelta: +0.4, bodyDelta: +0.2, wrapperForwardBonus: 5 },
  thick: { strengthDelta: -0.3, bodyDelta: -0.1, wrapperForwardBonus: 0 },
  longSmoothStrengthDelta: -0.1, // duljina blago glača početnu oštrinu
} as const;

const clamp15 = (x: number) => Math.max(1, Math.min(5, x));

/** Ring/length iz odabrane vitole ili iz "RING x LENGTHmm" stringa; null ako nepoznato.
 *  Nakon applyVitola() je vitolas.length === 1 (odabir). Na razini linije (više vitola)
 *  ne uzimamo vitolas[0] — to je proizvoljan redoslijed kataloga — nego format linije. */
export function parseGeometry(cigar: Cigar): { ring: number | null; len: number | null } {
  const selected = cigar.vitolas?.length === 1 ? cigar.vitolas[0] : undefined;
  let ring = selected?.ring ?? null;
  let len = selected?.lengthMM ?? null;
  const m = /(\d{2})\s*[x×]\s*(\d{2,3})\s*mm/i.exec(cigar.format ?? "");
  if (ring == null && m) ring = Number(m[1]);
  if (len == null && m) len = Number(m[2]);
  return { ring, len };
}

/**
 * EFEKTIVNA cigara (strength/body dotjerani geometrijom) + wrapper-forward bonus + reason.
 * Ako geometrija nepoznata (≈1% unosa) → neutralno (cigar netaknut).
 */
export function applyGeometry(cigar: Cigar): {
  cigar: Cigar;
  wrapperForwardBonus: number;
  reason?: PairingReason;
} {
  const { ring, len } = parseGeometry(cigar);
  if (ring == null) return { cigar, wrapperForwardBonus: 0 };

  let dS = 0;
  let dB = 0;
  let wrapperForwardBonus = 0;
  let reason: PairingReason | undefined;

  if (ring <= GEOMETRY.thinRingMax) {
    dS += GEOMETRY.thin.strengthDelta;
    dB += GEOMETRY.thin.bodyDelta;
    wrapperForwardBonus = GEOMETRY.thin.wrapperForwardBonus;
    reason = {
      rule: "vitola-thin",
      score: 0,
      text: {
        hr: `Tanak ring (${ring}): gori toplije i brže, wrapper vodi — intenzivnije i začinjenije.`,
        en: `Thin ring (${ring}): burns hotter and faster, wrapper-led — more intense and spicy.`,
      },
    };
  } else if (ring >= GEOMETRY.thickRingMin) {
    dS += GEOMETRY.thick.strengthDelta;
    dB += GEOMETRY.thick.bodyDelta;
    reason = {
      rule: "vitola-thick",
      score: 0,
      text: {
        hr: `Debeo ring (${ring}): gori hladnije i glađe, punija/mekša strana duhana.`,
        en: `Thick ring (${ring}): burns cooler and smoother, fuller/mellower tobacco.`,
      },
    };
  }
  if (len != null && len >= GEOMETRY.longLenMin) dS += GEOMETRY.longSmoothStrengthDelta;

  const eff: Cigar = {
    ...cigar,
    strength: clamp15(cigar.strength + dS),
    body: clamp15(cigar.body + dB),
  };
  return { cigar: eff, wrapperForwardBonus, reason };
}
