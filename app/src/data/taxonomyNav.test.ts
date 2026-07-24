import { describe, expect, it } from "vitest";
import {
  BRAND_INDEX,
  brandFromSlug,
  brandSlug,
  linesByBrand,
  resolveCigarId,
  vitolaSlug,
  CIGARS,
} from "./index";
import aliasFile from "./cigarIdAliases.json";

describe("Phase 4 taxonomy derivations", () => {
  it("BRAND_INDEX covers every brand", () => {
    expect(BRAND_INDEX.length).toBeGreaterThan(400);
    expect(BRAND_INDEX.every((b) => b.lines.length >= 1 && b.vitolaCount >= 1)).toBe(true);
  });

  it("linesByBrand sorts brand-named line first, then A→Z", () => {
    const brand = CIGARS.find((c) =>
      CIGARS.some((x) => x.brand === c.brand && x.line === c.brand),
    )?.brand;
    if (!brand) return;
    const lines = linesByBrand(brand);
    const core = lines.filter((c) => c.line === brand);
    expect(core.length).toBeGreaterThan(0);
    expect(lines[0].line).toBe(brand);
    const rest = lines.slice(core.length).map((c) => c.line);
    const sorted = [...rest].sort((a, b) => a.localeCompare(b));
    expect(rest).toEqual(sorted);
  });

  it("vitolaSlug is stable kebab-case", () => {
    expect(vitolaSlug("Chaveta")).toBe("chaveta");
    expect(vitolaSlug({ name: "El Lector", format: null, smokeTimeMin: null, priceEUR: null, url: null })).toBe(
      "el-lector",
    );
  });

  it("brandSlug round-trips via brandFromSlug", () => {
    const brand = BRAND_INDEX[0]?.brand;
    expect(brand).toBeTruthy();
    expect(brandFromSlug(brandSlug(brand!))).toBe(brand);
  });

  it("resolveCigarId follows alias chain to a live record", () => {
    const aliases =
      (aliasFile as { aliases?: Record<string, string> }).aliases ?? {};
    const sample = Object.entries(aliases).find(([, target]) =>
      CIGARS.some((c) => c.id === target),
    );
    expect(sample).toBeTruthy();
    const [from, to] = sample!;
    const hit = resolveCigarId(from);
    expect(hit?.id).toBe(to);
    expect(resolveCigarId(to)?.id).toBe(to);
  });
});
