import { describe, it, expect } from "vitest";
import {
  BUCKETS,
  buffetFive,
  collectionGaps,
  groupWishlistByShop,
  groupWishlistDrinksByCategory,
  segmentPicks,
  wishlistText,
  wishlistTextSections,
} from "./shoppingPicks";
import { DRINKS } from "../data";
import type { Drink, DrinkCategory } from "../types";

const CATS: DrinkCategory[] = [
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
];
const nitko = () => false;

const stubDrink = (id: string, category: DrinkCategory): Drink =>
  ({
    id,
    category,
    name: id,
    style: "blend",
    region: "",
    body: 3,
    sweetness: 3,
    flavorTags: [],
    qualityScore: 7,
    priceEUR: { min: 20, max: 30 },
    shopHR: "test",
    pairable: true,
    serving: { best: "neat" },
    notes: { hr: "", en: "" },
  }) as Drink;

describe("grupiranje liste zelja po trgovini", () => {
  it("grupira, cisti sufikse u zagradi i sortira po trosku", () => {
    const groups = groupWishlistByShop(
      [
        { shop: "allez.hr", price: 40 },
        { shop: "allez.hr (rijetko)", price: 60 },
        { shop: "The Humidor", price: 12 },
        { shop: "", price: 9 },
        { shop: null, price: null },
      ],
      "ostalo",
    );
    expect(groups[0]).toEqual({ shop: "allez.hr", count: 2, total: 100 });
    expect(groups[1]).toEqual({ shop: "The Humidor", count: 1, total: 12 });
    expect(groups[2]).toEqual({ shop: "ostalo", count: 2, total: 9 });
  });
});

describe("grupiranje liste zelja po kategoriji pica", () => {
  it("odvaja vrste pica i ispušta prazne kategorije", () => {
    const groups = groupWishlistDrinksByCategory(
      [
        stubDrink("r1", "rum"),
        stubDrink("w1", "whisky"),
        stubDrink("r2", "rum"),
        stubDrink("g1", "gin"),
      ],
      CATS,
    );
    expect(groups.map((g) => g.category)).toEqual(["rum", "whisky", "gin"]);
    expect(groups[0].drinks.map((d) => d.id)).toEqual(["r1", "r2"]);
    expect(groups[1].drinks.map((d) => d.id)).toEqual(["w1"]);
    expect(groups[2].drinks.map((d) => d.id)).toEqual(["g1"]);
  });
});

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

  it("wishlistTextSections odvaja cigare od vrsta pica", () => {
    const txt = wishlistTextSections([
      {
        title: "Cigare",
        items: [{ name: "Partagas Serie D No.4", price: 12, shop: "The Humidor" }],
      },
      {
        title: "Rum",
        items: [{ name: "Doorly's 12", price: 35, shop: "allez.hr" }],
      },
      {
        title: "Whisky",
        items: [{ name: "Talisker 10", price: 45 }],
      },
      { title: "Gin", items: [] },
    ]);
    expect(txt).toBe(
      [
        "Cigare",
        "• Partagas Serie D No.4 — ~12 € (The Humidor)",
        "",
        "Rum",
        "• Doorly's 12 — ~35 € (allez.hr)",
        "",
        "Whisky",
        "• Talisker 10 — ~45 €",
        "Ukupno: ~92 €",
      ].join("\n"),
    );
  });
});
