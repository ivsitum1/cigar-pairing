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

describe("curatedPairingOpinion — tri zone (pohvala / null / upozorenje)", () => {
  it("srednja zona → null; niska zona → upozorenje (npr. Doorly 41%)", () => {
    const doorly = byId(rums, "rum-doorly-s-xo-foursquare");
    const macanudo = byId(cigars, "cig-macanudo-cafe");
    const { score, reasons } = scorePairing(macanudo, doorly);
    expect(score).toBeLessThan(WEIGHTS.curatedHintMinScore);
    const op = curatedPairingOpinion(macanudo, doorly, reasons, score);
    if (score <= WEIGHTS.curatedWarnMaxScore) {
      expect(op).not.toBeNull();
      expect(op!.tone).toBe("warning");
      expect(op!.text.hr).toMatch(/Macanudo/);
    } else {
      expect(op).toBeNull();
    }
  });

  it("izraziti promašaj → upozorenje s konkretnim razlogom", () => {
    // najjaca cigara + pjenusac: klasican sudar punoce
    const tabernacle = byId(cigars, "cig-foundation-tabernacle");
    const sparkling = ALL_DRINKS.find((d) => d.style === "sparkling")!;
    const { score, reasons } = scorePairing(tabernacle, sparkling);
    expect(score).toBeLessThanOrEqual(WEIGHTS.curatedWarnMaxScore);
    const op = curatedPairingOpinion(tabernacle, sparkling, reasons, score);
    expect(op).not.toBeNull();
    expect(op!.tone).toBe("warning");
    expect(op!.text.hr.length).toBeGreaterThan(25);
    expect(op!.text.hr).toMatch(/Tabernacle/);
  });

  it("nikad ne čita drink.cigarHint", () => {
    const cigar = CIGARS.find((c) => /san lotano/i.test(c.line))!;
    const ranked = pairDrinksForCigar(cigar, ALL_DRINKS);
    const topRum = ranked.find((r) => r.item.category === "rum")!;
    const drinkWithoutHint = { ...topRum.item, cigarHint: null };
    const drinkWithHint = {
      ...topRum.item,
      cigarHint: {
        hr: "SENTINEL HR cigarHint se ne smije pojaviti",
        en: "SENTINEL EN cigarHint must not appear",
      },
    };

    expect(topRum.score).toBeGreaterThanOrEqual(80);
    const withoutHint = curatedPairingOpinion(cigar, drinkWithoutHint, topRum.reasons, topRum.score);
    const withHint = curatedPairingOpinion(cigar, drinkWithHint, topRum.reasons, topRum.score);

    expect(withHint).toEqual(withoutHint);
    expect(withHint?.text.hr).not.toContain("SENTINEL");
  });

  it("San Lotano + Eminente (85%) → ima kuriranu poruku s imenima", () => {
    const cigar = CIGARS.find((c) => /san lotano/i.test(c.line))!;
    expect(cigar).toBeTruthy();
    const ranked = pairDrinksForCigar(cigar, ALL_DRINKS);
    const rum = ranked.find((r) => r.item.category === "rum")!;
    expect(rum.score).toBeGreaterThanOrEqual(80);
    const op = curatedPairingOpinion(cigar, rum.item, rum.reasons, rum.score);
    expect(op).not.toBeNull();
    expect(op!.tone).toBe("praise");
    expect(op!.text.hr).toMatch(/San Lotano/i);
    expect(op!.text.hr).toMatch(/Eminente/i);
  });

  it("New World top rum/whisky/brandy iznad 80 → svi imaju poruku; gin ispod → null", () => {
    const cigar = byId(cigars, "cig-aj-fernandez-new-world");
    const ranked = pairDrinksForCigar(cigar, ALL_DRINKS);
    for (const cat of ["rum", "whisky", "brandy"] as const) {
      const top = ranked.find((r) => r.item.category === cat)!;
      expect(top.score).toBeGreaterThanOrEqual(80);
      const op = curatedPairingOpinion(cigar, top.item, top.reasons, top.score);
      expect(op, `${cat} ${top.score}%`).not.toBeNull();
      expect(op!.tone).toBe("praise");
      expect(op!.text.hr).toContain(cigar.line);
      expect(op!.text.hr).toContain(top.item.name.split(" ")[0]);
    }
    const gin = ranked.find((r) => r.item.category === "gin");
    if (gin && gin.score < 80) {
      const ginOp = curatedPairingOpinion(cigar, gin.item, gin.reasons, gin.score);
      // srednja zona nema poruku; niska zona nosi upozorenje
      if (gin.score > WEIGHTS.curatedWarnMaxScore) expect(ginOp).toBeNull();
      else expect(ginOp!.tone).toBe("warning");
    }
  });

  it("zone su dosljedne: >=80 jedinstvena pohvala, sredina null, <=45 upozorenje", () => {
    const sampleCigars = CIGARS.filter((c) =>
      /aj fernandez|oliva|arturo fuente|davidoff/i.test(c.brand),
    ).slice(0, 25);
    const drinks = ALL_DRINKS.filter((d) => d.pairable);
    const seen = new Set<string>();

    for (const cigar of sampleCigars) {
      for (const drink of drinks) {
        const { score, reasons } = scorePairing(cigar, drink);
        const op = curatedPairingOpinion(cigar, drink, reasons, score);
        if (score >= WEIGHTS.curatedHintMinScore) {
          expect(op).not.toBeNull();
          expect(op!.tone).toBe("praise");
          expect(op!.text.hr.length).toBeGreaterThan(25);
          expect(seen.has(op!.text.hr)).toBe(false);
          seen.add(op!.text.hr);
        } else if (score <= WEIGHTS.curatedWarnMaxScore) {
          expect(op).not.toBeNull();
          expect(op!.tone).toBe("warning");
          expect(op!.text.hr.length).toBeGreaterThan(25);
        } else {
          expect(op).toBeNull();
        }
      }
    }
  });
});
