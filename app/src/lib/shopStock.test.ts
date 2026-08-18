import { describe, expect, it } from "vitest";
import type { Cigar, Drink } from "../types";
import {
  cigarLinkStock,
  drinkStockView,
  stockView,
  urlsMatch,
} from "./shopStock";

const cigar = (extra: Partial<Cigar> = {}): Cigar =>
  ({
    id: "cig-test",
    brand: "Test",
    line: "Line",
    vitola: "Robusto",
    format: "50 x 127mm",
    country: "Nikaragva",
    wrapper: "Habano",
    strength: 3,
    body: 3,
    flavorTags: [],
    smokeTimeMin: 50,
    priceEUR: null,
    vitolas: [],
    markets: ["HR"],
    availabilityHR: [],
    notes: { hr: "", en: "" },
    ...extra,
  }) as Cigar;

const drink = (extra: Partial<Drink> = {}): Drink =>
  ({
    id: "d-test",
    category: "rum",
    name: "Hampden HLCF Classic 60%",
    style: "jamaica",
    region: "JM",
    body: 3,
    sweetness: 2,
    flavorTags: [],
    qualityScore: 7,
    priceEUR: { min: 40, max: 40 },
    pairable: true,
    serving: { best: "neat" },
    notes: { hr: "", en: "" },
    shopHR: "allez.hr",
    ...extra,
  }) as Drink;

const HUMIDOR = "https://humidor.hr/hr/product/padron-1964";
const ALLEZ =
  "https://allez.hr/shop/svi-proizvodi/hampden-hlcf-classic-estate-pure-single-jamaican-rum-60-vol-07l-u-poklon-kutiji";

describe("urlsMatch", () => {
  it("ignores trailing slash and fragment", () => {
    expect(urlsMatch(HUMIDOR + "/", HUMIDOR + "#x")).toBe(true);
    expect(urlsMatch(HUMIDOR, "https://famous-smoke.com/x")).toBe(false);
    expect(urlsMatch(null, HUMIDOR)).toBe(false);
  });
});

describe("stockView", () => {
  it("returns null when stock was never pinged", () => {
    expect(stockView(undefined, undefined)).toBeNull();
    expect(stockView(undefined, "2026-08-17")).toBeNull();
  });

  it("returns in-stock when pinged recently", () => {
    const now = Date.parse("2026-08-17T12:00:00Z");
    expect(stockView(true, "2026-08-16", now)).toEqual({
      inStock: true,
      stale: false,
      fetchedAt: "2026-08-16",
    });
  });

  it("marks stock stale after 14 days", () => {
    const now = Date.parse("2026-08-17T12:00:00Z");
    expect(stockView(false, "2026-07-01", now)).toEqual({
      inStock: false,
      stale: true,
      fetchedAt: "2026-07-01",
    });
  });
});

describe("cigarLinkStock", () => {
  it("reads inStock from the vitola that owns the product URL", () => {
    const c = cigar({
      vitolas: [
        {
          name: "Robusto",
          format: null,
          smokeTimeMin: null,
          priceEUR: 9.5,
          url: HUMIDOR,
          inStock: true,
          stockFetchedAt: "2026-08-17",
        },
        {
          name: "Toro",
          format: null,
          smokeTimeMin: null,
          priceEUR: 11,
          url: "https://humidor.hr/other",
          inStock: false,
          stockFetchedAt: "2026-08-17",
        },
      ],
    });
    expect(cigarLinkStock(c, HUMIDOR + "/")).toEqual({
      inStock: true,
      stockFetchedAt: "2026-08-17",
    });
    expect(cigarLinkStock(c, "https://humidor.hr/missing")).toBeNull();
  });

  it("reads inStock from regionLinks when the vitola URL is absent", () => {
    const c = cigar({
      regionLinks: {
        USA: {
          shop: "Famous Smoke",
          url: "https://www.famous-smoke.com/padron-1964",
          inStock: false,
          stockFetchedAt: "2026-08-10",
        },
      },
    });
    expect(cigarLinkStock(c, "https://www.famous-smoke.com/padron-1964")).toEqual({
      inStock: false,
      stockFetchedAt: "2026-08-10",
    });
  });
});

describe("drinkStockView", () => {
  it("shows stock only on a confirmed product page", () => {
    const now = Date.parse("2026-08-17T12:00:00Z");
    expect(
      drinkStockView(
        drink({ priceUrl: ALLEZ, inStock: true, stockFetchedAt: "2026-08-16" }),
        now,
      ),
    ).toEqual({ inStock: true, stale: false, fetchedAt: "2026-08-16" });
    expect(
      drinkStockView(drink({ shopHR: "allez.hr", inStock: true, stockFetchedAt: "2026-08-16" }), now),
    ).toBeNull();
  });
});
