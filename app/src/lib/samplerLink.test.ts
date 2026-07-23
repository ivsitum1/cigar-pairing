import { describe, it, expect } from "vitest";
import { CIGARS } from "../data";
import { resolveSamplerCigar } from "./samplerLink";

describe("resolveSamplerCigar", () => {
  const sampler = CIGARS.find((c) => c.id === "cig-la-galera-robusto-sampler");

  it("La Galera Robusto Sampler ima lineup", () => {
    expect(sampler?.lineup?.length).toBeGreaterThan(0);
  });

  it("Connecticut Robusto → Connecticut linija, vitola Robusto", () => {
    const hit = resolveSamplerCigar("La Galera", "Connecticut Robusto ×2", sampler!.id);
    expect(hit).not.toBeNull();
    expect(hit!.line).toBe("Connecticut");
    expect(hit!.vitola).toBe("Robusto");
  });

  it("Anemoi Eurus → Anemoi Eurus linija", () => {
    const hit = resolveSamplerCigar("La Galera", "Anemoi Eurus ×1", sampler!.id);
    expect(hit?.line).toBe("Anemoi Eurus");
  });

  it("1936 Box Pressed Robusto → 1936 Box Pressed linija", () => {
    const hit = resolveSamplerCigar("La Galera", "1936 Box Pressed Robusto ×2", sampler!.id);
    expect(hit?.line).toMatch(/^1936 Box Pressed/);
  });

  it("Imperial Jade Robusto → Imperial Jade linija", () => {
    const hit = resolveSamplerCigar("La Galera", "Imperial Jade Robusto ×1", sampler!.id);
    expect(hit?.line).toMatch(/^Imperial Jade/);
  });

  it("svaki redak La Galera samplera se razriješi u neku cigaru", () => {
    for (const label of sampler!.lineup ?? []) {
      const hit = resolveSamplerCigar("La Galera", label, sampler!.id);
      expect(hit, label).not.toBeNull();
    }
  });

  it("ne otvara samog sebe / drugi sampler", () => {
    const hit = resolveSamplerCigar("La Galera", "Connecticut Robusto ×2", sampler!.id);
    expect(hit?.lineup ?? null).toBeNull();
    expect(hit?.id).not.toBe(sampler!.id);
  });

  it("besmislena oznaka → null (chip ostaje bez linka)", () => {
    const hit = resolveSamplerCigar("La Galera", "×2", sampler!.id);
    expect(hit).toBeNull();
  });
});
