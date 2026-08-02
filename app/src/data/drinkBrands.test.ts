// Marke pića su IZVEDENE iz imena (pića nemaju `brand` polje), pa moraju
// ostati u skladu s podacima — inače filter po marki prikazuje marke bez boca
// ili gubi boce koje su u međuvremenu dodane.
import { describe, expect, it } from "vitest";
import { ALL_DRINKS, ALL_DRINK_BRANDS, drinkBrand, drinksByBrand } from "./index";

describe("marke pića", () => {
  // Kava nema proizvođača — "Ristretto", "Cold brew", "Brazil Santos" su
  // priprema i podrijetlo. Namjerno je izvan pojma marke.
  const withBrand = ALL_DRINKS.filter((d) => d.category !== "coffee");

  it("svako piće osim kave ima marku", () => {
    const missing = withBrand.filter((d) => !drinkBrand(d.id)).map((d) => d.id);
    expect(
      missing,
      "Novo piće? Pokreni `python3 scripts/derive-drink-brands.py`.",
    ).toEqual([]);
  });

  it("kava namjerno nema marku", () => {
    const coffee = ALL_DRINKS.filter((d) => d.category === "coffee");
    expect(coffee.length).toBeGreaterThan(0);
    expect(coffee.filter((d) => drinkBrand(d.id)).map((d) => d.id)).toEqual([]);
  });

  it("svaka marka ima barem jednu bocu", () => {
    const empty = ALL_DRINK_BRANDS.filter((b) => drinksByBrand(b).length === 0);
    expect(empty).toEqual([]);
  });

  it("marka nije prazna ni sam broj", () => {
    const bad = ALL_DRINK_BRANDS.filter((b) => !b.trim() || /^[\d\s.,%]+$/.test(b));
    expect(bad).toEqual([]);
  });

  it("boce marke su poredane po kvaliteti pa imenu", () => {
    const brand = ALL_DRINK_BRANDS.find((b) => drinksByBrand(b).length > 2);
    expect(brand).toBeDefined();
    const list = drinksByBrand(brand!);
    for (let i = 1; i < list.length; i++) {
      const a = list[i - 1].qualityScore ?? 0;
      const b = list[i].qualityScore ?? 0;
      expect(a >= b).toBe(true);
    }
  });

  it("zbroj boca po markama pokriva sva ne-kavena pića", () => {
    const total = ALL_DRINK_BRANDS.reduce((n, b) => n + drinksByBrand(b).length, 0);
    expect(total).toBe(withBrand.length);
  });
});
