import { describe, it, expect } from "vitest";
import { scorePairing, pairDrinksForCigar } from "./pairing";
import { curatedPairingOpinion } from "./curatedOpinion";
import { WEIGHTS } from "./rules";
import { CIGARS, ALL_DRINKS } from "../data";
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

describe("curatedPairingOpinion — strogo pravilo 80%", () => {
  it("ispod 80% → null (npr. Doorly 41%)", () => {
    const doorly = byId(rums, "rum-doorly-s-xo-foursquare");
    const macanudo = byId(cigars, "cig-macanudo-cafe");
    const { score, reasons } = scorePairing(macanudo, doorly);
    expect(score).toBeLessThan(WEIGHTS.curatedHintMinScore);
    expect(curatedPairingOpinion(macanudo, doorly, reasons, score)).toBeNull();
  });

  it("nikad ne čita drink.cigarHint", () => {
    for (const d of ALL_DRINKS.slice(0, 50)) {
      expect(d.cigarHint == null || d.cigarHint === null).toBe(true);
    }
  });

  it("San Lotano + Eminente (85%) → ima kuriranu poruku s imenima", () => {
    const cigar = CIGARS.find((c) => /san lotano/i.test(c.line))!;
    expect(cigar).toBeTruthy();
    const ranked = pairDrinksForCigar(cigar, ALL_DRINKS);
    const rum = ranked.find((r) => r.item.category === "rum")!;
    expect(rum.score).toBeGreaterThanOrEqual(80);
    const op = curatedPairingOpinion(cigar, rum.item, rum.reasons, rum.score);
    expect(op).not.toBeNull();
    expect(op!.hr).toMatch(/San Lotano/i);
    expect(op!.hr).toMatch(/Eminente/i);
  });

  it("New World top rum/whisky/brandy iznad 80 → svi imaju poruku; gin ispod → null", () => {
    const cigar = byId(cigars, "cig-aj-fernandez-new-world");
    const ranked = pairDrinksForCigar(cigar, ALL_DRINKS);
    for (const cat of ["rum", "whisky", "brandy"] as const) {
      const top = ranked.find((r) => r.item.category === cat)!;
      expect(top.score).toBeGreaterThanOrEqual(80);
      const op = curatedPairingOpinion(cigar, top.item, top.reasons, top.score);
      expect(op, `${cat} ${top.score}%`).not.toBeNull();
      expect(op!.hr).toContain(cigar.line);
      expect(op!.hr).toContain(top.item.name.split(" ")[0]);
    }
    const gin = ranked.find((r) => r.item.category === "gin");
    if (gin && gin.score < 80) {
      expect(curatedPairingOpinion(cigar, gin.item, gin.reasons, gin.score)).toBeNull();
    }
  });

  it("svaki par >= 80 ima jedinstvenu ne-praznu poruku", () => {
    const sampleCigars = CIGARS.filter((c) =>
      /aj fernandez|oliva|arturo fuente|davidoff/i.test(c.brand),
    ).slice(0, 25);
    const drinks = ALL_DRINKS.filter((d) => d.pairable);
    const seen = new Set<string>();

    for (const cigar of sampleCigars) {
      for (const drink of drinks) {
        const { score, reasons } = scorePairing(cigar, drink);
        const op = curatedPairingOpinion(cigar, drink, reasons, score);
        if (score < WEIGHTS.curatedHintMinScore) {
          expect(op).toBeNull();
        } else {
          expect(op).not.toBeNull();
          expect(op!.hr.length).toBeGreaterThan(25);
          expect(seen.has(op!.hr)).toBe(false);
          seen.add(op!.hr);
        }
      }
    }
  });
});
