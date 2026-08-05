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
  /** When true, cycle 0 starts at the top of the pool (no day-hash drift). */
  stableTop?: boolean;
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
    opts.stableTop || n === 0
      ? 0
      : stableHash(`${opts.anchorId}|${opts.dayKey}`) % n;
  const offset = n === 0 ? 0 : (baseOffset + cycle * windowSize) % n;

  const window: PairingResult<T>[] = [];
  for (let i = 0; i < Math.min(windowSize, n); i++) {
    window.push(pool[(offset + i) % n]);
  }

  return { window, band, total: n };
}

/**
 * Stable #1 + button rotation among near-equals.
 * - cycle 0 returns `ranked[0]` (ili, uz `tieSeed`, jednog od bodovno
 *   izjednačenih s vrhom — vidi dolje).
 * - prvi krug rotacije uzima po jedno piće iz svakog ključa (stila), kao i
 *   prije; sljedeći krugovi idu u DUBINU istog ključa.
 *
 * Zašto dubina: kad katalog nema čime razlikovati boce (46 konjaka staje u
 * dva profila — svi XO dijele tijelo, slatkoću i note), pojas na vrhu su
 * deseci gotovo istih bodova. Stari pool je uzimao samo najbolju bocu po
 * stilu, pa je „Sljedeći prijedlog” u konjaku često imao točno jednu opciju
 * i kartica je zauvijek pokazivala istu bocu.
 *
 * `tieSeed` (npr. `cigarId|dan`) rotira među SAVRŠENO izjednačenima na vrhu.
 * Kad engine doista ne razlikuje dvije boce, nema razloga da uvijek pobijedi
 * ista — a sjeme drži izbor stabilnim kroz dan i kroz re-render.
 */
export function stableBestRotate<T extends { id: string }>(
  ranked: PairingResult<T>[],
  cycle: number,
  opts: {
    margin?: number;
    keyOf: (item: T) => string;
    tieSeed?: string;
    /** Najmanji broj ponuda; ispod margine se dopunjuje po bodovima. */
    minPool?: number;
  },
): {
  pick: PairingResult<T> | undefined;
  pool: PairingResult<T>[];
  total: number;
} {
  if (ranked.length === 0) {
    return { pick: undefined, pool: [], total: 0 };
  }

  const margin = opts.margin ?? SOFT_BAND_MARGIN;
  const band = softBand(ranked, margin);

  const ties = band.filter((r) => r.score === ranked[0].score);
  const head =
    opts.tieSeed && ties.length > 1
      ? ties[stableHash(opts.tieSeed) % ties.length]
      : ranked[0];

  const groups = new Map<string, PairingResult<T>[]>();
  for (const r of band) {
    const key = opts.keyOf(r.item);
    const list = groups.get(key);
    if (list) list.push(r);
    else groups.set(key, [r]);
  }

  const seen = new Set<string>([head.item.id]);
  const pool: PairingResult<T>[] = [head];
  const lists = [...groups.values()];
  const depth = lists.reduce((max, l) => Math.max(max, l.length), 0);
  for (let i = 0; i < depth; i++) {
    for (const list of lists) {
      const r = list[i];
      if (!r || seen.has(r.item.id)) continue;
      seen.add(r.item.id);
      pool.push(r);
    }
  }

  // kad vrh bježi za više od margine, pojas ostane sam — gumb „Sljedeći
  // prijedlog” tada ne bi imao što ponuditi. Dopuni po bodovima, kao što
  // softBandWindow pada na širi popis.
  const minPool = opts.minPool ?? SOFT_BAND_WINDOW;
  for (const r of ranked) {
    if (pool.length >= minPool) break;
    if (seen.has(r.item.id)) continue;
    seen.add(r.item.id);
    pool.push(r);
  }

  const total = pool.length;
  const idx = ((cycle % total) + total) % total;
  return { pick: pool[idx], pool, total };
}
