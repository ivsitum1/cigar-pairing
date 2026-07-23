import { describe, it, expect } from "vitest";
import { applyGeometry, parseGeometry, GEOMETRY } from "./vitolaGeometry";
import { scorePairing } from "./pairing";
import type { Cigar, Drink, Vitola } from "../types";

const vitola = (partial: Partial<Vitola> & Pick<Vitola, "name">): Vitola => ({
  format: null,
  smokeTimeMin: null,
  priceEUR: null,
  url: null,
  ...partial,
});

const baseCigar = (overrides: Partial<Cigar> = {}): Cigar => ({
  id: "cig-test",
  brand: "Test",
  line: "Line",
  vitola: "Robusto",
  format: "",
  country: "NI",
  wrapper: "Habano",
  strength: 4,
  body: 3,
  flavorTags: ["zacini"],
  smokeTimeMin: 55,
  priceEUR: null,
  vitolas: [],
  markets: [],
  availabilityHR: [],
  notes: { hr: "", en: "" },
  ...overrides,
});

const baseDrink = (overrides: Partial<Drink> = {}): Drink => ({
  id: "drink-test",
  category: "rum",
  name: "Test Drink",
  style: "jamaica",
  region: "JM",
  body: 3,
  sweetness: 2,
  flavorTags: ["zacini"],
  qualityScore: 7,
  priceEUR: null,
  shopHR: "",
  pairable: true,
  serving: { best: "neat" },
  notes: { hr: "", en: "" },
  ...overrides,
});

describe("parseGeometry", () => {
  it("cita ring/lengthMM iz odabrane vitole", () => {
    const cigar = baseCigar({
      vitolas: [vitola({ name: "Lancero", ring: 38, lengthMM: 190 })],
    });
    expect(parseGeometry(cigar)).toEqual({ ring: 38, len: 190 });
  });

  it("fallback na regex iz format stringa kad vitola nema dimenzije", () => {
    const cigar = baseCigar({
      format: "42 x 152mm",
      vitolas: [vitola({ name: "Corona" })],
    });
    expect(parseGeometry(cigar)).toEqual({ ring: 42, len: 152 });
  });

  it("na razini linije (vise vitola) koristi format, ne proizvoljni vitolas[0]", () => {
    const cigar = baseCigar({
      format: "50 x 127mm",
      vitolas: [
        vitola({ name: "Petit Corona", ring: 36, lengthMM: 102 }),
        vitola({ name: "Robusto", ring: 50, lengthMM: 127 }),
      ],
    });
    expect(parseGeometry(cigar)).toEqual({ ring: 50, len: 127 });
  });

  it("prihvaca × separator i razmake", () => {
    const cigar = baseCigar({ format: "50×127 mm" });
    expect(parseGeometry(cigar)).toEqual({ ring: 50, len: 127 });
  });

  it("vraca null kad nema ni vitole ni formata", () => {
    expect(parseGeometry(baseCigar({ format: "", vitolas: [] }))).toEqual({
      ring: null,
      len: null,
    });
  });
});

describe("applyGeometry", () => {
  it("tanak ring: visi strength/body, wrapperForwardBonus 5, vitola-thin reason", () => {
    const cigar = baseCigar({
      strength: 3,
      body: 3,
      vitolas: [vitola({ name: "Lancero", ring: 38, lengthMM: 140 })],
    });
    const { cigar: eff, wrapperForwardBonus, reason } = applyGeometry(cigar);
    expect(eff.strength).toBeGreaterThan(cigar.strength);
    expect(eff.strength).toBeCloseTo(3 + GEOMETRY.thin.strengthDelta);
    expect(eff.body).toBeCloseTo(3 + GEOMETRY.thin.bodyDelta);
    expect(wrapperForwardBonus).toBe(5);
    expect(reason?.rule).toBe("vitola-thin");
    expect(reason?.text.hr).toContain("38");
    expect(reason?.text.en).toContain("38");
  });

  it("debeo ring: nizi strength, bonus 0, vitola-thick reason", () => {
    const cigar = baseCigar({
      strength: 4,
      body: 3,
      vitolas: [vitola({ name: "Gordo", ring: 60, lengthMM: 150 })],
    });
    const { cigar: eff, wrapperForwardBonus, reason } = applyGeometry(cigar);
    expect(eff.strength).toBeLessThan(cigar.strength);
    expect(eff.strength).toBeCloseTo(4 + GEOMETRY.thick.strengthDelta);
    expect(eff.body).toBeCloseTo(3 + GEOMETRY.thick.bodyDelta);
    expect(wrapperForwardBonus).toBe(0);
    expect(reason?.rule).toBe("vitola-thick");
  });

  it("nepoznata geometrija: cigar netaknut, bonus 0, bez reasona", () => {
    const cigar = baseCigar({ format: "", vitolas: [] });
    const result = applyGeometry(cigar);
    expect(result.cigar).toBe(cigar);
    expect(result.wrapperForwardBonus).toBe(0);
    expect(result.reason).toBeUndefined();
  });

  it("klema strength/body u [1, 5]", () => {
    const hot = applyGeometry(
      baseCigar({
        strength: 5,
        body: 5,
        vitolas: [vitola({ name: "Panetela", ring: 36, lengthMM: 140 })],
      }),
    );
    expect(hot.cigar.strength).toBe(5);
    expect(hot.cigar.body).toBe(5);

    const cool = applyGeometry(
      baseCigar({
        strength: 1,
        body: 1,
        vitolas: [vitola({ name: "Gordo", ring: 60, lengthMM: 150 })],
      }),
    );
    expect(cool.cigar.strength).toBe(1);
    expect(cool.cigar.body).toBe(1);
  });

  it("duga cigara blago glaca strength (uz ring)", () => {
    const short = applyGeometry(
      baseCigar({
        strength: 4,
        vitolas: [vitola({ name: "Corona", ring: 50, lengthMM: 140 })],
      }),
    );
    const long = applyGeometry(
      baseCigar({
        strength: 4,
        vitolas: [vitola({ name: "Churchill", ring: 50, lengthMM: 178 })],
      }),
    );
    expect(short.cigar.strength).toBe(4);
    expect(long.cigar.strength).toBeCloseTo(4 + GEOMETRY.longSmoothStrengthDelta);
  });
});

describe("scorePairing + geometrija", () => {
  it("ista linija: tanka vitola ima vecu overwhelm kaznu uz delikatno pice", () => {
    const delicate = baseDrink({ body: 2, sweetness: 1, flavorTags: ["citrus"] });
    const thin = baseCigar({
      strength: 4,
      body: 3,
      flavorTags: ["zemljano"],
      wrapper: "Connecticut",
      vitolas: [vitola({ name: "Lancero", ring: 38, lengthMM: 140 })],
    });
    const thick = baseCigar({
      ...thin,
      vitolas: [vitola({ name: "Gordo", ring: 60, lengthMM: 150 })],
    });
    const thinScore = scorePairing(thin, delicate);
    const thickScore = scorePairing(thick, delicate);
    expect(thinScore.reasons.some((r) => r.rule === "strength-overwhelm")).toBe(true);
    expect(thickScore.reasons.some((r) => r.rule === "strength-overwhelm")).toBe(false);
    expect(thinScore.score).toBeLessThan(thickScore.score);
    expect(thinScore.reasons.some((r) => r.rule === "vitola-thin")).toBe(true);
    expect(thickScore.reasons.some((r) => r.rule === "vitola-thick")).toBe(true);
  });

  it("tanka vitola ima veci wrapper-afinitet uz zacinjeno pice", () => {
    const spicy = baseDrink({
      body: 3,
      style: "jamaica",
      flavorTags: ["zacini", "dim"],
    });
    const thin = baseCigar({
      strength: 3,
      body: 3,
      wrapper: "Habano",
      flavorTags: ["zemljano"],
      vitolas: [vitola({ name: "Lancero", ring: 38, lengthMM: 140 })],
    });
    const thick = baseCigar({
      ...thin,
      vitolas: [vitola({ name: "Gordo", ring: 60, lengthMM: 150 })],
    });
    const thinResult = scorePairing(thin, spicy);
    const thickResult = scorePairing(thick, spicy);
    const thinWrap = thinResult.reasons.find((r) => r.rule === "wrapper-affinity");
    const thickWrap = thickResult.reasons.find((r) => r.rule === "wrapper-affinity");
    expect(thinWrap).toBeDefined();
    expect(thickWrap).toBeDefined();
    expect(thinWrap!.score).toBeGreaterThan(thickWrap!.score);
    expect(thinResult.score).toBeGreaterThan(thickResult.score);
  });

  it("regresija: cigara bez vitolas/format daje isti score kao prije geometrije", () => {
    const cigar = baseCigar({ format: "", vitolas: [] });
    const drink = baseDrink({ body: 3, flavorTags: ["zacini"] });
    const { score, reasons } = scorePairing(cigar, drink);
    expect(reasons.every((r) => !r.rule.startsWith("vitola-"))).toBe(true);
    // baseline bez geometrije: strength 4, body 3, shared zacini, wrapper habano+jamaica
    expect(score).toBeGreaterThan(0);
    expect(applyGeometry(cigar).wrapperForwardBonus).toBe(0);
  });
});
