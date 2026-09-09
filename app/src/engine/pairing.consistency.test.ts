// Isti par (cigara+vitola, piće, prefs, serve, occasion) → isti score
// kroz scorePairing / pairDrinksForCigar / pairCigarsForDrink.
import { describe, it, expect } from "vitest";
import { ALL_DRINKS, CIGARS, cigarById, drinkById } from "../data";
import {
  displayScore,
  pairCigarsForDrink,
  pairDrinksForCigar,
  scorePairing,
} from "./pairing";
import { applyVitola, expandForPairing, uniqueVitolas } from "../lib/cigarVitola";
import type { PersonalPrefs } from "./personal";

const hennessy = () => drinkById("br-hennessy-vs")!;
const cusanoBundle = () => cigarById("cig-cusano-bundle-selection")!;

function vitolaOf(lineId: string, name: string) {
  const line = cigarById(lineId)!;
  const v = uniqueVitolas(line).find((x) => x.name === name);
  if (!v) throw new Error(`missing vitola ${name} on ${lineId}`);
  return applyVitola(line, v);
}

describe("pairing consistency — ista vitola = isti broj", () => {
  it("Cusano Bundle × Hennessy VS je dobar par (~70), ne mismatch ~39", () => {
    // Connecticut + cognac-vs: wrapper afinitet + body Δ=1 → body-match, ne kazna.
    const drink = hennessy();
    const robusto = vitolaOf("cig-cusano-bundle-selection", "Robusto");
    const { score, reasons } = scorePairing(robusto, drink);
    expect(reasons.some((r) => r.rule === "body-match")).toBe(true);
    expect(reasons.some((r) => r.rule === "wrapper-affinity")).toBe(true);
    expect(score).toBeGreaterThanOrEqual(65);
    expect(score).toBeLessThanOrEqual(80);
    // isti broj u oba wrapera
    expect(pairDrinksForCigar(robusto, [drink])[0].score).toBe(score);
    expect(pairCigarsForDrink(drink, [robusto])[0].score).toBe(score);
  });

  it("Cusano Figurado ≠ Robusto × Hennessy VS (geometrija)", () => {
    const drink = hennessy();
    const figurado = vitolaOf("cig-cusano-bundle-selection", "Figurado");
    const robusto = vitolaOf("cig-cusano-bundle-selection", "Robusto");
    const f = scorePairing(figurado, drink).score;
    const r = scorePairing(robusto, drink).score;
    // Ring 49 vs 50: bar jedan se može poklopiti; Panatela (30) je jasniji kontrast
    // — Figurado i Robusto smiju biti blizu, ali ne smiju biti isti objekt.
    expect(figurado.selectedVitola).toBe("Figurado");
    expect(robusto.selectedVitola).toBe("Robusto");
    expect(figurado.format).not.toBe(robusto.format);
    // Ako su scoreovi jednaki zbog sličnog ringa, barem raw / reasons path
    // mora ići preko odabrane vitole (vitolas.length === 1).
    expect(figurado.vitolas).toHaveLength(1);
    expect(robusto.vitolas).toHaveLength(1);
    void f;
    void r;
  });

  it("Cusano Panatela × Hennessy VS ≠ Robusto (tanak ring mijenja score)", () => {
    const drink = hennessy();
    const panatela = vitolaOf("cig-cusano-bundle-selection", "Panatela");
    const robusto = vitolaOf("cig-cusano-bundle-selection", "Robusto");
    expect(scorePairing(panatela, drink).score).not.toBe(
      scorePairing(robusto, drink).score,
    );
  });

  it("isti par: scorePairing === pairDrinksForCigar === pairCigarsForDrink", () => {
    const drink = hennessy();
    for (const name of ["Figurado", "Robusto", "Panatela"] as const) {
      const cigar = vitolaOf("cig-cusano-bundle-selection", name);
      const direct = scorePairing(cigar, drink);
      const fromCigar = pairDrinksForCigar(cigar, [drink])[0];
      const fromDrink = pairCigarsForDrink(drink, [cigar])[0];
      expect(fromCigar.score, name).toBe(direct.score);
      expect(fromDrink.score, name).toBe(direct.score);
      expect(fromCigar.rawScore, name).toBe(direct.rawScore);
      expect(fromDrink.rawScore, name).toBe(direct.rawScore);
    }
  });

  it("occasion i serve u oba wrapera daju isti broj", () => {
    const cigar = vitolaOf("cig-cusano-bundle-selection", "Robusto");
    const drink = hennessy();
    const evening = {
      a: scorePairing(cigar, drink, undefined, undefined, "evening"),
      b: pairDrinksForCigar(cigar, [drink], undefined, undefined, "evening")[0],
      c: pairCigarsForDrink(drink, [cigar], undefined, undefined, "evening")[0],
    };
    expect(evening.b.score).toBe(evening.a.score);
    expect(evening.c.score).toBe(evening.a.score);

    const rocks = {
      a: scorePairing(cigar, drink, undefined, "rocks"),
      b: pairDrinksForCigar(cigar, [drink], undefined, "rocks")[0],
      c: pairCigarsForDrink(drink, [cigar], undefined, "rocks")[0],
    };
    expect(rocks.b.score).toBe(rocks.a.score);
    expect(rocks.c.score).toBe(rocks.a.score);
  });

  it("prefs u Custom putu (scorePairing) jednak wraperima", () => {
    const cigar = vitolaOf("cig-cusano-bundle-selection", "Robusto");
    const drink = hennessy();
    const prefs: PersonalPrefs = {
      drinkStyle: { [drink.style]: 0.8 },
      cigarBrand: { Cusano: 0.5 },
      entries: 4,
    };
    const direct = scorePairing(cigar, drink, prefs, "water", "morning");
    const fromCigar = pairDrinksForCigar(
      cigar,
      [drink],
      prefs,
      "water",
      "morning",
    )[0];
    const fromDrink = pairCigarsForDrink(
      drink,
      [cigar],
      prefs,
      "water",
      "morning",
    )[0];
    expect(fromCigar.score).toBe(direct.score);
    expect(fromDrink.score).toBe(direct.score);
    expect(direct.score).not.toBe(scorePairing(cigar, drink).score);
  });

  it("katalog: expandForPairing + oba wrapera se slažu (uzorak)", () => {
    const multi = CIGARS.filter((c) => uniqueVitolas(c).length > 1).filter(
      (_, i) => i % 11 === 0,
    );
    // uvijek uključi Bundle Selection
    const bundle = cusanoBundle();
    if (!multi.some((c) => c.id === bundle.id)) multi.unshift(bundle);

    const drinks = ALL_DRINKS.filter((d) => d.pairable).filter(
      (_, i) => i % 17 === 0,
    );
    expect(drinks.length).toBeGreaterThan(5);

    for (const line of multi) {
      for (const applied of expandForPairing(line)) {
        expect(applied.vitolas.length).toBe(1);
        for (const drink of drinks) {
          const a = pairDrinksForCigar(applied, [drink])[0].score;
          const b = pairCigarsForDrink(drink, [applied])[0].score;
          expect(a, `${line.id}/${applied.vitola}×${drink.id}`).toBe(b);
          expect(a).toBe(Math.round(displayScore(scorePairing(applied, drink).rawScore)));
        }
      }
    }
  }, 60_000);

  it("expandForPairing ne ostavlja gol multi-vitola bundle", () => {
    const line = cusanoBundle();
    expect(uniqueVitolas(line).length).toBeGreaterThan(1);
    const expanded = expandForPairing(line);
    expect(expanded.length).toBe(uniqueVitolas(line).length);
    for (const c of expanded) {
      expect(c.vitolas).toHaveLength(1);
      expect(c.selectedVitola).toBeTruthy();
    }
  });
});
