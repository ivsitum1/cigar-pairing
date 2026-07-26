import { describe, expect, it } from "vitest";
import {
  brandDisplayName,
  brandSearchHaystack,
  brandInfo,
  CIGARS,
  cigarInRegion,
  resolveCigarId,
} from "./index";

const BRAND = "La Aroma de Cuba";

describe("brandDisplayName — La Aroma market alias", () => {
  it("HR and EU show La Aroma del Caribe", () => {
    expect(brandDisplayName(BRAND, "HR")).toBe("La Aroma del Caribe");
    expect(brandDisplayName(BRAND, "EU")).toBe("La Aroma del Caribe");
  });

  it("USA and ALL keep La Aroma de Cuba", () => {
    expect(brandDisplayName(BRAND, "USA")).toBe("La Aroma de Cuba");
    expect(brandDisplayName(BRAND, "ALL")).toBe("La Aroma de Cuba");
  });

  it("unknown brand falls back to canonical name", () => {
    expect(brandDisplayName("Nonexistent Brand XYZ", "HR")).toBe(
      "Nonexistent Brand XYZ",
    );
  });
});

describe("brandSearchHaystack — caribe + cuba", () => {
  it("includes both canonical and display aliases", () => {
    const hay = brandSearchHaystack(BRAND).toLowerCase();
    expect(hay).toContain("la aroma de cuba");
    expect(hay).toContain("la aroma del caribe");
  });

  it("brands.json has HR/EU displayNames", () => {
    const info = brandInfo(BRAND);
    expect(info?.displayNames?.HR).toBe("La Aroma del Caribe");
    expect(info?.displayNames?.EU).toBe("La Aroma del Caribe");
  });
});

describe("La Aroma catalog fills", () => {
  const byLine = (line: string) =>
    CIGARS.find((c) => c.brand === BRAND && c.line === line);

  it("Mi Amor is available in HR with humidor links", () => {
    const c = byLine("Mi Amor");
    expect(c).toBeTruthy();
    expect(c!.markets).toContain("HR");
    expect(c!.availabilityHR?.length).toBeGreaterThan(0);
    const duque = c!.vitolas.find((v) => v.name === "Duque");
    expect(duque?.regionLinks?.HR?.url).toMatch(/humidor\.hr/);
  });

  it("Edición Especial No. 3 exists with HR + EU links", () => {
    const c = byLine("Edición Especial No. 3");
    expect(c).toBeTruthy();
    expect(c!.id).toBe("cig-la-aroma-de-cuba-edicion-especial-no-3");
    expect(cigarInRegion(c!, "HR")).toBe(true);
    expect(cigarInRegion(c!, "EU")).toBe(true);
    expect(c!.regionLinks?.HR?.url).toMatch(/humidor\.hr/);
    expect(c!.regionLinks?.EU?.url).toMatch(/cigarworld\.de/);
  });

  it("Reserva is available in EU with Cigarworld vitolas", () => {
    const c = byLine("Reserva");
    expect(c).toBeTruthy();
    expect(c!.markets).toContain("EU");
    expect(c!.regionLinks?.EU?.url).toMatch(/cigarworld\.de/);
    const names = c!.vitolas.map((v) => v.name);
    expect(names).toEqual(
      expect.arrayContaining(["Maximo", "Divino", "Romantico", "Pomposo"]),
    );
  });

  it("Habano Reserve and Small Batch exist as USA lines", () => {
    const habano = byLine("Habano Reserve");
    const small = byLine("Small Batch");
    expect(habano?.markets).toContain("USA");
    expect(small?.markets).toContain("USA");
    expect(habano?.regionLinks?.USA?.url).toMatch(/holts\.com/);
    expect(small?.regionLinks?.USA?.url).toMatch(/holts\.com/);
  });

  it("legacy del Caribe EE No. 3 alias resolves", () => {
    const hit = resolveCigarId("cig-la-aroma-del-caribe-edicion-especial-no-3");
    expect(hit?.id).toBe("cig-la-aroma-de-cuba-edicion-especial-no-3");
  });

  it("HR filter shows at least Base Line, Connecticut, Pasión, Mi Amor, EE No. 3", () => {
    const hrLines = CIGARS.filter(
      (c) => c.brand === BRAND && cigarInRegion(c, "HR"),
    ).map((c) => c.line);
    for (const line of [
      "Base Line",
      "Connecticut",
      "Pasión",
      "Mi Amor",
      "Edición Especial No. 3",
    ]) {
      expect(hrLines).toContain(line);
    }
  });
});
