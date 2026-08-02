// Omiljene marke — cigara i pića zajedno.
//
// Kolekcija bilježi pojedine boce i vitole; ovo je razina iznad: markama
// kojima se vraćaš. Netko voli Foursquare bez obzira koju ekspresiju drži, i
// to je podatak koji „Imam" ne hvata.
//
// Ključ nosi vrstu (`cigar:Padrón`, `drink:Foursquare`) jer se imena marki
// mogu preklapati među vrstama, a i filtri su odvojeni.
import { useSyncExternalStore } from "react";

export type FavoriteKind = "cigar" | "drink";

const KEY = "cigar-pairing-favorite-brands-v1";

export const favoriteKey = (kind: FavoriteKind, brand: string): string =>
  `${kind}:${brand}`;

function load(): Set<string> {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return new Set();
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return new Set();
    return new Set(parsed.filter((x): x is string => typeof x === "string"));
  } catch {
    return new Set();
  }
}

let cache = load();
const listeners = new Set<() => void>();
let storageFailed = false;

function persist(next: Set<string>) {
  cache = next;
  try {
    localStorage.setItem(KEY, JSON.stringify([...next].sort()));
    storageFailed = false;
  } catch {
    // pun ili blokiran storage — oznaka vrijedi do zatvaranja
    storageFailed = true;
  }
  listeners.forEach((l) => l());
}

const subscribe = (cb: () => void) => {
  listeners.add(cb);
  return () => listeners.delete(cb);
};

export function useFavoriteBrands(): Set<string> {
  return useSyncExternalStore(subscribe, () => cache);
}

export function useFavoritesStorageHealth(): boolean {
  return useSyncExternalStore(subscribe, () => storageFailed);
}

export const isFavoriteBrand = (kind: FavoriteKind, brand: string): boolean =>
  cache.has(favoriteKey(kind, brand));

export function toggleFavoriteBrand(kind: FavoriteKind, brand: string): boolean {
  const key = favoriteKey(kind, brand);
  const next = new Set(cache);
  const nowFavorite = !next.has(key);
  if (nowFavorite) next.add(key);
  else next.delete(key);
  persist(next);
  return nowFavorite;
}

/** Marke jedne vrste, abecedno — za „samo omiljeni" filtre i izvoz. */
export function favoriteBrandsOf(kind: FavoriteKind): string[] {
  const prefix = `${kind}:`;
  return [...cache]
    .filter((k) => k.startsWith(prefix))
    .map((k) => k.slice(prefix.length))
    .sort((a, b) => a.localeCompare(b));
}

/** Backup: ide uz kolekciju u Export/Import. */
export function exportFavorites(): string[] {
  return [...cache].sort();
}

export function importFavorites(value: unknown): boolean {
  if (!Array.isArray(value)) return false;
  const valid = value.filter(
    (x): x is string => typeof x === "string" && /^(cigar|drink):.+/.test(x),
  );
  persist(new Set(valid));
  return true;
}
