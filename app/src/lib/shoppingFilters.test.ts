import { describe, expect, it } from "vitest";
import {
  EMPTY_BUY_FILTERS,
  buyTotal,
  countryCounts,
  filterBuyEntries,
  hasActiveBuyFilters,
  matchesBuyFilters,
  shapeCounts,
  sortBuyEntries,
  strengthCounts,
  type BuyFilterable,
} from "./shoppingFilters";

const cigar = (
  name: string,
  price: number | null,
  shopKey: string,
  shape: BuyFilterable["shape"],
  strength = 3,
  country = "Nikaragva",
): BuyFilterable => ({ kind: "cigar", name, price, shopKey, shape, strength, country });

const drink = (name: string, price: number | null, shopKey: string): BuyFilterable => ({
  kind: "drink",
  name,
  price,
  shopKey,
  shape: null,
  strength: null,
  country: null,
});

const LIST: BuyFilterable[] = [
  cigar("Oliva Serie V", 12, "humidor.hr", "robusto", 4, "Nikaragva"),
  cigar("Don Tomas", 8, "ostalo", "toro", 2, "Honduras"),
  cigar("Partagas", null, "humidor.hr", "robusto", 4, "Kuba"),
  drink("Diplomatico", 35, "vivat.hr"),
  drink("Zacapa", 45, "humidor.hr"),
];

describe("filtriranje popisa za kupnju", () => {
  it("bez filtera prolazi sve", () => {
    expect(filterBuyEntries(LIST, EMPTY_BUY_FILTERS)).toHaveLength(5);
    expect(hasActiveBuyFilters(EMPTY_BUY_FILTERS)).toBe(false);
  });

  it("filtrira po vrsti", () => {
    const cigars = filterBuyEntries(LIST, { ...EMPTY_BUY_FILTERS, kind: "cigar" });
    expect(cigars.map((e) => e.name)).toEqual(["Oliva Serie V", "Don Tomas", "Partagas"]);
    expect(filterBuyEntries(LIST, { ...EMPTY_BUY_FILTERS, kind: "drink" })).toHaveLength(2);
  });

  it("filtrira po trgovini", () => {
    const hits = filterBuyEntries(LIST, { ...EMPTY_BUY_FILTERS, shop: "humidor.hr" });
    expect(hits.map((e) => e.name)).toEqual(["Oliva Serie V", "Partagas", "Zacapa"]);
  });

  it("filtrira po obliku; pića na tom filteru ispadaju", () => {
    const hits = filterBuyEntries(LIST, { ...EMPTY_BUY_FILTERS, shape: "robusto" });
    expect(hits.map((e) => e.name)).toEqual(["Oliva Serie V", "Partagas"]);
  });

  it("filtrira po jačini i zemlji", () => {
    expect(
      filterBuyEntries(LIST, { ...EMPTY_BUY_FILTERS, strength: 4 }).map((e) => e.name),
    ).toEqual(["Oliva Serie V", "Partagas"]);
    expect(
      filterBuyEntries(LIST, { ...EMPTY_BUY_FILTERS, country: "Kuba" }).map((e) => e.name),
    ).toEqual(["Partagas"]);
  });

  it("filteri se zbrajaju", () => {
    const hits = filterBuyEntries(LIST, {
      kind: "cigar",
      shop: "humidor.hr",
      shape: "robusto",
      strength: 4,
      country: "Kuba",
    });
    expect(hits.map((e) => e.name)).toEqual(["Partagas"]);
    expect(
      matchesBuyFilters(LIST[0], {
        ...EMPTY_BUY_FILTERS,
        shape: "robusto",
        country: "Kuba",
      }),
    ).toBe(false);
  });

  it("prepoznaje da je filter aktivan", () => {
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, shop: "humidor.hr" })).toBe(true);
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, kind: "drink" })).toBe(true);
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, shape: "toro" })).toBe(true);
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, strength: 1 })).toBe(true);
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, country: "Kuba" })).toBe(true);
  });
});

describe("sortiranje popisa za kupnju", () => {
  it("abecedno", () => {
    expect(sortBuyEntries(LIST, "name").map((e) => e.name)).toEqual([
      "Diplomatico",
      "Don Tomas",
      "Oliva Serie V",
      "Partagas",
      "Zacapa",
    ]);
  });

  it("po cijeni uzlazno, bez cijene na kraju", () => {
    expect(sortBuyEntries(LIST, "priceAsc").map((e) => e.name)).toEqual([
      "Don Tomas",
      "Oliva Serie V",
      "Diplomatico",
      "Zacapa",
      "Partagas",
    ]);
  });

  it("po cijeni silazno, bez cijene i dalje na kraju", () => {
    expect(sortBuyEntries(LIST, "priceDesc").map((e) => e.name)).toEqual([
      "Zacapa",
      "Diplomatico",
      "Oliva Serie V",
      "Don Tomas",
      "Partagas",
    ]);
  });

  it("ne mijenja izvorni niz", () => {
    const before = LIST.map((e) => e.name);
    sortBuyEntries(LIST, "priceDesc");
    expect(LIST.map((e) => e.name)).toEqual(before);
  });
});

describe("brojevi uz filtere", () => {
  it("oblici idu redoslijedom Kataloga, samo oni prisutni", () => {
    expect(shapeCounts(LIST)).toEqual([
      { value: "robusto", count: 2 },
      { value: "toro", count: 1 },
    ]);
  });

  it("jačine idu od najblaže prema najjačoj", () => {
    expect(strengthCounts(LIST)).toEqual([
      { value: 2, count: 1 },
      { value: 4, count: 2 },
    ]);
  });

  it("zemlje idu po brojnosti", () => {
    expect(countryCounts(LIST)).toEqual([
      { value: "Honduras", count: 1 },
      { value: "Kuba", count: 1 },
      { value: "Nikaragva", count: 1 },
    ]);
  });

  it("pića ne ulaze u brojeve cigarskih filtera", () => {
    expect(shapeCounts([drink("Zacapa", 45, "humidor.hr")])).toEqual([]);
    expect(strengthCounts([drink("Zacapa", 45, "humidor.hr")])).toEqual([]);
    expect(countryCounts([drink("Zacapa", 45, "humidor.hr")])).toEqual([]);
  });

  it("ukupno preskače stavke bez cijene", () => {
    expect(buyTotal(LIST)).toBe(100);
  });
});
