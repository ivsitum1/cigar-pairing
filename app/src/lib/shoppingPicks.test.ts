import { describe, it, expect } from "vitest";
import { BUCKETS, buffetFive, collectionGaps, segmentPicks, wishlistText } from "./shoppingPicks";
import { DRINKS } from "../data";
import type { DrinkCategory } from "../types";

const CATS: DrinkCategory[] = ["rum", "whisky", "brandy", "gin", "wine"];
const nitko = () => false;

describe("shopping picks", () => {
  it("buffet petorka: 5 razlicitih boca po kategoriji, po jedna iz svakog segmenta", () => {
    for (const cat of CATS) {
      const picks = buffetFive(cat, DRINKS[cat], nitko);
      expect(picks.length, cat).toBe(5);
      expect(new Set(picks.map((p) => p.drink.id)).size, cat).toBe(5);
      expect(new Set(picks.map((p) => p.bucket.id)).size, cat).toBe(5);
      for (const p of picks) {
        expect(p.bucket.styles, `${cat}: ${p.drink.name}`).toContain(p.drink.style);
      }
    }
  });

  it("buffet preskace boce koje vec imam", () => {
    const first = buffetFive("rum", DRINKS.rum, nitko)[0].drink;
    const again = buffetFive("rum", DRINKS.rum, (id) => id === first.id);
    expect(again.map((p) => p.drink.id)).not.toContain(first.id);
  });

  it("segmentPicks vraca tri razlicite preporuke; budget je <= 30 EUR", () => {
    for (const cat of CATS) {
      const { top, value, budget } = segmentPicks(DRINKS[cat], nitko);
      expect(top, cat).toBeTruthy();
      expect(value, cat).toBeTruthy();
      const ids = [top?.id, value?.id, budget?.id].filter(Boolean);
      expect(new Set(ids).size, cat).toBe(ids.length);
      if (budget) expect(budget.priceEUR!.min, cat).toBeLessThanOrEqual(30);
    }
  });

  it("svaki pairable stil u podacima pripada nekom bucketu (nista ne ispada)", () => {
    for (const cat of CATS) {
      const covered = new Set(BUCKETS[cat]!.flatMap((b) => b.styles));
      for (const d of DRINKS[cat]) {
        if (!d.pairable) continue;
        expect(covered.has(d.style), `${cat}: ${d.name} (${d.style})`).toBe(true);
      }
    }
  });

  it("rupe u kolekciji: bez icega = svi segmenti; posjedovanje zatvara segment", () => {
    const all = collectionGaps("rum", DRINKS.rum, nitko);
    expect(all.length).toBe(5);
    const jamajka = DRINKS.rum.find((d) => d.style === "jamaica")!;
    const after = collectionGaps("rum", DRINKS.rum, (id) => id === jamajka.id);
    expect(after.length).toBe(4);
    expect(after.map((g) => g.bucket.id)).not.toContain("jamaica");
  });

  it("wishlistText sadrzi stavke i ukupno", () => {
    const txt = wishlistText([
      { name: "Talisker 10", price: 45, shop: "Vrutak" },
      { name: "Dingač", price: 30 },
    ]);
    expect(txt).toContain("Talisker 10");
    expect(txt).toContain("(Vrutak)");
    expect(txt).toContain("Ukupno: ~75 €");
  });
});
