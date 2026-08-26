import { describe, expect, it } from "vitest";
import type { Cigar, Vitola } from "../types";
import {
  cigarAvailableInRegion,
  cigarCatalogProof,
  cigarShelfStatus,
} from "./cigarAvailability";
import { cigarShopLinks, CIGARS } from "../data";

const vitola = (partial: Partial<Vitola> & Pick<Vitola, "name">): Vitola => ({
  format: null,
  smokeTimeMin: null,
  priceEUR: null,
  url: null,
  ...partial,
});

const stub = (overrides: Partial<Cigar> = {}): Cigar => ({
  id: "cig-stub",
  brand: "Stub",
  line: "Line",
  vitola: "Robusto",
  format: "50 x 127mm",
  country: "NI",
  wrapper: "Habano",
  strength: 3,
  body: 3,
  flavorTags: [],
  smokeTimeMin: 60,
  priceEUR: null,
  vitolas: [],
  markets: ["WW"],
  availabilityHR: [],
  notes: { hr: "", en: "" },
  ...overrides,
});

describe("cigarCatalogProof", () => {
  it("product — HR humidor URL", () => {
    const c = stub({
      markets: ["HR"],
      priceUrl: "https://humidor.hr/product/foo",
      vitolas: [
        vitola({
          name: "Robusto",
          url: "https://humidor.hr/product/foo",
        }),
      ],
    });
    expect(cigarCatalogProof(c, "HR")).toBe("product");
  });

  it("product — availabilityHR online shop bez URL-a", () => {
    const c = stub({
      markets: ["HR"],
      availabilityHR: ["The Humidor"],
    });
    expect(cigarCatalogProof(c, "HR")).toBe("product");
  });

  it("walkin — samo Tobacco Petica", () => {
    const c = stub({
      markets: ["HR"],
      availabilityHR: ["Tobacco Petica (Branimir)"],
    });
    expect(cigarCatalogProof(c, "HR")).toBe("walkin");
  });

  it("line — Holt's brand listing", () => {
    const c = stub({
      markets: ["USA"],
      regionLinks: {
        USA: {
          shop: "Holt's",
          url: "https://www.holts.com/cigars/all-cigar-brands/oliva.html",
        },
      },
    });
    expect(cigarCatalogProof(c, "USA")).toBe("line");
  });

  it("product — CigarWorld regionLinks", () => {
    const c = stub({
      markets: ["EU"],
      regionLinks: {
        EU: {
          shop: "CigarWorld",
          url: "https://www.cigarworld.de/en/oliva-serie-v",
        },
      },
    });
    expect(cigarCatalogProof(c, "EU")).toBe("product");
  });

  it("none — WW-only bez dokaza", () => {
    const c = stub({ markets: ["WW"] });
    expect(cigarCatalogProof(c, "HR")).toBe("none");
    expect(cigarCatalogProof(c, "EU")).toBe("none");
    expect(cigarCatalogProof(c, "USA")).toBe("none");
  });
});

describe("cigarAvailableInRegion", () => {
  it("ALL uvijek true", () => {
    expect(cigarAvailableInRegion(stub(), "ALL")).toBe(true);
  });

  it("HR filter ne propušta WW-only", () => {
    expect(cigarAvailableInRegion(stub({ markets: ["WW"] }), "HR")).toBe(false);
  });

  it("HR filter propušta walk-in dokaz", () => {
    const c = stub({
      availabilityHR: ["Aficionado"],
      markets: ["HR"],
    });
    expect(cigarAvailableInRegion(c, "HR")).toBe(true);
  });

  it("out-of-stock i dalje available", () => {
    const c = stub({
      markets: ["HR"],
      priceUrl: "https://humidor.hr/product/foo",
      inStock: false,
      stockFetchedAt: "2026-08-20",
      vitolas: [
        vitola({
          name: "Robusto",
          url: "https://humidor.hr/product/foo",
          inStock: false,
          stockFetchedAt: "2026-08-20",
        }),
      ],
    });
    expect(cigarAvailableInRegion(c, "HR")).toBe(true);
    expect(cigarShelfStatus(c, "HR")).toBe("out_of_stock");
  });

  it("in_stock kad ping kaže true", () => {
    const c = stub({
      markets: ["HR"],
      priceUrl: "https://humidor.hr/product/bar",
      vitolas: [
        vitola({
          name: "Robusto",
          url: "https://humidor.hr/product/bar",
          inStock: true,
          stockFetchedAt: "2026-08-20",
        }),
      ],
    });
    expect(cigarShelfStatus(c, "HR")).toBe("in_stock");
  });
});

describe("cigarShopLinks — bez lažne pretrage", () => {
  it("EU s samo CigarWorld productom nema C.Gars / La Couronne search", () => {
    const c = stub({
      markets: ["EU"],
      regionLinks: {
        EU: {
          shop: "CigarWorld",
          url: "https://www.cigarworld.de/en/only-cw",
        },
      },
    });
    const shops = cigarShopLinks(c).map((l) => l.shop);
    expect(shops).toContain("CigarWorld");
    expect(shops).not.toContain("C.Gars Ltd");
    expect(shops).not.toContain("La Couronne");
    expect(cigarShopLinks(c).every((l) => l.kind !== "search")).toBe(true);
  });

  it("katalog: EU-only CigarWorld linija nema search gumbe za druge EU shopove", () => {
    const euOnly = CIGARS.find(
      (c) =>
        c.markets.includes("EU") &&
        c.regionLinks?.EU?.url?.includes("cigarworld.de") &&
        !c.markets.includes("HR") &&
        !(c.vitolas ?? []).some((v) =>
          Object.values(v.regionLinks ?? {}).some(
            (l) =>
              l?.url?.includes("cgarsltd") || l?.url?.includes("cigarpassion"),
          ),
        ) &&
        !c.regionLinks?.EU?.url?.includes("cgarsltd") &&
        !c.regionLinks?.EU?.url?.includes("cigarpassion"),
    );
    expect(euOnly).toBeDefined();
    const euLinks = cigarShopLinks(euOnly!).filter((l) => l.region === "EU");
    expect(euLinks.some((l) => l.shop === "CigarWorld")).toBe(true);
    expect(euLinks.every((l) => l.kind !== "search")).toBe(true);
    expect(euLinks.map((l) => l.shop)).not.toContain("C.Gars Ltd");
    expect(euLinks.map((l) => l.shop)).not.toContain("La Couronne");
  });
});
