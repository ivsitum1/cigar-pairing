import type { PairingResult } from "../types";

export const SOFT_BAND_MARGIN = 5;
export const SOFT_BAND_WINDOW = 3;

/** First occurrence of each diversity key (preserves score order). */
export function diverseBy<T>(
  ranked: PairingResult<T>[],
  keyOf: (item: T) => string,
): PairingResult<T>[] {
  const seen = new Set<string>();
  return ranked.filter((r) => {
    const k = keyOf(r.item);
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

/** Brand-diverse filter for cigars (and any item with `brand`). */
export function brandDiverse<T extends { brand: string }>(
  ranked: PairingResult<T>[],
): PairingResult<T>[] {
  return diverseBy(ranked, (item) => item.brand);
}

/** Keep results within `margin` points of the top score. */
export function softBand<T>(
  ranked: PairingResult<T>[],
  margin: number = SOFT_BAND_MARGIN,
): PairingResult<T>[] {
  if (ranked.length === 0) return [];
  const maxScore = ranked[0].score;
  return ranked.filter((r) => r.score >= maxScore - margin);
}

/** UTC calendar day `YYYY-MM-DD` (stable for the UTC day). */
export function dayKey(date: Date = new Date()): string {
  return date.toISOString().slice(0, 10);
}

/**
 * Deterministic 32-bit hash (FNV-1a). Not cryptographic — only for
 * stable rotation seeds across sessions.
 */
export function stableHash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export type SoftBandWindowOpts<T> = {
  anchorId: string;
  dayKey: string;
  cycle?: number;
  windowSize?: number;
  margin?: number;
  /** Diversity key; default for cigars is brand via `brandDiverse` callers. */
  keyOf: (item: T) => string;
};

export type SoftBandWindowResult<T> = {
  window: PairingResult<T>[];
  band: PairingResult<T>[];
  /** Pool length used for cycling (band or fallback). */
  total: number;
};

/**
 * Brand/key-diverse soft band, then rotate by day seed + cycle.
 * If the band has fewer than `windowSize` items, fall back to the diverse
 * list (or full ranked if diverse is still short) — same UX as before.
 */
export function softBandWindow<T>(
  ranked: PairingResult<T>[],
  opts: SoftBandWindowOpts<T>,
): SoftBandWindowResult<T> {
  const windowSize = opts.windowSize ?? SOFT_BAND_WINDOW;
  const margin = opts.margin ?? SOFT_BAND_MARGIN;
  const cycle = opts.cycle ?? 0;

  if (ranked.length === 0) {
    return { window: [], band: [], total: 0 };
  }

  const diverse = diverseBy(ranked, opts.keyOf);
  const band = softBand(diverse, margin);
  const pool =
    band.length >= windowSize
      ? band
      : diverse.length >= windowSize
        ? diverse
        : ranked;

  const n = pool.length;
  const baseOffset =
    n === 0 ? 0 : stableHash(`${opts.anchorId}|${opts.dayKey}`) % n;
  const offset = n === 0 ? 0 : (baseOffset + cycle * windowSize) % n;

  const window: PairingResult<T>[] = [];
  for (let i = 0; i < Math.min(windowSize, n); i++) {
    window.push(pool[(offset + i) % n]);
  }

  return { window, band, total: n };
}
