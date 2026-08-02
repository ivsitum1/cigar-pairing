import { describe, expect, it, beforeEach, vi } from "vitest";

function fakeStorage() {
  const map = new Map<string, string>();
  return {
    getItem: (k: string) => map.get(k) ?? null,
    setItem: (k: string, v: string) => void map.set(k, v),
    removeItem: (k: string) => void map.delete(k),
  };
}

beforeEach(() => {
  vi.resetModules();
  vi.stubGlobal("localStorage", fakeStorage());
});

const load = () => import("./favorites");

describe("omiljene marke", () => {
  it("prazno na pocetku", async () => {
    const { favoriteBrandsOf, isFavoriteBrand } = await load();
    expect(favoriteBrandsOf("cigar")).toEqual([]);
    expect(isFavoriteBrand("drink", "Foursquare")).toBe(false);
  });

  it("toggle ukljucuje pa iskljucuje", async () => {
    const { toggleFavoriteBrand, isFavoriteBrand } = await load();
    expect(toggleFavoriteBrand("drink", "Foursquare")).toBe(true);
    expect(isFavoriteBrand("drink", "Foursquare")).toBe(true);
    expect(toggleFavoriteBrand("drink", "Foursquare")).toBe(false);
    expect(isFavoriteBrand("drink", "Foursquare")).toBe(false);
  });

  // Ista marka moze postojati i kao cigara i kao pice — ne smiju se mijesati.
  it("cigare i pica su odvojeni prostori imena", async () => {
    const { toggleFavoriteBrand, isFavoriteBrand, favoriteBrandsOf } = await load();
    toggleFavoriteBrand("cigar", "Padrón");
    expect(isFavoriteBrand("drink", "Padrón")).toBe(false);
    expect(favoriteBrandsOf("cigar")).toEqual(["Padrón"]);
    expect(favoriteBrandsOf("drink")).toEqual([]);
  });

  it("popis je abecedan", async () => {
    const { toggleFavoriteBrand, favoriteBrandsOf } = await load();
    for (const b of ["Zacapa", "Ardbeg", "Foursquare"]) toggleFavoriteBrand("drink", b);
    expect(favoriteBrandsOf("drink")).toEqual(["Ardbeg", "Foursquare", "Zacapa"]);
  });

  it("preživi ponovno ucitavanje modula", async () => {
    const first = await load();
    first.toggleFavoriteBrand("drink", "Ardbeg");
    vi.resetModules();
    const second = await load();
    expect(second.isFavoriteBrand("drink", "Ardbeg")).toBe(true);
  });

  it("blokiran storage ne rusi nista", async () => {
    vi.stubGlobal("localStorage", {
      getItem: () => {
        throw new Error("SecurityError");
      },
      setItem: () => {
        throw new Error("SecurityError");
      },
      removeItem: () => {},
    });
    const { toggleFavoriteBrand, isFavoriteBrand } = await load();
    expect(() => toggleFavoriteBrand("drink", "Ardbeg")).not.toThrow();
    // u memoriji vrijedi i dalje, samo se ne pamti
    expect(isFavoriteBrand("drink", "Ardbeg")).toBe(true);
  });

  it("import odbija smece, prihvaca ispravne kljuceve", async () => {
    const { importFavorites, exportFavorites } = await load();
    expect(importFavorites("nije niz")).toBe(false);
    expect(importFavorites(["drink:Ardbeg", 42, "bez-prefiksa", "cigar:Oliva"])).toBe(
      true,
    );
    expect(exportFavorites()).toEqual(["cigar:Oliva", "drink:Ardbeg"]);
  });
});
