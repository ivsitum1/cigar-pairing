// Indeks marki pića hrani pregled „Marke" u katalogu: kartica marke, deep-link
// `#/catalog/drink-brand/<slug>` i usporedna tablica. Kad se katalog regenerira,
// ovi guardovi hvataju tihe rupe — marku bez boca, slug koji se ne vraća,
// dvije marke na istom slugu.
import { describe, expect, it } from "vitest";
import {
  ALL_DRINK_BRANDS,
  DRINK_BRAND_CATALOG,
  drinkBrandFromSlug,
  drinkBrandSlug,
  drinkBrandStats,
  drinksByBrand,
} from "./index";

describe("indeks marki pića", () => {
  it("pokriva sve marke, jednom svaku", () => {
    expect(DRINK_BRAND_CATALOG.map((b) => b.brand)).toEqual(ALL_DRINK_BRANDS);
  });

  it("svaka marka ima boce, kategoriju i slug", () => {
    for (const b of DRINK_BRAND_CATALOG) {
      expect(b.count, b.brand).toBeGreaterThan(0);
      expect(b.categories.length, b.brand).toBeGreaterThan(0);
      expect(b.slug, b.brand).not.toBe("");
    }
  });

  it("broj boca odgovara popisu boca", () => {
    for (const b of DRINK_BRAND_CATALOG) {
      expect(drinksByBrand(b.brand).length, b.brand).toBe(b.count);
    }
  });

  // Slug je izveden iz imena; kolizija bi značila da jedna marka postane
  // nedohvatljiva deep-linkom, tiho, jer bi je druga preuzela.
  it("slugovi su jedinstveni", () => {
    const seen = new Map<string, string>();
    const collisions: string[] = [];
    for (const b of DRINK_BRAND_CATALOG) {
      const prev = seen.get(b.slug);
      if (prev) collisions.push(`${b.slug}: ${prev} / ${b.brand}`);
      else seen.set(b.slug, b.brand);
    }
    expect(collisions).toEqual([]);
  });

  it("slug se vraća u istu marku", () => {
    for (const b of ALL_DRINK_BRANDS) {
      expect(drinkBrandFromSlug(drinkBrandSlug(b)), b).toBe(b);
    }
  });

  it("nepoznat slug ne ruši nego vraća undefined", () => {
    expect(drinkBrandFromSlug("ne-postoji-takva-marka")).toBeUndefined();
    expect(drinkBrandFromSlug("")).toBeUndefined();
  });

  it("najbolja ocjena i najniža cijena su stvarno krajnosti", () => {
    for (const b of DRINK_BRAND_CATALOG) {
      const bottles = drinksByBrand(b.brand);
      const scores = bottles
        .map((d) => d.qualityScore)
        .filter((q): q is number => q != null);
      if (scores.length) expect(b.bestQuality, b.brand).toBe(Math.max(...scores));
      else expect(b.bestQuality, b.brand).toBeNull();

      const mins = bottles.map((d) => d.priceEUR?.min).filter((p): p is number => p != null);
      if (mins.length) expect(b.minPriceEUR, b.brand).toBe(Math.min(...mins));
      else expect(b.minPriceEUR, b.brand).toBeNull();
    }
  });

  // drinksByBrand vraća kopiju: sortiranje u pregledu ne smije preurediti
  // zajednički indeks pod nogama ostalih pozivatelja.
  it("popis boca je kopija, ne živi indeks", () => {
    const brand = ALL_DRINK_BRANDS.find((b) => drinksByBrand(b).length > 2)!;
    const first = drinksByBrand(brand);
    first.reverse();
    expect(drinksByBrand(brand).map((d) => d.id)).not.toEqual(first.map((d) => d.id));
  });

  it("nepoznata marka daje prazan, a ne bačen, rezultat", () => {
    expect(drinksByBrand("Nepostojeća")).toEqual([]);
    expect(drinkBrandStats("Nepostojeća").count).toBe(0);
  });
});
