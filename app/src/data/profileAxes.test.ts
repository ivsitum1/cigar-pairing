// Snaga i tijelo su dvije osi, ne jedan broj prepisan dvaput.
//
// Dok se iz Neptuneova opisa citao jedan broj, `merge-neptune-profiles.py` ga je
// upisivao u oba polja (`cigar["body"] = strength_raw`). Katalog je time tvrdio
// da cigara koja je jaka mora biti i puna, a to nije tocno: Connecticut zna biti
// pun a blag, corojo jak a suh. Pairing tijelo i snagu vaze odvojeno, pa je ta
// kopija gasila jednu cijelu dimenziju.
//
// Ovi testovi ne propisuju pojedinacne vrijednosti — cuvaju da osi ostanu
// razdvojene i da nijedna ne ode u nemoguc raspon.
import { describe, expect, it } from "vitest";
import cigarsData from "./cigars.json";
import type { Cigar } from "../types";

const cigars = cigarsData as Cigar[];

describe("snaga i tijelo kao dvije osi", () => {
  it("znatan dio kataloga ima tijelo razlicito od snage", () => {
    const split = cigars.filter((c) => c.strength !== c.body).length;
    expect(split / cigars.length).toBeGreaterThan(0.25);
  });

  it("obje osi ostaju u 1–5 i nijedna ne nedostaje", () => {
    for (const c of cigars) {
      expect(Number.isInteger(c.strength), c.id).toBe(true);
      expect(Number.isInteger(c.body), c.id).toBe(true);
      expect(c.strength, c.id).toBeGreaterThanOrEqual(1);
      expect(c.strength, c.id).toBeLessThanOrEqual(5);
      expect(c.body, c.id).toBeGreaterThanOrEqual(1);
      expect(c.body, c.id).toBeLessThanOrEqual(5);
    }
  });

  it("osi se ne razilaze vise nego sto je fizicki smisleno", () => {
    // Razmak od dvije stepenice je stvaran (pun a blag Connecticut); tri nije —
    // to bi znacilo gresku u citanju, ne cigaru.
    const wild = cigars.filter((c) => Math.abs(c.strength - c.body) > 2);
    expect(wild.map((c) => c.id)).toEqual([]);
  });

  it("obje strane razmaka postoje — nije samo jedan smjer", () => {
    const fuller = cigars.filter((c) => c.body > c.strength).length;
    const stronger = cigars.filter((c) => c.strength > c.body).length;
    expect(fuller).toBeGreaterThan(50);
    expect(stronger).toBeGreaterThan(50);
  });
});
