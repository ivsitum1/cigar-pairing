import { describe, expect, it } from "vitest";
import {
  EMPTY_BUY_FILTERS,
  buyTotal,
  familyCounts,
  filterBuyEntries,
  hasActiveBuyFilters,
  matchesBuyFilters,
  sortBuyEntries,
  type BuyFilterable,
} from "./shoppingFilters";

const cigar = (
  name: string,
  price: number | null,
  shopKey: string,
  family: BuyFilterable["family"],
): BuyFilterable => ({ kind: "cigar", name, price, shopKey, family });

const drink = (name: string, price: number | null, shopKey: string): BuyFilterable => ({
  kind: "drink",
  name,
  price,
  shopKey,
  family: null,
});

const LIST: BuyFilterable[] = [
  cigar("Oliva Serie V", 12, "humidor.hr", "robusto"),
  cigar("Don Tomas", 8, "ostalo", "toro"),
  cigar("Partagas", null, "humidor.hr", "robusto"),
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

  it("filtrira po vrsti vitole; pića na tom filteru ispadaju", () => {
    const hits = filterBuyEntries(LIST, { ...EMPTY_BUY_FILTERS, family: "robusto" });
    expect(hits.map((e) => e.name)).toEqual(["Oliva Serie V", "Partagas"]);
  });

  it("filteri se zbrajaju", () => {
    const hits = filterBuyEntries(LIST, {
      kind: "cigar",
      shop: "humidor.hr",
      family: "robusto",
    });
    expect(hits.map((e) => e.name)).toEqual(["Oliva Serie V", "Partagas"]);
    expect(
      matchesBuyFilters(LIST[1], { kind: "cigar", shop: "humidor.hr", family: "robusto" }),
    ).toBe(false);
  });

  it("prepoznaje da je filter aktivan", () => {
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, shop: "humidor.hr" })).toBe(true);
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, kind: "drink" })).toBe(true);
    expect(hasActiveBuyFilters({ ...EMPTY_BUY_FILTERS, family: "toro" })).toBe(true);
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
  it("vrste vitola idu od kratkih prema dugima, samo one prisutne", () => {
    expect(familyCounts(LIST)).toEqual([
      { family: "robusto", count: 2 },
      { family: "toro", count: 1 },
    ]);
  });

  it("ukupno preskače stavke bez cijene", () => {
    expect(buyTotal(LIST)).toBe(100);
  });
});
