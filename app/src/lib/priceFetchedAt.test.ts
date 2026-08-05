import { describe, it, expect } from "vitest";
import { CIGARS } from "../data";
import { cigarPriceForMarket, cigarLatestFetchedAt } from "../data";
import type { Cigar } from "../types";

const YYYY_MM_DD = /^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$/;

// Minimal stub cigar for unit tests.
function makeStub(overrides: Partial<Cigar> = {}): Cigar {
  return {
    id: "test-cigar",
    brand: "TestBrand",
    line: "TestLine",
    vitola: "Robusto",
    format: "50 x 127mm",
    country: "Nikaragva",
    wrapper: "Natural",
    strength: 3,
    body: 3,
    flavorTags: [],
    smokeTimeMin: 45,
    priceEUR: null,
    availabilityHR: [],
    notes: { hr: "", en: "" },
    markets: ["HR"],
    vitolas: [],
    ...overrides,
  };
}

describe("fetchedAt format", () => {
  it("every fetchedAt on vitolas matches YYYY-MM-DD", () => {
    const bad: string[] = [];
    for (const c of CIGARS) {
      for (const v of c.vitolas ?? []) {
        if (v.fetchedAt && !YYYY_MM_DD.test(v.fetchedAt)) {
          bad.push(`${c.id} vitola "${v.name}": ${v.fetchedAt}`);
        }
      }
    }
    expect(bad).toEqual([]);
  });

  it("every fetchedAt on regionLinks matches YYYY-MM-DD", () => {
    const bad: string[] = [];
    for (const c of CIGARS) {
      for (const region of ["HR", "EU", "USA"] as const) {
        const fa = c.regionLinks?.[region]?.fetchedAt;
        if (fa && !YYYY_MM_DD.test(fa)) {
          bad.push(`${c.id} regionLinks.${region}: ${fa}`);
        }
      }
      for (const v of c.vitolas ?? []) {
        for (const region of ["HR", "EU", "USA"] as const) {
          const fa = v.regionLinks?.[region]?.fetchedAt;
          if (fa && !YYYY_MM_DD.test(fa)) {
            bad.push(`${c.id} vitola "${v.name}" regionLinks.${region}: ${fa}`);
          }
        }
      }
    }
    expect(bad).toEqual([]);
  });

  it("no fetchedAt is in the future", () => {
    const today = new Date().toISOString().slice(0, 10);
    const future: string[] = [];
    for (const c of CIGARS) {
      for (const v of c.vitolas ?? []) {
        if (v.fetchedAt && v.fetchedAt > today) {
          future.push(`${c.id} vitola "${v.name}": ${v.fetchedAt}`);
        }
      }
      for (const region of ["HR", "EU", "USA"] as const) {
        const fa = c.regionLinks?.[region]?.fetchedAt;
        if (fa && fa > today) {
          future.push(`${c.id} regionLinks.${region}: ${fa}`);
        }
      }
    }
    expect(future).toEqual([]);
  });
});

describe("cigarPriceForMarket fetchedAt passthrough", () => {
  it("passes fetchedAt from regionLinks.EU", () => {
    const c = makeStub({
      markets: ["EU"],
      regionLinks: {
        EU: { shop: "CigarWorld", url: "https://example.com", priceEUR: 12.5, fetchedAt: "2026-07-01" },
      },
    });
    const result = cigarPriceForMarket(c, "EU");
    expect(result.fetchedAt).toBe("2026-07-01");
    expect(result.price).toBe(12.5);
  });

  it("passes fetchedAt from regionLinks.USA", () => {
    const c = makeStub({
      markets: ["USA"],
      regionLinks: {
        USA: { shop: "Holt's", url: "https://holts.com", priceEUR: 10, fetchedAt: "2026-06-15" },
      },
    });
    const result = cigarPriceForMarket(c, "USA");
    expect(result.fetchedAt).toBe("2026-06-15");
  });

  it("passes fetchedAt from default vitola for HR", () => {
    const c = makeStub({
      markets: ["HR"],
      vitolas: [
        { name: "Robusto", format: "50 x 127mm", smokeTimeMin: 45, priceEUR: 9.5, url: "https://humidor.hr/r", fetchedAt: "2026-05-20" },
      ],
    });
    const result = cigarPriceForMarket(c, "HR");
    expect(result.fetchedAt).toBe("2026-05-20");
    expect(result.price).toBe(9.5);
  });

  it("returns undefined fetchedAt when no vitola fetchedAt set", () => {
    const c = makeStub({
      markets: ["HR"],
      vitolas: [
        { name: "Robusto", format: "50 x 127mm", smokeTimeMin: 45, priceEUR: 9.5, url: null },
      ],
    });
    const result = cigarPriceForMarket(c, "HR");
    expect(result.fetchedAt).toBeUndefined();
  });

  it("returns no price and no fetchedAt for unpriced EU cigar", () => {
    const c = makeStub({ markets: ["EU"] });
    const result = cigarPriceForMarket(c, "EU");
    expect(result.price).toBeNull();
    expect(result.fetchedAt).toBeUndefined();
  });
});

describe("cigarLatestFetchedAt", () => {
  it("returns undefined when no dates present", () => {
    const c = makeStub({
      vitolas: [{ name: "Robusto", format: null, smokeTimeMin: null, priceEUR: null, url: null }],
    });
    expect(cigarLatestFetchedAt(c)).toBeUndefined();
  });

  it("returns the latest date across multiple sources", () => {
    const c = makeStub({
      markets: ["HR", "EU"],
      vitolas: [
        { name: "Robusto", format: null, smokeTimeMin: null, priceEUR: 10, url: null, fetchedAt: "2026-04-01" },
        { name: "Churchill", format: null, smokeTimeMin: null, priceEUR: 15, url: null, fetchedAt: "2026-07-15" },
      ],
      regionLinks: {
        EU: { shop: "CigarWorld", url: "https://example.com", priceEUR: 12, fetchedAt: "2026-06-01" },
      },
    });
    expect(cigarLatestFetchedAt(c)).toBe("2026-07-15");
  });
});
