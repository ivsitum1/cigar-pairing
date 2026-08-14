import { describe, expect, it } from "vitest";
import coffeesData from "./coffees.json";
import model from "./coffeePairingModel.json";
import { inferCoffeeProfile } from "../engine/coffeePairing";
import type { Drink } from "../types";

const coffees = coffeesData as unknown as Drink[];

/** Grill / Hoffmann regional map → at least one catalog id per region. */
const REGION_COVERAGE: Record<string, string[]> = {
  Ethiopia: ["cf-v60-ethiopia", "cf-ethiopia-natural"],
  Kenya: ["cf-v60-kenya"],
  "Burundi/Rwanda": ["cf-burundi-washed"],
  Brazil: ["cf-brazil-santos", "cf-aeropress-brazil"],
  Colombia: ["cf-colombia-medium", "cf-decaf-quality"],
  "Costa Rica": ["cf-pour-over-costa-rica"],
  Guatemala: ["cf-guatemala-antigua"],
  Panama: ["cf-panama-geisha"],
  "Indonesia (semi-washed)": ["cf-sumatra-mandheling", "cf-monsooned-malabar"],
  "Islands (Jamaica/Cuba/Dominican)": [
    "cf-jamaica-blue-mountain",
    "cf-cuba-serrano",
    "cf-cubano-sweet",
  ],
};

describe("coffees catalog — Hoffmann regional alignment", () => {
  const regionKeys = Object.keys(
    (model as { origins: { regions: Record<string, string> } }).origins.regions,
  );

  it("pokriva sve regije iz coffeePairingModel", () => {
    for (const region of regionKeys) {
      const ids = REGION_COVERAGE[region];
      expect(ids, `missing coverage map for ${region}`).toBeDefined();
      for (const id of ids!) {
        expect(coffees.some((c) => c.id === id), id).toBe(true);
      }
    }
  });

  it("sumatra nosi duhan/drvo za earthy-habano most", () => {
    const sumatra = coffees.find((c) => c.id === "cf-sumatra-mandheling")!;
    expect(sumatra.flavorTags).toEqual(expect.arrayContaining(["duhan", "drvo"]));
    expect(inferCoffeeProfile(sumatra).flavorFamily).toBe("earthy");
  });

  it("tri okomite osi: priprema, prženje i zrno stoje odvojeno", () => {
    const PREPS = new Set([
      "espresso",
      "ristretto",
      "lungo",
      "americano",
      "moka",
      "turkish",
      "filter",
      "french-press",
      "cold-brew",
      "milk",
      "instant",
      "spiked",
    ]);
    for (const c of coffees) {
      // stari spojeni ključ ("espresso-dark") ne smije se vratiti u podatke
      expect(c.style, c.id).not.toMatch(/-(light|medium|dark)$/);
      expect(PREPS.has(c.style), `${c.id}: nepoznata priprema ${c.style}`).toBe(true);
      expect(["light", "medium", "dark"], c.id).toContain(c.roast);
      expect(["arabica", "robusta", "blend"], c.id).toContain(c.species);
    }
  });

  it("kava vođena podrijetlom ima zemlju, priprema bez podrijetla nema", () => {
    const origin = coffees.find((c) => c.id === "cf-v60-ethiopia")!;
    expect(origin.country).toBe("Etiopija");
    // ristretto nije ni jedna zemlja — to je način pripreme
    expect(coffees.find((c) => c.id === "cf-ristretto")!.country).toBe("—");
  });

  it("instant je u katalogu, ali pošteno ocijenjen", () => {
    const instants = coffees.filter((c) => c.style === "instant");
    expect(instants.length).toBeGreaterThanOrEqual(1);
    for (const c of instants) {
      expect(c.pairable, `${c.id} mora biti pairable — engine ga boduje, ne cenzurira`).toBe(true);
      expect(c.qualityScore ?? 0).toBeLessThanOrEqual(4);
    }
  });

  it("americano postoji za medium-TDS stil", () => {
    const am = coffees.find((c) => c.id === "cf-americano")!;
    expect(am.style).toBe("americano");
    expect(inferCoffeeProfile(am).intensity).toBe("medium");
  });

  it("panama geisha mapira na floral + high acidity", () => {
    const geisha = coffees.find((c) => c.id === "cf-panama-geisha")!;
    const p = inferCoffeeProfile(geisha);
    expect(p.flavorFamily).toBe("floral");
    expect(p.acidity).toBe("high");
    expect(p.intensity).toBe("low");
  });
});
