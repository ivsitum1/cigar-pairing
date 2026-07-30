import { describe, expect, it } from "vitest";
import type { Cigar } from "../types";
import cigarsJson from "./cigars.json";
import { SHOPS } from "./shops";
import { cigarShopLinks } from "./index";

const cigars = cigarsJson as unknown as Cigar[];
const TOBACCO_PETICA = "Tobacco Petica (Branimir)";

const byId = (id: string): Cigar => {
  const hit = cigars.find((c) => c.id === id);
  if (!hit) throw new Error(`missing ${id}`);
  return hit;
};

describe("Tobacco Petica (Branimir centar)", () => {
  it("registrirana je kao HR trgovina bez web kataloga", () => {
    const shop = SHOPS.find((s) => s.id === "tobacco-petica-branimir");
    expect(shop).toBeDefined();
    expect(shop?.name).toBe(TOBACCO_PETICA);
    expect(shop?.region).toBe("HR");
    expect(shop?.walkIn).toBe(true);
    expect(shop?.productHost).toBeUndefined();
  });

  it("CAO Bones, Don Tomas Bundle i Clásico su ondje dostupni", () => {
    expect(byId("cig-cao-bones").availabilityHR).toContain(TOBACCO_PETICA);
    expect(byId("cig-cao-bones").vitolas.map((v) => v.name)).toContain(
      "Chicken Foot",
    );
    expect(byId("cig-don-tomas-bundle").availabilityHR).toContain(
      TOBACCO_PETICA,
    );
    const bundleByName = Object.fromEntries(
      byId("cig-don-tomas-bundle").vitolas.map((v) => [v.name, v]),
    );
    expect(bundleByName.Rothschild?.priceEUR).toBe(2.8);
    expect(bundleByName.Robusto?.priceEUR).toBe(3.6);
    expect(bundleByName["Petit Corona"]?.priceEUR).toBe(3.6);
    expect(byId("cig-don-tomas-clasico").markets).toContain("HR");
    expect(byId("cig-don-tomas-clasico").availabilityHR).toContain(
      TOBACCO_PETICA,
    );
  });

  it("La Estrella Polar (Robusto, Gigante) je ondje dostupna", () => {
    const polar = byId("cig-la-estrella-polar");
    expect(polar.markets).toContain("HR");
    expect(polar.availabilityHR).toContain(TOBACCO_PETICA);
    const byName = Object.fromEntries(polar.vitolas.map((v) => [v.name, v]));
    expect(byName.Robusto?.priceEUR).toBe(5.2);
    expect(byName.Gigante?.priceEUR).toBe(6.2);
  });

  it("ducan bez kataloga ne dobiva link po proizvodu", () => {
    for (const id of [
      "cig-cao-bones",
      "cig-don-tomas-bundle",
      "cig-don-tomas-clasico",
      "cig-la-estrella-polar",
    ]) {
      const shops = cigarShopLinks(byId(id)).map((l) => l.shop);
      expect(shops, id).not.toContain(TOBACCO_PETICA);
    }
  });
});
