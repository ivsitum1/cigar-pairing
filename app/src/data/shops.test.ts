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

  it("CAO Bones (Chicken Foot) i Don Tomas Bundle su ondje dostupni", () => {
    expect(byId("cig-cao-bones").availabilityHR).toContain(TOBACCO_PETICA);
    expect(byId("cig-cao-bones").vitolas.map((v) => v.name)).toContain(
      "Chicken Foot",
    );
    expect(byId("cig-don-tomas-bundle").availabilityHR).toContain(
      TOBACCO_PETICA,
    );
  });

  it("ducan bez kataloga ne dobiva link po proizvodu", () => {
    for (const id of ["cig-cao-bones", "cig-don-tomas-bundle"]) {
      const shops = cigarShopLinks(byId(id)).map((l) => l.shop);
      expect(shops, id).not.toContain(TOBACCO_PETICA);
    }
  });
});

describe("USA shop registry", () => {
  it("Holt's je jedina USA trgovina; Cigars Daily je demoted", () => {
    const usa = SHOPS.filter((s) => s.region === "USA").map((s) => s.id);
    expect(usa).toEqual(["holts"]);
  });
});
