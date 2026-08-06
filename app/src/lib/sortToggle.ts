// Tri-stanje sortiranja za chipove u katalogu.
//
// Prije je chip bio prekidač: klik = sortiraj po tom ključu, i to uvijek u
// jednom, unaprijed zadanom smjeru. "Cijena" je time značila samo "najjeftinije
// prvo" — nije se moglo pitati "što je ovdje najskuplje", a jednom uključeno
// sortiranje nije se dalo isključiti bez odabira drugog ključa.
//
// Sada svaki chip ciklira: 1. klik zadani smjer → 2. klik obrnuti smjer →
// 3. klik isključeno (popis se vraća na zadani poredak kartice).
export type SortDir = "asc" | "desc";

export interface SortState<K extends string> {
  key: K;
  dir: SortDir;
}

export const flipDir = (d: SortDir): SortDir => (d === "asc" ? "desc" : "asc");

/**
 * Sljedeće stanje nakon klika na `key`.
 * `defaultDir` je smjer prvog klika za taj ključ (cijena raste, kvaliteta pada).
 * Vraća `null` kad se sortiranje gasi.
 */
export function cycleSort<K extends string>(
  current: SortState<K> | null,
  key: K,
  defaultDir: SortDir,
): SortState<K> | null {
  if (!current || current.key !== key) return { key, dir: defaultDir };
  if (current.dir === defaultDir) return { key, dir: flipDir(defaultDir) };
  return null;
}

/** Strelica uz aktivni chip. Neaktivan ključ nema strelicu. */
export function sortArrow<K extends string>(
  current: SortState<K> | null,
  key: K,
): string {
  if (!current || current.key !== key) return "";
  return current.dir === "asc" ? " ↑" : " ↓";
}

/**
 * Komparator okrenut u traženom smjeru. `cmp` je uvijek pisan u svom ZADANOM
 * smjeru (cijena uzlazno, kvaliteta silazno), pa se obrne samo kad se traži
 * suprotno od zadanog.
 */
export function directedComparator<T>(
  cmp: (a: T, b: T) => number,
  defaultDir: SortDir,
  dir: SortDir,
): (a: T, b: T) => number {
  return dir === defaultDir ? cmp : (a, b) => -cmp(a, b);
}
