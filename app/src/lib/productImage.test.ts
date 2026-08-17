import { describe, it, expect } from "vitest";
import { productImageUrl } from "./productImage";
import images from "../data/productImages.json";
import { CIGARS, ALL_DRINKS } from "../data";

describe("productImageUrl", () => {
  it("returns https shop photos for mapped cigars and drinks", () => {
    const cigarIds = Object.keys(images.cigars);
    const drinkIds = Object.keys(images.drinks);
    expect(cigarIds.length).toBeGreaterThan(0);
    expect(drinkIds.length).toBeGreaterThan(0);
    const cigarUrl = productImageUrl("cigar", cigarIds[0]!);
    const drinkUrl = productImageUrl("drink", drinkIds[0]!);
    expect(cigarUrl).toMatch(/^https:\/\//);
    expect(drinkUrl).toMatch(/^https:\/\//);
  });

  it("returns null for unknown ids", () => {
    expect(productImageUrl("cigar", "cig-does-not-exist")).toBeNull();
    expect(productImageUrl("drink", "wh-does-not-exist")).toBeNull();
  });

  it("only maps ids that exist in the app catalogs", () => {
    const cigarSet = new Set(CIGARS.map((c) => c.id));
    const drinkSet = new Set(ALL_DRINKS.map((d) => d.id));
    for (const id of Object.keys(images.cigars)) {
      expect(cigarSet.has(id), id).toBe(true);
      expect(images.cigars[id as keyof typeof images.cigars]).toMatch(/^https:\/\//);
    }
    for (const id of Object.keys(images.drinks)) {
      expect(drinkSet.has(id), id).toBe(true);
      expect(images.drinks[id as keyof typeof images.drinks]).toMatch(/^https:\/\//);
    }
  });
});
