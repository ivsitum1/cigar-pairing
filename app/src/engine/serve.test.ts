import { describe, it, expect } from "vitest";
import { applyServe, SERVE_EFFECT } from "./serve";
import { scorePairing } from "./pairing";
import type { Cigar, Drink } from "../types";

// minimalni fixturei (samo polja koja engine čita)
const mkDrink = (over: Partial<Drink> = {}): Drink => ({
  id: "d",
  category: "rum",
  name: "Test Drink",
  style: "demerara",
  region: "—",
  body: 3,
  sweetness: 2,
  flavorTags: [],
  qualityScore: 7,
  priceEUR: null,
  shopHR: "",
  pairable: true,
  serving: { neat: 3, water: 2, rocks: 1, best: "Cisto" },
  notes: { hr: "", en: "" },
  ...over,
});

const mkCigar = (over: Partial<Cigar> = {}): Cigar => ({
  id: "c",
  brand: "Test",
  line: "Line",
  vitola: "Robusto",
  format: "50 x 127mm",
  country: "Kuba",
  wrapper: "connecticut",
  strength: 3,
  body: 3,
  flavorTags: [],
  smokeTimeMin: 45,
  priceEUR: null,
  vitolas: [],
  markets: ["HR"],
  availabilityHR: [],
  notes: { hr: "", en: "" },
  ...over,
});

describe("applyServe", () => {
  it("neat/undefined ne mijenja piće i množitelji su neutralni", () => {
    const d = mkDrink({ body: 3, sweetness: 2 });
    for (const s of [undefined, "neat"] as const) {
      const { drink, effect, reason } = applyServe(d, s);
      expect(drink.body).toBe(3);
      expect(drink.sweetness).toBe(2);
      expect(effect.aromaFactor).toBe(1);
      expect(effect.tameFactor).toBe(1);
      expect(reason).toBeUndefined();
    }
  });

  it("voda OTVARA aromu i umiruje žestinu, a tijelo NE mijenja (§0.5)", () => {
    const d = mkDrink({ body: 4, sweetness: 2 });
    const { drink, effect, reason } = applyServe(d, "water");
    expect(SERVE_EFFECT.water.bodyDelta).toBe(0);
    expect(drink.body).toBe(4); // tijelo netaknuto
    expect(effect.aromaFactor).toBeGreaterThan(1);
    expect(effect.tameFactor).toBeLessThan(1);
    expect(reason?.rule).toBe("serve-water");
  });

  it("led ZATVARA aromu i prigušuje slatkoću", () => {
    const d = mkDrink({ body: 4, sweetness: 3 });
    const { drink, effect } = applyServe(d, "rocks");
    expect(effect.aromaFactor).toBeLessThan(1);
    expect(drink.sweetness).toBeLessThan(3);
  });

  it("cola diže slatkoću i klema na 5", () => {
    const d = mkDrink({ sweetness: 4 });
    const { drink } = applyServe(d, "cola");
    expect(drink.sweetness).toBe(5); // 4 + 1.3 -> clamp 5
  });

  it("highball klema tijelo na >= 1", () => {
    const d = mkDrink({ body: 1 });
    const { drink } = applyServe(d, "highball");
    expect(drink.body).toBeGreaterThanOrEqual(1);
  });
});

describe("scorePairing sa serve", () => {
  it("regresija: serve=undefined identičan kao bez argumenta", () => {
    const c = mkCigar({ flavorTags: ["kakao"], strength: 4, body: 4 });
    const d = mkDrink({ flavorTags: ["kakao"], body: 4, sweetness: 3 });
    expect(scorePairing(c, d, undefined, undefined).score).toBe(
      scorePairing(c, d).score,
    );
  });

  it("žestina: voda smanjuje kaznu jakog pića prema blagoj cigari (score ↑)", () => {
    const mild = mkCigar({ strength: 2, body: 2 });
    const strong = mkDrink({ body: 5, sweetness: 1, flavorTags: ["overproof"], style: "navy-strength" });
    const neat = scorePairing(mild, strong, undefined, "neat").score;
    const water = scorePairing(mild, strong, undefined, "water").score;
    expect(water).toBeGreaterThanOrEqual(neat);
  });

  it("aroma: voda diže score na zajedničkim notama, led ga spušta", () => {
    const c = mkCigar({ flavorTags: ["kakao", "kava"], strength: 3, body: 3 });
    const d = mkDrink({ flavorTags: ["kakao", "kava"], body: 3, sweetness: 1 });
    const neat = scorePairing(c, d, undefined, "neat").score;
    const water = scorePairing(c, d, undefined, "water").score;
    const rocks = scorePairing(c, d, undefined, "rocks").score;
    expect(water).toBeGreaterThan(neat);
    expect(rocks).toBeLessThan(neat);
  });

  it("serve dodaje objašnjenje u reasons", () => {
    const c = mkCigar();
    const d = mkDrink();
    const { reasons } = scorePairing(c, d, undefined, "water");
    expect(reasons.some((r) => r.rule === "serve-water")).toBe(true);
  });
});
