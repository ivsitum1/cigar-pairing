import { describe, it, expect } from "vitest";
import { scorePairing, pairDrinksForCigar } from "./pairing";
import { occasionKeep, occasionReasons } from "./occasion";
import { WEIGHTS } from "./rules";
import type { Cigar, Drink } from "../types";
import cigarsData from "../data/cigars.json";
import rumsData from "../data/rums.json";

const cigars = cigarsData as Cigar[];
const rums = rumsData as unknown as Drink[];

const byId = <T extends { id: string }>(arr: T[], id: string): T => {
  const found = arr.find((x) => x.id === id);
  if (!found) throw new Error(`missing ${id}`);
  return found;
};

describe("occasion soft-only (par > vrijeme)", () => {
  it("occasionKeep ne reže pool", () => {
    const keep = occasionKeep("evening", 1);
    expect(keep({ body: 1, category: "rum" } as Drink)).toBe(true);
    expect(keep({ body: 5, category: "rum" } as Drink)).toBe(true);
  });

  it("ukupni |occasion delta| < bodyPerStep (ne pregazi body-match)", () => {
    const delta = occasionReasons("morning", {
      cigar: { strength: 1, body: 1 },
      drink: { body: 1, category: "rum", flavorTags: [] },
    }).reduce((s, r) => s + r.score, 0);
    const clash = occasionReasons("morning", {
      cigar: { strength: 1, body: 1 },
      drink: { body: 5, category: "rum", flavorTags: [] },
    }).reduce((s, r) => s + r.score, 0);
    expect(Math.abs(delta)).toBeLessThan(WEIGHTS.bodyPerStep);
    expect(Math.abs(clash)).toBeLessThan(WEIGHTS.bodyPerStep);
    expect(WEIGHTS.occasionFit + WEIGHTS.occasionMild).toBeLessThan(
      WEIGHTS.bodyPerStep,
    );
  });

  it("bolji body-match pobjeđuje occasion preferenciju", () => {
    // blaga cigara: lagani rum (dobar par) vs puni rum (loš par) uvečer
    const macanudo = byId(cigars, "cig-macanudo-cafe");
    const light = rums.find((d) => d.pairable && d.body <= 2)!;
    const full = rums.find((d) => d.pairable && d.body >= 4)!;
    const ranked = pairDrinksForCigar(
      macanudo,
      [light, full],
      undefined,
      "evening",
    );
    expect(ranked[0].item.id).toBe(light.id);
    expect(ranked[0].score).toBeGreaterThan(ranked[1].score);
  });

  it("Ashton Cabinet: top rum uvečer i dalje ≥ 70 (ne hard-filter 41)", () => {
    const cigar = byId(cigars, "cig-ashton-cabinet");
    const ranked = pairDrinksForCigar(
      cigar,
      rums.filter((d) => d.pairable),
      undefined,
      "evening",
    ).filter((r) => r.item.category === "rum");
    expect(ranked[0].score).toBeGreaterThanOrEqual(70);
  });

  it("ista baza: jutro favorizira laganije relativno prema večeri", () => {
    const cigar = byId(cigars, "cig-partagas-serie-d");
    const light = rums.find((d) => d.pairable && d.body === 2)!;
    const fuller = rums.find((d) => d.pairable && d.body === 4)!;
    const mL = scorePairing(cigar, light, undefined, undefined, "morning").score;
    const mF = scorePairing(cigar, fuller, undefined, undefined, "morning").score;
    const eL = scorePairing(cigar, light, undefined, undefined, "evening").score;
    const eF = scorePairing(cigar, fuller, undefined, undefined, "evening").score;
    expect(mL - mF).toBeGreaterThan(eL - eF);
  });
});
