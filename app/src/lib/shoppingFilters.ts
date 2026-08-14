// Filteri i sortiranje za Kupovinu (lista želja + dopuna zalihe).
//
// Čista logika, bez Reacta: popis se gleda u trgovini, s jednom rukom — mora se
// dati suziti na policu koju gledaš (format, jačina, zemlja, trgovina) i
// posložiti po cijeni bez razmišljanja. Obitelji oblika su iste one koje ima
// Katalog (`lib/vitolaShape`), da isti chip svugdje znači isto.
import type { ShapeFamily } from "./vitolaShape";
import { SHAPE_FAMILIES } from "./vitolaShape";

export type BuyKind = "cigar" | "drink";
export type BuyKindFilter = "all" | BuyKind;
export type BuySort = "name" | "priceAsc" | "priceDesc";

export interface BuyFilterable {
  kind: BuyKind;
  name: string;
  price: number | null;
  /** Normalizirani ključ trgovine (`wishlistShopKey`). */
  shopKey: string;
  /** Samo cigare; `null` i kad linija ima više formata pa se ne zna koji. */
  shape: ShapeFamily | null;
  /** 1–5, samo cigare. */
  strength: number | null;
  /** Zemlja podrijetla, samo cigare. */
  country: string | null;
}

export interface BuyFilters {
  kind: BuyKindFilter;
  shop: string | null;
  shape: ShapeFamily | null;
  strength: number | null;
  country: string | null;
}

export const EMPTY_BUY_FILTERS: BuyFilters = {
  kind: "all",
  shop: null,
  shape: null,
  strength: null,
  country: null,
};

export function hasActiveBuyFilters(f: BuyFilters): boolean {
  return (
    f.kind !== "all" ||
    f.shop != null ||
    f.shape != null ||
    f.strength != null ||
    f.country != null
  );
}

export function matchesBuyFilters(entry: BuyFilterable, f: BuyFilters): boolean {
  if (f.kind !== "all" && entry.kind !== f.kind) return false;
  if (f.shop != null && entry.shopKey !== f.shop) return false;
  // format / jačina / zemlja su pitanja o cigarama — pića na njima ispadaju
  if (f.shape != null && entry.shape !== f.shape) return false;
  if (f.strength != null && entry.strength !== f.strength) return false;
  if (f.country != null && entry.country !== f.country) return false;
  return true;
}

export function filterBuyEntries<T extends BuyFilterable>(list: T[], f: BuyFilters): T[] {
  return list.filter((e) => matchesBuyFilters(e, f));
}

/** Bez cijene ide na kraj u oba smjera — „ne znam koliko” nije ni jeftino ni skupo. */
export function sortBuyEntries<T extends BuyFilterable>(list: T[], sort: BuySort): T[] {
  const out = [...list];
  if (sort === "name") {
    return out.sort((a, b) => a.name.localeCompare(b.name, "hr"));
  }
  return out.sort((a, b) => {
    if (a.price == null && b.price == null) return a.name.localeCompare(b.name, "hr");
    if (a.price == null) return 1;
    if (b.price == null) return -1;
    const diff = sort === "priceAsc" ? a.price - b.price : b.price - a.price;
    return diff || a.name.localeCompare(b.name, "hr");
  });
}

export interface OptionCount<T> {
  value: T;
  count: number;
}

function countBy<T>(
  list: BuyFilterable[],
  pick: (e: BuyFilterable) => T | null,
): Map<T, number> {
  const counts = new Map<T, number>();
  for (const e of list) {
    if (e.kind !== "cigar") continue;
    const value = pick(e);
    if (value == null) continue;
    counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  return counts;
}

/** Formati prisutni na popisu, u redoslijedu Kataloga. */
export function shapeCounts(list: BuyFilterable[]): OptionCount<ShapeFamily>[] {
  const counts = countBy(list, (e) => e.shape);
  return SHAPE_FAMILIES.filter((s) => counts.has(s)).map((value) => ({
    value,
    count: counts.get(value)!,
  }));
}

/** Jačine prisutne na popisu, od najblaže prema najjačoj. */
export function strengthCounts(list: BuyFilterable[]): OptionCount<number>[] {
  const counts = countBy(list, (e) => e.strength);
  return [...counts.entries()]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => a.value - b.value);
}

/** Zemlje prisutne na popisu, najbrojnije prvo. */
export function countryCounts(list: BuyFilterable[]): OptionCount<string>[] {
  const counts = countBy(list, (e) => e.country);
  return [...counts.entries()]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value, "hr"));
}

export function buyTotal(list: BuyFilterable[]): number {
  return list.reduce((sum, e) => sum + (e.price ?? 0), 0);
}
