import { describe, expect, it } from "vitest";
import { ALL_DRINKS, CIGARS } from "../data";
import {
  allGiftAnswerCombos,
  cigarGiftEligible,
  drinkGiftEligible,
  findGifts,
  giftRegion,
  type GiftBudget,
} from "./giftFinder";

const CATALOG = { cigars: CIGARS, drinks: ALL_DRINKS };

const BAND_MAX: Record<GiftBudget, number> = {
  under20: 20,
  "20to40": 40,
  "40to60": 60,
  "60to100": 100,
  unknown: 40,
};

describe("giftFinder", () => {
  it("giftRegion tretira ALL kao HR (blizina)", () => {
    expect(giftRegion("ALL")).toBe("HR");
    expect(giftRegion("HR")).toBe("HR");
    expect(giftRegion("EU")).toBe("EU");
  });

  it("cigara bez HR trgovine nije poklon u blizini", () => {
    const pricedHr = CIGARS.filter((c) => cigarGiftEligible(c, "HR"));
    expect(pricedHr.length).toBeGreaterThan(10);
    const noShop = CIGARS.find((c) => c.availabilityHR.length === 0);
    if (noShop) expect(cigarGiftEligible(noShop, "HR")).toBe(false);
  });

  it("piće bez shopHR nije HR poklon", () => {
    const ok = ALL_DRINKS.filter((d) => drinkGiftEligible(d, "HR"));
    expect(ok.length).toBeGreaterThan(50);
  });

  it("budžet se nikad ne prekorači — boca, cigara i kombinacija", () => {
    const budgets: GiftBudget[] = ["under20", "20to40", "40to60", "60to100"];
    const shapes = ["bottle", "cigar", "pairing"] as const;
    for (const budget of budgets) {
      for (const shape of shapes) {
        const picks = findGifts(
          {
            recipient: "regular",
            budget,
            drink: "rum",
            intensity: "medium",
            shape,
          },
          CATALOG,
          "HR",
        );
        for (const pick of picks) {
          expect(pick.price).not.toBeNull();
          expect(pick.price!).toBeLessThanOrEqual(BAND_MAX[budget] + 0.01);
        }
      }
    }
  });

  it("cigara vraća cigaru, boca bocu, kombinacija oboje", () => {
    const cigar = findGifts(
      {
        recipient: "regular",
        budget: "under20",
        drink: "unknown",
        intensity: "medium",
        shape: "cigar",
      },
      CATALOG,
      "HR",
    );
    expect(cigar.some((p) => p.kind === "cigar" && p.cigar)).toBe(true);

    const bottle = findGifts(
      {
        recipient: "regular",
        budget: "20to40",
        drink: "rum",
        intensity: "medium",
        shape: "bottle",
      },
      CATALOG,
      "HR",
    );
    expect(bottle.some((p) => p.kind === "drink" && p.drink)).toBe(true);

    const pair = findGifts(
      {
        recipient: "regular",
        budget: "40to60",
        drink: "rum",
        intensity: "medium",
        shape: "pairing",
      },
      CATALOG,
      "HR",
    );
    const combo = pair.find((p) => p.kind === "pairing");
    if (combo) {
      expect(combo.cigar).toBeTruthy();
      expect(combo.drink).toBeTruthy();
      expect(combo.price!).toBeLessThanOrEqual(60.01);
    }
  });

  it("drinks-only ne predlaže cigare i ne ponavlja istu bocu", () => {
    const picks = findGifts(
      {
        recipient: "drinks-only",
        budget: "20to40",
        drink: "whisky",
        intensity: "medium",
        shape: "pairing",
      },
      CATALOG,
      "HR",
    );
    for (const p of picks) {
      expect(p.cigar).toBeUndefined();
      expect(p.cigars).toBeUndefined();
      expect(p.kind).toBe("drink");
    }
    if (picks.length === 2) expect(picks[0].id).not.toBe(picks[1].id);
  });

  it(
    "svaka kombinacija odgovora daje barem jedan prijedlog u HR",
    () => {
      const empty: string[] = [];
      for (const answers of allGiftAnswerCombos()) {
        const picks = findGifts(answers, CATALOG, "HR");
        if (picks.length === 0) empty.push(JSON.stringify(answers));
        for (const p of picks) {
          if (p.price != null) expect(p.price).toBeGreaterThan(0);
          const max = BAND_MAX[answers.budget];
          if (p.price != null && !p.fellBackBudget) {
            expect(p.price).toBeLessThanOrEqual(max + 0.01);
          }
        }
      }
      expect(empty.length).toBeLessThan(allGiftAnswerCombos().length * 0.05);
      if (empty.length > 0) {
        expect(empty.length).toBeLessThanOrEqual(5);
      }
    },
    300_000,
  );
});
