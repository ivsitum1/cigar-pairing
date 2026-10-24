// Snaga, tijelo i intenzitet note su tri osi, ne jedan broj prepisan dvaput.
//
// Dok se iz Neptuneova opisa citao jedan broj, `merge-neptune-profiles.py` ga je
// upisivao u snagu i tijelo. Katalog je time tvrdio da cigara koja je jaka mora
// biti i puna, a to nije tocno. Intenzitet note (CigarWorld aroma strength) je
// treci dial — koliko je okus glasan — i ne smije se svesti na tijelo.
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

describe("intenzitet note kao treca os", () => {
  it("svaka linija ima flavorIntensity 1–5", () => {
    for (const c of cigars) {
      expect(c.flavorIntensity, c.id).toBeTypeOf("number");
      expect(Number.isInteger(c.flavorIntensity), c.id).toBe(true);
      expect(c.flavorIntensity!, c.id).toBeGreaterThanOrEqual(1);
      expect(c.flavorIntensity!, c.id).toBeLessThanOrEqual(5);
    }
  });

  it("nije kopija tijela — znatan dio kataloga se razlikuje", () => {
    const split = cigars.filter((c) => c.flavorIntensity !== c.body).length;
    expect(split / cigars.length).toBeGreaterThan(0.2);
  });

  it("nije saturiran na jednoj vrijednosti", () => {
    const counts = [1, 2, 3, 4, 5].map(
      (v) => cigars.filter((c) => c.flavorIntensity === v).length,
    );
    const maxShare = Math.max(...counts) / cigars.length;
    expect(maxShare).toBeLessThan(0.55);
    expect(counts.filter((n) => n > 0).length).toBeGreaterThanOrEqual(4);
  });

  it("dio kataloga nosi shop mjerenje (CigarWorld aroma strength)", () => {
    const shop = cigars.filter((c) => c.flavorIntensityFromShop).length;
    expect(shop).toBeGreaterThan(400);
  });
});
