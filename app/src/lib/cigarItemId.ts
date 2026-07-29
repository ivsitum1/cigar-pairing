// Stanje kolekcije (Imam / Probao / ocjena / bilješka) po VITOLI, ne po liniji.
//
// Ranije je ključ bio `cigar.id`, pa je linija s više formata dijelila jedno
// stanje: označiš Don Tomas Bundle Churchill i isto se vidi pod Coronom. Ključ
// sada nosi i odabranu vitolu: `cig-don-tomas-bundle@churchill`.
//
// Linije s jednom vitolom namjerno ostaju na golom `cigar.id` — nema
// dvosmislenosti, a stara spremljena stanja se ne gube.

import type { Cigar, Vitola } from "../types";

export const VITOLA_ID_SEP = "@";

const slug = (label: string): string =>
  label
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/['’`]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

/**
 * Ključ stavke za kolekciju/dnevnik. `selectedVitola` postavlja `applyVitola`
 * kad je korisnik birao između više formata; bez njega ostaje `cigar.id`.
 */
export function cigarItemId(cigar: Cigar): string {
  const picked = cigar.selectedVitola;
  if (!picked) return cigar.id;
  const s = slug(picked);
  return s ? `${cigar.id}${VITOLA_ID_SEP}${s}` : cigar.id;
}

/** Rastavi ključ natrag na id linije + slug vitole (ako je ključ vitola-scoped). */
export function parseCigarItemId(itemId: string): {
  cigarId: string;
  vitolaSlug?: string;
} {
  const at = itemId.lastIndexOf(VITOLA_ID_SEP);
  if (at <= 0) return { cigarId: itemId };
  return {
    cigarId: itemId.slice(0, at),
    vitolaSlug: itemId.slice(at + VITOLA_ID_SEP.length),
  };
}

/** Vitola iz linije koja odgovara slugu iz ključa. */
export function vitolaFromItemId(
  cigar: Cigar,
  itemId: string,
): Vitola | undefined {
  const { vitolaSlug } = parseCigarItemId(itemId);
  if (!vitolaSlug) return undefined;
  return (cigar.vitolas ?? []).find((v) => slug(v.name) === vitolaSlug);
}

export const vitolaKeySlug = slug;
