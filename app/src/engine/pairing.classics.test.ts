// Klasični parovi ne smiju pasti nakon body/affinity kalibracije.
import { describe, it, expect } from "vitest";
import { cigarById, drinkById } from "../data";
import { scorePairing } from "./pairing";
import { applyVitola, uniqueVitolas } from "../lib/cigarVitola";

function applied(lineId: string) {
  const line = cigarById(lineId)!;
  const vs = uniqueVitolas(line);
  return vs.length ? applyVitola(line, vs[0]) : line;
}

describe("pairing classic floors — smisleni parovi ostaju visoko", () => {
  it("blagi Connecticut × cognac VS / agricole", () => {
    const hennessy = drinkById("br-hennessy-vs")!;
    const clement = drinkById("rum-clement-vsop-agricole")!;
    const bundle = applied("cig-cusano-bundle-selection");
    const macanudo = cigarById("cig-macanudo-cafe")!;
    expect(scorePairing(bundle, hennessy).score).toBeGreaterThanOrEqual(65);
    expect(scorePairing(macanudo, clement).score).toBeGreaterThanOrEqual(80);
  });

  it("Cusano Bundle: Hennessy VS pobjeđuje VSOP/XO i body-3 VS", () => {
    const line = cigarById("cig-cusano-bundle-selection")!;
    const robusto = uniqueVitolas(line).find((v) => /robusto/i.test(v.name))!;
    const cigar = applyVitola(line, robusto);
    const hennessy = scorePairing(cigar, drinkById("br-hennessy-vs")!).score;
    const courvoisier = scorePairing(cigar, drinkById("br-courvoisier-vs")!).score;
    const remy = scorePairing(cigar, drinkById("br-remy-martin-vsop")!).score;
    const camusXo = scorePairing(
      cigar,
      drinkById("br-camus-xo-intensely-aromatic-cognac-40-vol-0-7l-u-poklon-kutiji")!,
    ).score;
    expect(hennessy).toBeGreaterThan(courvoisier);
    expect(hennessy).toBeGreaterThan(remy);
    expect(hennessy).toBeGreaterThan(camusXo);
  });

  it("puna maduro × tamni rum / espresso ostaje preferirana", () => {
    const padron = cigarById("cig-padron-1964-anniversary")!;
    const zacapa = drinkById("rum-zacapa-centenario-23")!;
    const espresso = drinkById("cf-espresso-italian-dark")!;
    const macanudo = cigarById("cig-macanudo-cafe")!;
    expect(scorePairing(padron, espresso).score).toBeGreaterThan(
      scorePairing(macanudo, espresso).score,
    );
    // Zacapa nije više sweetness 4, ali maduro i dalje bolje od blagog Connecticuta
    expect(scorePairing(padron, zacapa).score).toBeGreaterThan(
      scorePairing(macanudo, zacapa).score,
    );
  });

  it("Cusano 18 Maduro × Hennessy VS ostaje jak (body match)", () => {
    const maduro = applied("cig-cusano-18-maduro");
    const hennessy = drinkById("br-hennessy-vs")!;
    expect(scorePairing(maduro, hennessy).score).toBeGreaterThanOrEqual(70);
  });

  it("jaki mismatch ostaje nizak (puna cigara × lagano agricole)", () => {
    const antano = cigarById("cig-joya-de-nicaragua-antano")!;
    const clement = drinkById("rum-clement-vsop-agricole")!;
    expect(scorePairing(antano, clement).score).toBeLessThan(55);
  });

  it("Hampden preferira jaku cigaru nad blagom", () => {
    const hampden = drinkById("rum-hampden-estate-8")!;
    const partagas = cigarById("cig-partagas-serie-d")!;
    const fonseca = cigarById("cig-fonseca-delicias")!;
    expect(scorePairing(partagas, hampden).score).toBeGreaterThan(
      scorePairing(fonseca, hampden).score,
    );
  });
});
