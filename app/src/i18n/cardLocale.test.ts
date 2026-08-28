import { describe, expect, it } from "vitest";
import cigarsJson from "../data/cigars.json";
import { leafLabel } from "../i18n/leafLabel";
import type { Cigar } from "../types";

const cigars = cigarsJson as unknown as Cigar[];

describe("kartice ne miješaju EN zemljopis u HR listovima", () => {
  it("učestali engleski geo-wrapperi lokaliziraju se na HR", () => {
    const samples = [
      "Nicaragua",
      "Nicaraguan",
      "Ecuador",
      "Dominican Republic",
      "Mexican San Andres",
      "Brazilian",
    ];
    for (const raw of samples) {
      const hr = leafLabel(raw, "hr");
      expect(hr, raw).not.toMatch(/\bNicaragua\b|\bEcuador\b|\bDominican Republic\b|\bMexican\b|\bBrazilian\b/i);
    }
  });

  it("uzorak kataloga: HR prikaz wrappera ne sadrži golu Nicaragua uz HR zemlju", () => {
    const mixed = cigars.filter(
      (c) =>
        c.country === "Nikaragva" &&
        /nicaragu/i.test(c.wrapper) &&
        !/habano|maduro|corojo|connecticut/i.test(c.wrapper),
    );
    expect(mixed.length).toBeGreaterThan(10);
    for (const c of mixed.slice(0, 40)) {
      const shown = leafLabel(c.wrapper, "hr");
      expect(shown, c.id).not.toMatch(/\bNicaragua\b|\bNicaraguan\b/);
    }
  });
});
