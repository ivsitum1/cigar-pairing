import { describe, it, expect } from "vitest";
import cigarsData from "./cigars.json";
import { CIGARS } from "./index";
import type { Cigar } from "../types";

describe("cigars.json integrity", () => {
  it("nema dupliciranih id-eva u izvornom JSON-u", () => {
    const ids = (cigarsData as Cigar[]).map((c) => c.id);
    const unique = new Set(ids);
    expect(unique.size).toBe(ids.length);
  });

  it("CIGARS nakon dedupe ima jedinstvene id-eve", () => {
    const ids = CIGARS.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("Oliva Serie O — ima više vitola i traži odabir", () => {
    const serieO = CIGARS.find((c) => c.id === "cig-oliva-serie-o");
    expect(serieO).toBeDefined();
    expect(serieO!.line).toBe("Serie O");
    expect(serieO!.vitola.toLowerCase()).not.toContain("tubos");
    const names = (serieO!.vitolas ?? []).map((v) => v.name);
    expect(names).toContain("Serie O Robusto");
    expect(names).toContain("Tubos");
    expect(names).toContain("Serie O Puro");
    expect(names).toContain("Serie O Churchill");
    expect(names.length).toBeGreaterThanOrEqual(4);
  });

  it("Oliva Serie G — odabir po id-u vraća istu liniju", () => {
    const serieG = CIGARS.find((c) => c.id === "cig-oliva-serie-g");
    expect(serieG).toBeDefined();
    expect(serieG!.line).toBe("Serie G");
    expect(serieG!.vitola.toLowerCase()).toBe("special g");
  });
});
