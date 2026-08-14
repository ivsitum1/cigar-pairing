// Filteri i sortiranje za Kupovinu (lista želja + dopuna zalihe).
//
// Čista logika, bez Reacta: popis za kupnju je kratak, ali se gleda u trgovini
// — mora se dati suziti na jednu trgovinu, jednu vrstu vitole i posložiti po
// cijeni bez razmišljanja.
import type { VitolaFamily } from "./vitolaFamily";
import { VITOLA_FAMILY_ORDER } from "./vitolaFamily";

export type BuyKind = "cigar" | "drink";
export type BuyKindFilter = "all" | BuyKind;
export type BuySort = "name" | "priceAsc" | "priceDesc";

export interface BuyFilterable {
  kind: BuyKind;
  name: string;
  price: number | null;
  /** Normalizirani ključ trgovine (`wishlistShopKey`). */
  shopKey: string;
  /** Samo cigare; pića nemaju vitolu. */
  family: VitolaFamily | null;
}

export interface BuyFilters {
  kind: BuyKindFilter;
  shop: string | null;
  family: VitolaFamily | null;
}

export const EMPTY_BUY_FILTERS: BuyFilters = { kind: "all", shop: null, family: null };

export function hasActiveBuyFilters(f: BuyFilters): boolean {
  return f.kind !== "all" || f.shop != null || f.family != null;
}

export function matchesBuyFilters(entry: BuyFilterable, f: BuyFilters): boolean {
  if (f.kind !== "all" && entry.kind !== f.kind) return false;
  if (f.shop != null && entry.shopKey !== f.shop) return false;
  // filter vitole je pitanje o cigarama — pića na njega ispadaju, ne prolaze
  if (f.family != null && entry.family !== f.family) return false;
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

export interface FamilyCount {
  family: VitolaFamily;
  count: number;
}

/** Vrste vitola prisutne na popisu, u fiksnom redoslijedu (kratke → duge). */
export function familyCounts(list: BuyFilterable[]): FamilyCount[] {
  const counts = new Map<VitolaFamily, number>();
  for (const e of list) {
    if (e.kind !== "cigar" || e.family == null) continue;
    counts.set(e.family, (counts.get(e.family) ?? 0) + 1);
  }
  return VITOLA_FAMILY_ORDER.filter((f) => counts.has(f)).map((family) => ({
    family,
    count: counts.get(family)!,
  }));
}

export function buyTotal(list: BuyFilterable[]): number {
  return list.reduce((sum, e) => sum + (e.price ?? 0), 0);
}
