import { describe, expect, it } from "vitest";
import {
  drinkAvailabilityHR,
  drinkPrimaryLink,
  drinkShopLinks,
  verifiedProductUrl,
} from "./drinkShopLinks";
import { DRINK_SHOPS } from "../data/drinkShops";
import type { Drink } from "../types";

const base = (over: Partial<Drink>): Drink =>
  ({
    id: "x",
    category: "rum",
    name: "Test",
    style: "jamaica",
    region: "JM",
    body: 3,
    sweetness: 2,
    flavorTags: [],
    qualityScore: 7,
    priceEUR: { min: 40, max: 40 },
    pairable: true,
    ...over,
  }) as Drink;

const HAMPDEN =
  "https://allez.hr/shop/svi-proizvodi/hampden-hlcf-classic-estate-pure-single-jamaican-rum-60-vol-07l-u-poklon-kutiji";

describe("registar trgovina pićem", () => {
  it("svaka trgovina ima https URL-ove i barem jedan način dolaska do boce", () => {
    for (const shop of DRINK_SHOPS) {
      expect(shop.home.startsWith("https://"), shop.id).toBe(true);
      const browse = Object.values(shop.browse ?? {});
      expect(shop.search != null || browse.length > 0, shop.id).toBe(true);
      for (const url of browse) expect(url.startsWith("https://"), `${shop.id} ${url}`).toBe(true);
      expect(shop.categories.length, shop.id).toBeGreaterThan(0);
    }
  });

  it("trgovina bez pretrage pokriva katalogom svaku kategoriju koju tvrdi", () => {
    for (const shop of DRINK_SHOPS) {
      if (shop.search) continue;
      for (const c of shop.categories) {
        expect(shop.browse?.[c], `${shop.id}/${c}`).toBeTruthy();
      }
    }
  });

  it("ID-jevi su jedinstveni", () => {
    const ids = DRINK_SHOPS.map((s) => s.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});

describe("drinkShopLinks", () => {
  it("potvrđena stranica boce ide prva i nosi ime svoje trgovine", () => {
    const links = drinkShopLinks(
      base({ name: "Hampden HLCF Classic 60%", priceUrl: HAMPDEN, shopHR: "allez.hr" }),
    );
    expect(links[0]).toMatchObject({ shopId: "allez", kind: "product", url: HAMPDEN });
    // ista trgovina se ne ponavlja kao katalog
    expect(links.filter((l) => l.shopId === "allez")).toHaveLength(1);
  });

  it("bez potvrđene stranice nudi trgovine s pretragom prije kataloga", () => {
    const links = drinkShopLinks(base({ name: "Doorly's 12", priceUrl: null }));
    expect(links.some((l) => l.kind === "product")).toBe(false);
    const hr = links.filter((l) => l.scope === "HR");
    const firstBrowse = hr.findIndex((l) => l.kind === "browse");
    const lastSearch = hr.map((l) => l.kind).lastIndexOf("search");
    expect(lastSearch).toBeGreaterThanOrEqual(0);
    expect(firstBrowse).toBeGreaterThan(lastSearch);
  });

  it("pretraga nosi očišćeno ime boce", () => {
    const links = drinkShopLinks(
      base({ name: "Hampden HLCF Classic (60%)", priceUrl: null }),
    );
    const tipsy = links.find((l) => l.shopId === "tipsy");
    expect(tipsy?.url).toContain("tipsy.hr/?s=");
    expect(decodeURIComponent(tipsy!.url)).toContain("Hampden HLCF Classic");
    expect(tipsy!.url).not.toContain("%25"); // postotak alkohola ispada iz upita
  });

  it("kategorijski URL u priceUrl ne prolazi kao potvrđena boca", () => {
    const d = base({ name: "Appleton Estate 15", priceUrl: "https://ecuga.com/katalog/rum" });
    expect(verifiedProductUrl(d)).toBeNull();
    expect(drinkShopLinks(d).some((l) => l.kind === "product")).toBe(false);
  });

  it("svjetski cjenik je zadnji i vodi na Wine-Searcher", () => {
    const links = drinkShopLinks(base({ name: "H by Hine VSOP", category: "brandy" }));
    const last = links[links.length - 1]!;
    expect(last.kind).toBe("ref");
    expect(last.url).toBe("https://www.wine-searcher.com/find/H+by+Hine+VSOP");
  });

  it("vino dobiva vinoteke, ne kataloge žestice", () => {
    const links = drinkShopLinks(base({ name: "Dingač Barrique", category: "wine" }));
    const ids = links.map((l) => l.shopId);
    expect(ids).toContain("vivat");
    expect(ids).not.toContain("allez");
  });

  it("kava nema HR trgovinu u registru — lista je prazna", () => {
    expect(drinkShopLinks(base({ name: "Cogito Bourbon", category: "coffee" }))).toEqual([]);
  });

  it("ne pretrpava karticu — najviše pet HR poveznica", () => {
    for (const category of ["rum", "whisky", "gin", "brandy", "tequila", "wine"] as const) {
      const links = drinkShopLinks(base({ name: "Neka boca", category, priceUrl: null }));
      expect(links.filter((l) => l.scope === "HR").length, category).toBeLessThanOrEqual(5);
    }
  });

  it("svi linkovi su https i bez razmaka", () => {
    const links = drinkShopLinks(base({ name: "Plantation O.F.T.D. 69%", priceUrl: null }));
    for (const l of links) {
      expect(l.url.startsWith("https://"), l.url).toBe(true);
      expect(l.url).not.toContain(" ");
    }
  });
});

describe("drinkPrimaryLink", () => {
  it("bira potvrđenu bocu kad postoji", () => {
    const link = drinkPrimaryLink(
      base({ name: "Hampden HLCF Classic 60%", priceUrl: HAMPDEN }),
    );
    expect(link).toEqual({ href: HAMPDEN, kind: "product" });
  });

  it("bez trgovine za kategoriju pada na web pretragu", () => {
    const link = drinkPrimaryLink(base({ name: "Cogito Bourbon", category: "coffee" }));
    expect(link.kind).toBe("web");
    expect(link.href).toContain("google.com/search");
  });

  it("inače vodi u HR trgovinu, ne na Google", () => {
    const link = drinkPrimaryLink(base({ name: "Doorly's 12", priceUrl: null }));
    expect(link.href).not.toContain("google.com");
    expect(link.kind).toBe("search");
  });
});

describe("drinkAvailabilityHR", () => {
  it("trgovina je potvrđena kad ista trgovina ima stranicu boce", () => {
    const a = drinkAvailabilityHR(
      base({ name: "Hampden HLCF Classic 60%", priceUrl: HAMPDEN, shopHR: "allez.hr" }),
    );
    expect(a).toEqual({ text: "allez.hr", verified: true });
  });

  it("zagrade u tekstu trgovine ne ruše poklapanje", () => {
    const a = drinkAvailabilityHR(
      base({ name: "Hampden HLCF Classic 60%", priceUrl: HAMPDEN, shopHR: "allez.hr (rijetko)" }),
    );
    expect(a?.verified).toBe(true);
  });

  it("bez potvrđene stranice ostaje orijentir", () => {
    expect(drinkAvailabilityHR(base({ shopHR: "allez.hr" }))?.verified).toBe(false);
    expect(
      drinkAvailabilityHR(base({ name: "Hampden HLCF Classic 60%", priceUrl: HAMPDEN, shopHR: "Lidl" }))
        ?.verified,
    ).toBe(false);
  });

  it("prazan shopHR ne daje redak", () => {
    expect(drinkAvailabilityHR(base({ shopHR: "  " }))).toBeNull();
  });
});
