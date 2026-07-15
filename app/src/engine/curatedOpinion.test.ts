import { describe, it, expect } from "vitest";
import { scorePairing } from "./pairing";
import { curatedPairingOpinion } from "./curatedOpinion";
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

describe("curatedPairingOpinion", () => {
  const doorly = byId(rums, "rum-doorly-s-xo-foursquare");

  it("ne preporučuje natural wrapper uz Doorly's XO", () => {
    const natural = cigars.find((c) => /\bnatural\b/i.test(c.wrapper));
    expect(natural).toBeTruthy();
    const { reasons } = scorePairing(natural!, doorly);
    const opinion = curatedPairingOpinion(natural!, doorly, reasons);
    expect(opinion?.hr).toMatch(/nije idealan|Habano|San Andrés/i);
    expect(opinion?.en).toMatch(/not ideal|Habano|San Andrés/i);
  });

  it("Habano uz Doorly's XO daje pozitivno mišljenje s imenima para", () => {
    const habano = cigars.find(
      (c) => /habano/i.test(c.wrapper) && scorePairing(c, doorly).score >= WEIGHTS.curatedHintMinScore,
    );
    expect(habano).toBeTruthy();
    const { reasons, score } = scorePairing(habano!, doorly);
    expect(score).toBeGreaterThanOrEqual(WEIGHTS.curatedHintMinScore);
    const opinion = curatedPairingOpinion(habano!, doorly, reasons);
    expect(opinion?.hr).toContain("Doorly");
    expect(opinion?.hr).toMatch(/Habano|tijela|struktur/i);
    expect(opinion?.en).toContain("Doorly");
  });

  it("mišljenje se ne generira ispod praga — app ne koristi legacy cigarHint", () => {
    const macanudo = byId(cigars, "cig-macanudo-cafe");
    const { score } = scorePairing(macanudo, doorly);
    expect(score).toBeLessThan(WEIGHTS.curatedHintMinScore);
    expect(doorly.cigarHint).toBeNull();
  });
});
