import { describe, it, expect } from "vitest";
import { productImageUrl, productPhoto } from "./productImage";
import images from "../data/productImages.json";
import local from "../data/productImagesLocal.json";
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

  it("maps 1502 Black Gold from the Humidor product photo used on the detail sheet", () => {
    expect(productImageUrl("cigar", "cig-1502-black-gold")).toMatch(
      /^https:\/\/humidor\.hr\//,
    );
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

describe("productPhoto — obrađena slika ispred dućanske", () => {
  it("bez obrađene inačice vraća dućanski URL i označi ga kao neobrađen", () => {
    // Ovo je stanje svake stavke koja još nije prošla obradu: kartica ima
    // sliku, samo joj podloga nije ujednačena. Traži se id kojeg NEMA u
    // obrađenom popisu — inače bi test mjerio obrađenu granu i prolazio lažno.
    const obradjeni = new Set(
      Object.keys((local as { cigars?: Record<string, unknown> }).cigars ?? {}),
    );
    const id = Object.keys(images.cigars).find((i) => !obradjeni.has(i));
    expect(id, "svaka cigara je obrađena — test više ne pokriva dućanski sloj").toBeDefined();
    const photo = productPhoto("cigar", id!);
    expect(photo?.src).toMatch(/^https:\/\//);
    expect(photo?.treatment).toBe("remote");
  });

  it("nepoznat id ne daje sliku ni na jednom sloju", () => {
    expect(productPhoto("cigar", "cig-does-not-exist")).toBeNull();
    expect(productPhoto("drink", "wh-does-not-exist")).toBeNull();
  });

  it("prazan id se ne pretvara u put", () => {
    expect(productPhoto("cigar", undefined)).toBeNull();
    expect(productPhoto("cigar", "")).toBeNull();
  });

  it("obrađene slike, kad ih ima, idu kroz BASE_URL i nose dimenzije", () => {
    // Popis je u repou prazan dok se obrada ne pokrene — test tada provjerava
    // samo da je prazan, a čim slike stignu provjerava njihov oblik.
    const cigars = (local as { cigars?: Record<string, { w: number; h: number; t: string }> })
      .cigars;
    const ids = Object.keys(cigars ?? {});
    if (ids.length === 0) {
      expect(ids).toEqual([]);
      return;
    }
    const photo = productPhoto("cigar", ids[0]!);
    expect(photo?.src).toContain(`${import.meta.env.BASE_URL}img/products/cigars/`);
    expect(photo?.src.endsWith(".webp")).toBe(true);
    expect(["cutout", "framed"]).toContain(photo?.treatment);
    expect(photo?.width).toBeGreaterThan(0);
    expect(photo?.height).toBeGreaterThan(0);
  });

  it("obrađeni popis ne smije spominjati id koji katalog ne zna", () => {
    const cigarSet = new Set(CIGARS.map((c) => c.id));
    const drinkSet = new Set(ALL_DRINKS.map((d) => d.id));
    const maps = local as {
      cigars?: Record<string, unknown>;
      drinks?: Record<string, unknown>;
    };
    for (const id of Object.keys(maps.cigars ?? {})) expect(cigarSet.has(id), id).toBe(true);
    for (const id of Object.keys(maps.drinks ?? {})) expect(drinkSet.has(id), id).toBe(true);
  });
});
