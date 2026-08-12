import { describe, it, expect } from "vitest";
import { scorePairing } from "./pairing";
import {
  inferCoffeeProfile,
  coffeePairingReasons,
  type CoffeeProfile,
} from "./coffeePairing";
import type { Cigar, Drink } from "../types";
import cigarsData from "../data/cigars.json";
import coffeesData from "../data/coffees.json";
import rumsData from "../data/rums.json";

const cigars = cigarsData as Cigar[];
const coffees = coffeesData as unknown as Drink[];
const rums = rumsData as unknown as Drink[];

const byId = <T extends { id: string }>(arr: T[], id: string): T => {
  const found = arr.find((x) => x.id === id);
  if (!found) throw new Error(`missing ${id}`);
  return found;
};

const stubCigar = (partial: Partial<Cigar> & Pick<Cigar, "body" | "strength" | "wrapper">): Cigar =>
  ({
    id: "stub-cig",
    brand: "Stub",
    line: "Line",
    vitola: "Robusto",
    format: "",
    country: "NI",
    flavorTags: [],
    smokeTimeMin: 60,
    priceEUR: null,
    vitolas: [],
    markets: ["WW"],
    availabilityHR: [],
    notes: { hr: "", en: "" },
    ...partial,
  }) as Cigar;

describe("inferCoffeeProfile", () => {
  it("mapira espresso-dark na dark roast + high intensity", () => {
    const espresso = byId(coffees, "cf-espresso-italian-dark");
    const p = inferCoffeeProfile(espresso);
    expect(p.roast).toBe("dark");
    expect(p.intensity).toBe("high");
    expect(p.flavorFamily).toBe("nuttyCocoa");
  });

  it("mapira ethiopian filter-light na light roast + floral + high acidity", () => {
    const eth = byId(coffees, "cf-v60-ethiopia");
    const p = inferCoffeeProfile(eth);
    expect(p.roast).toBe("light");
    expect(p.intensity).toBe("low");
    expect(p.flavorFamily).toBe("floral");
    expect(p.acidity).toBe("high");
  });

  it("mapira sumatra filter-dark na earthy family", () => {
    const sumatra = byId(coffees, "cf-sumatra-mandheling");
    const p = inferCoffeeProfile(sumatra);
    expect(p.flavorFamily).toBe("earthy");
    expect(p.roast).toBe("dark");
  });

  it("mapira brazil na nuttyCocoa s nižom kiselošću", () => {
    const brazil = byId(coffees, "cf-brazil-santos");
    const p = inferCoffeeProfile(brazil);
    expect(p.flavorFamily).toBe("nuttyCocoa");
    expect(p.acidity).toBe("low");
  });

  it("mapira americano na medium intensity (espresso + voda)", () => {
    const americano = byId(coffees, "cf-americano");
    const p = inferCoffeeProfile(americano);
    expect(p.intensity).toBe("medium");
    expect(p.flavorFamily).toBe("nuttyCocoa");
  });
});

describe("coffeePairingReasons — overlay", () => {
  it("ne dira ne-kavu", () => {
    const cigar = byId(cigars, "cig-padron-1964-anniversary");
    const rum = byId(rums, "rum-hampden-estate-8");
    expect(coffeePairingReasons(cigar, rum)).toEqual([]);
  });

  it("tamni espresso + jaka cigara: intensity match", () => {
    const espresso = byId(coffees, "cf-espresso-italian-dark");
    const strong = stubCigar({
      body: 4,
      strength: 4,
      wrapper: "Maduro",
      flavorTags: ["kakao", "zemljano"],
    });
    const rules = coffeePairingReasons(strong, espresso).map((r) => r.rule);
    expect(rules).toContain("coffee-intensity-match");
  });

  it("tamni espresso + blaga cigara: intensity mismatch", () => {
    const espresso = byId(coffees, "cf-espresso-italian-dark");
    const mild = stubCigar({
      body: 1,
      strength: 1,
      wrapper: "Connecticut",
      flavorTags: ["kremasto"],
    });
    const rules = coffeePairingReasons(mild, espresso).map((r) => r.rule);
    expect(rules).toContain("coffee-intensity-mismatch");
  });

  it("floral/light kava + blaga cigara: delicate bridge", () => {
    const eth = byId(coffees, "cf-v60-ethiopia");
    const mild = stubCigar({
      body: 1,
      strength: 1,
      wrapper: "Connecticut",
      flavorTags: ["cvjetno", "kremasto"],
    });
    const rules = coffeePairingReasons(mild, eth).map((r) => r.rule);
    expect(rules).toContain("coffee-delicate-bridge");
  });

  it("floral/light kava + puna jaka cigara: delicate overwhelm", () => {
    const eth = byId(coffees, "cf-v60-ethiopia");
    const heavy = stubCigar({
      body: 5,
      strength: 5,
      wrapper: "Maduro",
      flavorTags: ["zemljano", "kakao"],
    });
    const rules = coffeePairingReasons(heavy, eth).map((r) => r.rule);
    expect(rules).toContain("coffee-delicate-overwhelm");
  });

  it("sumatra earthy + cigara s duhan/zemljano: flavor bridge", () => {
    const sumatra = byId(coffees, "cf-sumatra-mandheling");
    const spicy = stubCigar({
      body: 4,
      strength: 4,
      wrapper: "Habano",
      flavorTags: ["zemljano", "duhan", "zacini"],
    });
    const rules = coffeePairingReasons(spicy, sumatra).map((r) => r.rule);
    expect(rules).toContain("coffee-flavor-bridge");
  });

  it("visoka kiselost (Kenya) + teška cigara: acidity contrast (cleanser)", () => {
    const kenya = byId(coffees, "cf-v60-kenya");
    const heavy = stubCigar({
      body: 5,
      strength: 4,
      wrapper: "Maduro",
      flavorTags: ["zemljano", "kakao"],
    });
    const profile: CoffeeProfile = inferCoffeeProfile(kenya);
    expect(profile.acidity).toBe("high");
    const rules = coffeePairingReasons(heavy, kenya).map((r) => r.rule);
    expect(rules).toContain("coffee-acidity-contrast");
  });

  it("slatka brazil kava + začinska cigara: sweet mellow", () => {
    const brazil = byId(coffees, "cf-brazil-santos");
    const spicy = stubCigar({
      body: 3,
      strength: 3,
      wrapper: "Habano",
      flavorTags: ["zacini", "papar"],
    });
    const rules = coffeePairingReasons(spicy, brazil).map((r) => r.rule);
    expect(rules).toContain("coffee-sweet-mellow");
  });
});

describe("scorePairing — coffee overlay wired in", () => {
  it("espresso + maduro dobiva coffee reason u reasons", () => {
    const espresso = byId(coffees, "cf-espresso-italian-dark");
    const padron = byId(cigars, "cig-padron-1964-anniversary");
    const { reasons } = scorePairing(padron, espresso);
    expect(reasons.some((r) => r.rule.startsWith("coffee-"))).toBe(true);
  });

  it("rum parovi nemaju coffee-* rules", () => {
    const rum = byId(rums, "rum-hampden-estate-8");
    const partagas = byId(cigars, "cig-partagas-serie-d");
    const { reasons } = scorePairing(partagas, rum);
    expect(reasons.every((r) => !r.rule.startsWith("coffee-"))).toBe(true);
  });

  it("ethiopia + connecticut bolje od ethiopia + antano (delicate rule)", () => {
    const eth = byId(coffees, "cf-v60-ethiopia");
    const macanudo = byId(cigars, "cig-macanudo-cafe");
    const antano = byId(cigars, "cig-joya-de-nicaragua-antano");
    expect(scorePairing(macanudo, eth).score).toBeGreaterThan(
      scorePairing(antano, eth).score,
    );
  });
});
