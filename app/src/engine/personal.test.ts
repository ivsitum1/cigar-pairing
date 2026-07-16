import { describe, it, expect } from "vitest";
import { buildPrefs, personalBrandReason, personalStyleReason } from "./personal";
import { scorePairing } from "./pairing";
import { WEIGHTS } from "./rules";
import type { Cigar, Drink } from "../types";

const cigar = (over: Partial<Cigar> = {}): Cigar => ({
  id: "c1",
  brand: "Padrón",
  line: "1964",
  vitola: "Exclusivo",
  format: "50 x 127mm",
  country: "Nikaragva",
  wrapper: "Maduro",
  strength: 4,
  body: 4,
  flavorTags: ["kakao", "kava"],
  smokeTimeMin: 60,
  priceEUR: 20,
  vitolas: [],
  markets: ["HR"],
  availabilityHR: [],
  notes: { hr: "", en: "" },
  ...over,
});

const drink = (over: Partial<Drink> = {}): Drink => ({
  id: "d1",
  category: "rum",
  name: "Test Rum",
  style: "demerara",
  region: "Gvajana",
  body: 4,
  sweetness: 3,
  flavorTags: ["melasa", "kava"],
  qualityScore: 8,
  priceEUR: { min: 40, max: 50 },
  shopHR: "",
  pairable: true,
  serving: { best: "neat" },
  notes: { hr: "", en: "" },
  ...over,
});

describe("personalizacija iz dnevnika", () => {
  it("bez ocjena nema nudgea", () => {
    const prefs = buildPrefs([{ rating: null, drinkStyle: "demerara" }]);
    expect(prefs.entries).toBe(0);
    expect(personalStyleReason(prefs, "demerara")).toBeNull();
  });

  it("visoke ocjene stila daju pozitivan nudge, niske negativan", () => {
    const prefs = buildPrefs([
      { rating: 10, drinkStyle: "demerara", cigarBrand: "Padrón" },
      { rating: 9, drinkStyle: "demerara", cigarBrand: "Padrón" },
      { rating: 2, drinkStyle: "jamaica", cigarBrand: "Macanudo" },
    ]);
    const pos = personalStyleReason(prefs, "demerara");
    expect(pos!.score).toBeGreaterThan(0);
    const neg = personalStyleReason(prefs, "jamaica");
    expect(neg!.score).toBeLessThan(0);
    expect(personalStyleReason(prefs, "bourbon")).toBeNull();
    const brand = personalBrandReason(prefs, "Padrón");
    expect(brand!.score).toBeGreaterThan(0);
  });

  it("nudge je ogranicen na WEIGHTS.personal po smjeru", () => {
    const prefs = buildPrefs(
      Array.from({ length: 20 }, () => ({ rating: 10, drinkStyle: "demerara" })),
    );
    const r = personalStyleReason(prefs, "demerara");
    expect(Math.abs(r!.score)).toBeLessThanOrEqual(WEIGHTS.personal);
  });

  it("scorePairing s prefs dodaje personal razloge i mijenja score", () => {
    const prefs = buildPrefs([
      { rating: 10, drinkStyle: "demerara", cigarBrand: "Padrón" },
      { rating: 10, drinkStyle: "demerara", cigarBrand: "Padrón" },
    ]);
    const base = scorePairing(cigar(), drink());
    const withPrefs = scorePairing(cigar(), drink(), prefs);
    expect(withPrefs.score).toBeGreaterThan(base.score);
    const rules = withPrefs.reasons.map((r) => r.rule);
    expect(rules).toContain("personal-style");
    expect(rules).toContain("personal-brand");
  });

  it("jedna usamljena ocjena vuce slabije od ponovljenih (shrinkage)", () => {
    const one = buildPrefs([{ rating: 10, drinkStyle: "demerara" }]);
    const three = buildPrefs(
      Array.from({ length: 3 }, () => ({ rating: 10, drinkStyle: "demerara" })),
    );
    expect(one.drinkStyle["demerara"]).toBeLessThan(three.drinkStyle["demerara"]);
  });
});
