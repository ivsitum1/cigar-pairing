import { describe, expect, it } from "vitest";
import cigarsData from "../data/cigars.json";
import type { Cigar } from "../types";
import {
  isSampler,
  samplerLabelCount,
  samplerParts,
  samplerPieceCount,
  unresolvedSamplerLabels,
} from "./samplerStock";

const cigars = cigarsData as Cigar[];
const byId = (id: string): Cigar => {
  const hit = cigars.find((c) => c.id === id);
  if (!hit) throw new Error(`nema ${id}`);
  return hit;
};

describe("prepoznavanje paketa", () => {
  it("paket ima popis sadržaja, obična linija nema", () => {
    expect(isSampler(byId("cig-aj-fernandez-toro-sampler"))).toBe(true);
    expect(isSampler(byId("cig-aj-fernandez-enclave"))).toBe(false);
  });

  it("čita količinu iz oznake", () => {
    expect(samplerLabelCount("Serie V Robusto")).toBe(1);
    expect(samplerLabelCount("Serie V Robusto ×2")).toBe(2);
    expect(samplerLabelCount("Serie V Robusto x3")).toBe(3);
    expect(samplerLabelCount("Serie V Robusto ×0")).toBe(1);
  });
});

describe("AJ Fernandez Toro Sampler", () => {
  const sampler = byId("cig-aj-fernandez-toro-sampler");

  it("razlaže se na pet Toro vitola iz kataloga", () => {
    const parts = samplerParts(sampler);
    expect(parts).toHaveLength(5);
    expect(parts.map((p) => p.itemId).sort()).toEqual([
      "cig-aj-fernandez-bellas-artes@hybrid-toro",
      "cig-aj-fernandez-enclave@connecticut-toro",
      "cig-aj-fernandez-new-world@oscuro-toro-redondo",
      "cig-aj-fernandez-new-world@puro-especial-toro",
      "cig-aj-fernandez-san-lotano@requiem-habano-toro",
    ]);
    expect(samplerPieceCount(sampler)).toBe(5);
  });

  it("nijedna oznaka ne ostaje nerazriješena", () => {
    expect(unresolvedSamplerLabels(sampler)).toEqual([]);
  });

  it("svaki dio je konkretna vitola, ne gola linija", () => {
    for (const part of samplerParts(sampler)) {
      expect(part.itemId, part.label).toContain("@");
      expect(part.cigar.selectedVitola, part.label).toBeTruthy();
      expect(part.count).toBe(1);
    }
  });
});

describe("svi paketi u katalogu", () => {
  const samplers = cigars.filter(isSampler);

  it("ima ih i svaki se razlaže na barem dvije vitole", () => {
    expect(samplers.length).toBeGreaterThan(0);
    for (const s of samplers) {
      expect(samplerParts(s).length, `${s.id} se ne razlaže`).toBeGreaterThanOrEqual(2);
    }
  });

  it("paket nikad ne sadrži samog sebe", () => {
    for (const s of samplers) {
      const ids = samplerParts(s).map((p) => p.itemId);
      expect(ids, s.id).not.toContain(s.id);
    }
  });
});
