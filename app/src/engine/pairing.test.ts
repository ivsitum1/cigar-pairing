import { describe, it, expect } from "vitest";
import { scorePairing, pairCigarsForDrink, pairDrinksForCigar } from "./pairing";
import type { Cigar, Drink } from "../types";
import cigarsData from "../data/cigars.json";
import rumsData from "../data/rums.json";
import coffeesData from "../data/coffees.json";
import winesData from "../data/wines.json";

const cigars = cigarsData as Cigar[];
const rums = rumsData as unknown as Drink[];
const coffees = coffeesData as unknown as Drink[];
const wines = winesData as unknown as Drink[];

const byId = <T extends { id: string }>(arr: T[], id: string): T => {
  const found = arr.find((x) => x.id === id);
  if (!found) throw new Error(`missing ${id}`);
  return found;
};

// Referentni parovi iz Excel sheeta "Serviranje + Cigare"
describe("pairing engine — poznati parovi iz Excela", () => {
  it("Hampden (esterski, puno tijelo) preferira jaku/punu cigaru nad blagom", () => {
    const hampden = byId(rums, "rum-hampden-estate-8");
    const partagas = byId(cigars, "cig-partagas-serie-d");
    const fonseca = byId(cigars, "cig-fonseca-delicias");
    expect(scorePairing(partagas, hampden).score).toBeGreaterThan(
      scorePairing(fonseca, hampden).score,
    );
  });

  it("agricole (travnat, lagan) preferira laganu cigaru nad punom", () => {
    const clement = byId(rums, "rum-clement-vsop-neisson-agricole");
    const macanudo = byId(cigars, "cig-macanudo-cafe"); // 1/1, blag
    const antano = byId(cigars, "cig-joya-de-nicaragua-antano"); // 5/5, pun
    expect(scorePairing(macanudo, clement).score).toBeGreaterThan(
      scorePairing(antano, clement).score,
    );
  });

  it("dosladjeni rum + puna maduro cigara dobiva kontrast bonus (slatkoca presijece gorcinu)", () => {
    const onyx = byId(rums, "rum-barcelo-imperial-onyx");
    const padronMaduro = byId(cigars, "cig-padron-1964-anniversary"); // Maduro wrapper, body 4
    const { reasons } = scorePairing(padronMaduro, onyx);
    expect(reasons.some((r) => r.rule === "contrast-sweet-maduro")).toBe(true);
  });

  it("tamni espresso preferira maduro nad blagim Connecticutom", () => {
    const espresso = byId(coffees, "cf-espresso-italian-dark");
    const padronMaduro = byId(cigars, "cig-padron-1964-anniversary"); // Maduro, body 4
    const macanudo = byId(cigars, "cig-macanudo-cafe"); // Connecticut, body 1
    expect(scorePairing(padronMaduro, espresso).score).toBeGreaterThan(
      scorePairing(macanudo, espresso).score,
    );
  });

  it("vino po principu punoce: puna maduro cigara preferira porto/PX nad proseccom", () => {
    const padronMaduro = byId(cigars, "cig-padron-1964-anniversary"); // Maduro, body 4
    const px = byId(wines, "wine-lustau-px"); // body 5, sweetness 5
    const lbv = byId(wines, "wine-taylors-lbv"); // body 4, sweetness 4
    const prosecco = byId(wines, "wine-prosecco-docg"); // body 1
    expect(scorePairing(padronMaduro, px).score).toBeGreaterThan(
      scorePairing(padronMaduro, prosecco).score,
    );
    expect(scorePairing(padronMaduro, lbv).score).toBeGreaterThan(
      scorePairing(padronMaduro, prosecco).score,
    );
    // slatki porto uz punu maduro cigaru dobiva klasicni kontrast bonus
    const { reasons } = scorePairing(padronMaduro, lbv);
    expect(reasons.some((r) => r.rule === "contrast-sweet-maduro")).toBe(true);
  });

  it("vino po principu punoce: blaga Connecticut cigara preferira pjenusac nad Amaroneom", () => {
    const macanudo = byId(cigars, "cig-macanudo-cafe"); // Connecticut, body 1
    const champagne = byId(wines, "wine-champagne-brut"); // body 2
    const amarone = byId(wines, "wine-amarone"); // body 5
    expect(scorePairing(macanudo, champagne).score).toBeGreaterThan(
      scorePairing(macanudo, amarone).score,
    );
  });

  it("body mismatch se penalizira: puna cigara bolje ide uz puno pice nego uz lagano", () => {
    const partagas = byId(cigars, "cig-partagas-serie-d");
    const espresso = byId(coffees, "cf-espresso-italian-dark");
    const lightFilter = byId(coffees, "cf-v60-ethiopia");
    expect(scorePairing(partagas, espresso).score).toBeGreaterThan(
      scorePairing(partagas, lightFilter).score,
    );
  });
});

describe("pairing engine — API", () => {
  it("pairCigarsForDrink vraca sortirano padajuce s objasnjenjima na oba jezika", () => {
    const hampden = byId(rums, "rum-hampden-estate-8");
    const results = pairCigarsForDrink(hampden, cigars);
    expect(results.length).toBe(cigars.length);
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
    }
    const top = results[0];
    expect(top.reasons.length).toBeGreaterThan(0);
    expect(top.reasons[0].text.hr.length).toBeGreaterThan(0);
    expect(top.reasons[0].text.en.length).toBeGreaterThan(0);
  });

  it("pairDrinksForCigar ukljucuje sva pica — neutralna politika, engine boduje spoj", () => {
    const cohiba = byId(cigars, "cig-cohiba-linea-clasica");
    const results = pairDrinksForCigar(cohiba, rums);
    expect(results.every((r) => r.item.pairable)).toBe(true);
    // spiced/liker vise nisu cenzurirani; niska ocjena spoja dolazi iz pravila
    expect(results.some((r) => r.item.name.includes("Malibu"))).toBe(true);
    const malibu = results.find((r) => r.item.name.includes("Malibu"))!;
    const best = results[0];
    expect(best.score).toBeGreaterThan(malibu.score);
  });

  it("svaka cigara ima barem jednu vitolu s imenom", () => {
    for (const c of cigars) {
      expect(c.vitolas.length).toBeGreaterThan(0);
      expect(c.vitolas[0].name.length).toBeGreaterThan(0);
    }
  });

  it("diversity: top cigare razlicitih brendova se mogu izdvojiti za svako pice", () => {
    const hampden = byId(rums, "rum-hampden-estate-8");
    const ranked = pairCigarsForDrink(hampden, cigars);
    const seen = new Set<string>();
    const diverse = ranked.filter((r) => {
      if (seen.has(r.item.brand)) return false;
      seen.add(r.item.brand);
      return true;
    });
    const top3 = diverse.slice(0, 3);
    expect(new Set(top3.map((r) => r.item.brand)).size).toBe(3);
  });

  it("score je u rasponu 0-100", () => {
    for (const c of cigars.slice(0, 10)) {
      for (const d of [...rums.slice(0, 15), ...coffees.slice(0, 5)]) {
        if (!d.pairable) continue;
        const { score } = scorePairing(c, d);
        expect(score).toBeGreaterThanOrEqual(0);
        expect(score).toBeLessThanOrEqual(100);
      }
    }
  });
});
