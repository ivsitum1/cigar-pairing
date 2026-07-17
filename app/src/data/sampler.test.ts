import { describe, it, expect } from "vitest";
import { ALL_DRINKS, CIGARS, cigarById } from "./index";
import { pairDrinksForCigar } from "../engine/pairing";

const samplers = CIGARS.filter((c) => c.sampler);

describe("sampler vodici", () => {
  it("svaki sampler u katalogu ima vodic", () => {
    const flagged = CIGARS.filter(
      (c) => /sampler|gift pack/i.test(c.line) && c.profileEstimated,
    );
    for (const s of flagged) {
      expect(s.sampler, `${s.id} nema sampler vodic`).toBeDefined();
    }
    expect(samplers.length).toBeGreaterThanOrEqual(8);
  });

  it("sve stavke referenciraju postojece cigare iz kataloga", () => {
    for (const s of samplers) {
      expect(s.sampler!.items.length, s.id).toBeGreaterThanOrEqual(3);
      for (const it of s.sampler!.items) {
        const c = cigarById(it.cigarId);
        expect(c, `${s.id} -> ${it.cigarId}`).toBeDefined();
        expect(c!.sampler, `${it.cigarId} je i sam sampler`).toBeUndefined();
      }
    }
  });

  it("svaka stavka ima dvojezicni tip pusaca i hostNote", () => {
    for (const s of samplers) {
      expect(s.sampler!.hostNote.hr.length, s.id).toBeGreaterThan(20);
      expect(s.sampler!.hostNote.en.length, s.id).toBeGreaterThan(20);
      // nepotvrdjen sastav mora to i reci
      if (!s.sampler!.confirmed) {
        expect(s.sampler!.hostNote.hr).toMatch(/provjeri/i);
      }
      for (const it of s.sampler!.items) {
        expect(it.smokerType.hr.length, it.cigarId).toBeGreaterThan(10);
        expect(it.smokerType.en.length, it.cigarId).toBeGreaterThan(10);
      }
    }
  });

  it("engine daje pice za svaku stavku, raznolikost unutar samplera postoji", () => {
    for (const s of samplers) {
      const strengths = new Set<number>();
      const bodies = new Set<number>();
      for (const it of s.sampler!.items) {
        const c = cigarById(it.cigarId)!;
        strengths.add(c.strength);
        bodies.add(c.body);
        const top = pairDrinksForCigar(c, ALL_DRINKS)[0];
        expect(top, `${s.id} -> ${it.cigarId}`).toBeDefined();
        expect(top.score).toBeGreaterThan(50);
      }
      // "za svakoga po nesto": kutija varira barem po snazi ili tijelu
      expect(
        Math.max(strengths.size, bodies.size),
        `${s.id} nema raznolikosti`,
      ).toBeGreaterThanOrEqual(2);
    }
  });
});
