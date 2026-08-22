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

  it("svaka kava ima coffeeDetail, cigarHint i dovoljno dugu HR bilješku", () => {
    for (const c of coffees) {
      expect(c.coffeeDetail?.roast, c.id).toMatch(/^(light|medium|dark)$/);
      expect(c.cigarHint?.hr?.length, c.id).toBeGreaterThan(40);
      expect(c.cigarHint?.en?.length, c.id).toBeGreaterThan(40);
      expect(c.notes.hr.length, c.id).toBeGreaterThanOrEqual(80);
      expect(c.notes.en.length, c.id).toBeGreaterThanOrEqual(80);
    }
  });

  it("imenovane HR mješavine postoje, bez cijene", () => {
    const named = [
      "cf-franck-jubilarna",
      "cf-franck-jubilarna-intense",
      "cf-franck-jubilarna-sensual",
      "cf-franck-bonus-espresso",
      "cf-franck-crema",
      "cf-franck-espresso",
      "cf-illy-classico",
      "cf-illy-intenso",
      "cf-lavazza-qualita-rossa",
      "cf-lavazza-qualita-oro",
      "cf-julius-meinl-vienna-espresso",
      "cf-segafredo-intermezzo",
    ];
    for (const id of named) {
      const c = coffees.find((x) => x.id === id);
      expect(c, id).toBeDefined();
      expect(c!.priceEUR, id).toBeNull();
      expect(c!.name.split(/\s+/)[0].length, id).toBeGreaterThan(0);
    }
  });

  it("illy Intenso je tamno prženje visokog intenziteta", () => {
    const p = inferCoffeeProfile(coffees.find((c) => c.id === "cf-illy-intenso")!);
    expect(p.roast).toBe("dark");
    expect(p.intensity).toBe("high");
  });

  it("Lavazza Rossa ostaje medium roast (službeni opis)", () => {
    const c = coffees.find((x) => x.id === "cf-lavazza-qualita-rossa")!;
    expect(c.coffeeDetail?.roast).toBe("medium");
    expect(c.coffeeDetail?.species).toBe("blend");
  });

  it("Jubilarna Intense je tamnija i punija od Sensual", () => {
    const intense = coffees.find((c) => c.id === "cf-franck-jubilarna-intense")!;
    const sensual = coffees.find((c) => c.id === "cf-franck-jubilarna-sensual")!;
    expect(intense.coffeeDetail?.roast).toBe("dark");
    expect(sensual.coffeeDetail?.roast).toBe("medium");
    expect(intense.body).toBeGreaterThan(sensual.body);
    expect(intense.coffeeDetail?.milk).not.toBe(true);
    expect(sensual.coffeeDetail?.milk).not.toBe(true);
  });
});
