// Humidor broji vitole, ne linije.
//
// Zaliha je dugo znala završiti na golom ključu linije (`cig-x`): Brzi unos i
// kartica dodavali su „liniju”, a kolekcija i dnevnik pišu po vitoli
// (`cig-x@robusto`). Posljedica: u humidoru piše 6 komada, a kartica Robusta
// pokazuje stanje 0 jer na tom ključu doista nema ničega.
//
// Ovdje su pomoćnici koji drže jedno pravilo: linija s više formata mora imati
// zalihu po vitoli. Sve je bez ovisnosti o Reactu, pa se lako testira.
import type { Cigar, Vitola } from "../types";
import { cigarItemId, parseCigarItemId, vitolaFromItemId } from "./cigarItemId";
import { applyVitola, uniqueVitolas } from "./cigarVitola";

/** Ključ zalihe za tu vitolu — isti ključ koji pišu kolekcija i dnevnik. */
export function vitolaStockId(line: Cigar, vitola: Vitola): string {
  return cigarItemId(applyVitola(line, vitola));
}

/**
 * Ključ ne nosi vitolu, a linija ih ima više → ne zna se što stoji u kutiji.
 * Takvu zalihu ne smijemo dodavati niti tiho pripisati nekoj vitoli; korisnik
 * je razrješava jednim dodirom („Odredi vitolu”).
 */
export function stockNeedsVitola(line: Cigar | undefined, itemId: string): boolean {
  if (!line) return false;
  if (parseCigarItemId(itemId).vitolaSlug) return false;
  return uniqueVitolas(line).length > 1;
}

/**
 * Ime vitole iza ključa zalihe. `null` = vitola nije određena (stara zaliha po
 * liniji). Linija s jednim formatom nema što razdvajati, pa goli ključ nosi
 * upravo taj format.
 */
export function stockVitolaName(
  line: Cigar | undefined,
  itemId: string,
): string | null {
  const { vitolaSlug } = parseCigarItemId(itemId);
  if (vitolaSlug) {
    if (!line) return vitolaSlug;
    return vitolaFromItemId(line, itemId)?.name ?? vitolaSlug;
  }
  if (!line) return null;
  const vitolas = uniqueVitolas(line);
  if (vitolas.length === 1) return vitolas[0].name;
  return vitolas.length === 0 ? (line.selectedVitola ?? line.vitola) : null;
}

/** Vitole te linije kojih još nema u zadanim ključevima zalihe. */
export function vitolasNotInStock(
  line: Cigar,
  presentItemIds: Iterable<string>,
): Vitola[] {
  const present = new Set(presentItemIds);
  return uniqueVitolas(line).filter((v) => !present.has(vitolaStockId(line, v)));
}

export interface StockLineGroup<T> {
  /** Id linije bez vitole — `cig-x` i za `cig-x@robusto`. */
  cigarId: string;
  total: number;
  entries: T[];
}

/**
 * Zalihu grupira po liniji, zadržavajući poredak prvog pojavljivanja. Humidor
 * tako prikazuje jednu karticu po liniji, a unutar nje red po vitoli.
 */
export function groupStockByLine<T extends { itemId: string; count: number }>(
  entries: T[],
): StockLineGroup<T>[] {
  const groups = new Map<string, StockLineGroup<T>>();
  for (const entry of entries) {
    const { cigarId } = parseCigarItemId(entry.itemId);
    const group = groups.get(cigarId);
    if (group) {
      group.entries.push(entry);
      group.total += entry.count;
    } else {
      groups.set(cigarId, { cigarId, total: entry.count, entries: [entry] });
    }
  }
  return [...groups.values()];
}
