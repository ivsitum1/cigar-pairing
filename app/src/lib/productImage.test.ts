import { beforeEach, describe, expect, it, vi } from "vitest";

// Popis se puni skriptom i u repou zna biti prazan, pa se ovdje podmece
// nadomjestak — testira se ponasanje, ne trenutno stanje mape sa slikama.
vi.mock("../data/productImages.json", () => ({
  default: {
    generatedAt: "2026-08-17",
    cigars: {
      "cig-oliva-serie-v": { w: 800, h: 240, t: "cutout", s: "humidor.hr" },
      "cig-ambijent": { w: 640, h: 640, t: "framed", s: "allez.hr" },
      "cig-bez-izvora": { w: 600, h: 200, t: "cutout" },
      "cig-nepoznat-postupak": { w: 600, h: 200, t: "nesto-novo", s: "x.hr" },
    },
    drinks: {
      "rum-foursquare-ecs-detente-2005": { w: 300, h: 800, t: "cutout", s: "allez.hr" },
    },
  },
}));

const ucitaj = async () => await import("./productImage");

describe("put do slike", () => {
  beforeEach(() => vi.resetModules());

  it("slika ide kroz BASE_URL, ne kroz korijen", async () => {
    const { cigarImage } = await ucitaj();
    // BASE_URL je "/cigar-pairing/" — tvrdi "/img/..." dao bi 404 na Pagesu
    expect(cigarImage("cig-oliva-serie-v")?.src).toBe(
      `${import.meta.env.BASE_URL}img/products/cigars/cig-oliva-serie-v.webp`,
    );
  });

  it("pića imaju svoju mapu", async () => {
    const { drinkImage } = await ucitaj();
    expect(drinkImage("rum-foursquare-ecs-detente-2005")?.src).toContain(
      "img/products/drinks/rum-foursquare-ecs-detente-2005.webp",
    );
  });

  it("nosi dimenzije, da kartica rezervira prostor prije učitavanja", async () => {
    const { cigarImage } = await ucitaj();
    const slika = cigarImage("cig-oliva-serie-v");
    expect(slika?.width).toBe(800);
    expect(slika?.height).toBe(240);
  });
});

describe("kad slike nema", () => {
  beforeEach(() => vi.resetModules());

  it("nepoznat id ne ruši ništa — kartica se crta bez slike", async () => {
    const { cigarImage, drinkImage } = await ucitaj();
    expect(cigarImage("cig-nema-me")).toBeNull();
    expect(drinkImage("rum-nema-me")).toBeNull();
  });

  it("prazan id se ne pretvara u put", async () => {
    const { cigarImage } = await ucitaj();
    expect(cigarImage(undefined)).toBeNull();
    expect(cigarImage("")).toBeNull();
  });
});

describe("postupak obrade", () => {
  beforeEach(() => vi.resetModules());

  it("razlikuje izrezanu sliku od one u okviru", async () => {
    const { cigarImage } = await ucitaj();
    expect(cigarImage("cig-oliva-serie-v")?.treatment).toBe("cutout");
    expect(cigarImage("cig-ambijent")?.treatment).toBe("framed");
  });

  it("nepoznata oznaka pada na izrez, ne na okvir", async () => {
    // Okvir je vidljiv zahvat; kad popis kaže nešto nepoznato, tiši je izbor.
    const { cigarImage } = await ucitaj();
    expect(cigarImage("cig-nepoznat-postupak")?.treatment).toBe("cutout");
  });

  it("izvor bez domene daje prazan potpis, ne 'undefined'", async () => {
    const { cigarImage } = await ucitaj();
    expect(cigarImage("cig-bez-izvora")?.source).toBe("");
  });
});
