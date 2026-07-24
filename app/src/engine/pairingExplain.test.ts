import { describe, it, expect } from "vitest";
import { scorePairing } from "./pairing";
import { pairingBlurb, pairingNarrative } from "./pairingExplain";
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

describe("pairingBlurb / pairingNarrative", () => {
  it("blurb is non-empty HR+EN for a real pair", () => {
    const cigar = byId(cigars, "cig-macanudo-cafe");
    const drink = byId(rums, "rum-doorly-s-xo-foursquare");
    const { score, reasons } = scorePairing(cigar, drink);
    const b = pairingBlurb(cigar, drink, reasons, score);
    expect(b.hr.length).toBeGreaterThan(20);
    expect(b.en.length).toBeGreaterThan(20);
  });

  it("narrative is longer than blurb for a strong-ish match", () => {
    const cigar = byId(cigars, "cig-macanudo-cafe");
    const drink = byId(rums, "rum-doorly-s-xo-foursquare");
    const { score, reasons } = scorePairing(cigar, drink);
    const b = pairingBlurb(cigar, drink, reasons, score);
    const n = pairingNarrative(cigar, drink, reasons, score);
    expect(n.hr.length).toBeGreaterThan(b.hr.length);
    expect(n.en.length).toBeGreaterThan(b.en.length);
  });

  it("EN narrative lokalizira zajedničke note (bez sirovih hrvatskih tagova)", () => {
    // Regres: "Shared notes: kakao" u engleskom tekstu.
    const LEAK = /Shared notes:[^.]*\b(kakao|karamela|zacini|vanilija|hrast|voce|suho-voce)\b/;
    for (const cigar of cigars.slice(0, 30)) {
      for (const drink of rums) {
        const { score, reasons } = scorePairing(cigar, drink);
        const n = pairingNarrative(cigar, drink, reasons, score);
        expect(n.en, `${cigar.brand} ${cigar.line} + ${drink.name}`).not.toMatch(LEAK);
      }
    }
  });

  it("handles empty reasons without throwing", () => {
    const cigar = byId(cigars, "cig-macanudo-cafe");
    const drink = byId(rums, "rum-doorly-s-xo-foursquare");
    const b = pairingBlurb(cigar, drink, [], 50);
    const n = pairingNarrative(cigar, drink, [], 50);
    expect(b.hr.length).toBeGreaterThan(10);
    expect(n.hr.length).toBeGreaterThan(10);
  });
});
