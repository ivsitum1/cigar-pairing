import { describe, expect, it } from "vitest";
import {
  drinkBuyLink,
  isDrinkProductUrl,
  urlMatchesDrinkName,
} from "./drinkBuyLink";
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

describe("isDrinkProductUrl", () => {
  it("prihvaca allez / ecuga product path", () => {
    expect(
      isDrinkProductUrl(
        "https://allez.hr/shop/svi-proizvodi/hampden-hlcf-classic-estate-pure-single-jamaican-rum-60-vol-07l-u-poklon-kutiji",
      ),
    ).toBe(true);
    expect(isDrinkProductUrl("https://ecuga.com/proizvod/courvoisier-xo")).toBe(true);
  });

  it("odbija katalog / kategoriju", () => {
    expect(isDrinkProductUrl("https://ecuga.com/katalog/rum")).toBe(false);
    expect(isDrinkProductUrl("https://www.vivat-finavina.hr/vrsta/port/")).toBe(false);
    expect(isDrinkProductUrl("https://dingac.hr/webshop/")).toBe(false);
  });
});

describe("urlMatchesDrinkName", () => {
  it("prihvaca ociti match", () => {
    expect(
      urlMatchesDrinkName(
        "Hampden HLCF Classic 60%",
        "https://allez.hr/shop/svi-proizvodi/hampden-hlcf-classic-estate-pure-single-jamaican-rum-60-vol-07l-u-poklon-kutiji",
      ),
    ).toBe(true);
  });

  it("odbija krivi proizvod iste marke", () => {
    expect(
      urlMatchesDrinkName(
        "Havana Club Tributo",
        "https://allez.hr/shop/svi-proizvodi/havana-club-gran-reserva-anejo-15-anos-40-vol-07l-u-poklon-kutiji",
      ),
    ).toBe(false);
    expect(
      urlMatchesDrinkName(
        "Frapin Château de Fontpinot XO",
        "https://ecuga.com/proizvod/frapin-vip-xo",
      ),
    ).toBe(false);
  });

  it("odbija krivu godinu / batch", () => {
    expect(
      urlMatchesDrinkName(
        "Laphroaig 25 YO 2019",
        "https://allez.hr/shop/svi-proizvodi/laphroaig-25-years-old-islay-single-malt-scotch-whisky-2018-52-vol-07l-in-wooden-case",
      ),
    ).toBe(false);
    expect(
      urlMatchesDrinkName(
        "Ardbeg TRAIGH BHAN 19 YO Batch No. 4",
        "https://allez.hr/shop/svi-proizvodi/ardbeg-traigh-bhan-19-yo-islay-single-malt-scotch-whisky-batch-no-2-462-vol-07l-u-poklon-kutiji",
      ),
    ).toBe(false);
  });
});

describe("drinkBuyLink", () => {
  it("pada na search kad je priceUrl kategorija", () => {
    const d = base({
      name: "Appleton Estate 15 Black River",
      priceUrl: "https://ecuga.com/katalog/rum",
      shopHR: "ecuga.com",
    });
    const link = drinkBuyLink(d);
    expect(link.label).toBe("search");
    expect(link.href).toContain("google.com/search");
    expect(link.href).toContain(encodeURIComponent("Appleton Estate 15 Black River"));
  });

  it("pada na search kad slug ne odgovara imenu", () => {
    const d = base({
      name: "Havana Club Tributo",
      priceUrl:
        "https://allez.hr/shop/svi-proizvodi/havana-club-gran-reserva-anejo-15-anos-40-vol-07l-u-poklon-kutiji",
      shopHR: "allez.hr",
    });
    expect(drinkBuyLink(d).label).toBe("search");
  });

  it("zadrzava buy kad se shop i slug slazu", () => {
    const d = base({
      name: "Hampden HLCF Classic 60%",
      priceUrl:
        "https://allez.hr/shop/svi-proizvodi/hampden-hlcf-classic-estate-pure-single-jamaican-rum-60-vol-07l-u-poklon-kutiji",
      shopHR: "allez.hr",
    });
    const link = drinkBuyLink(d);
    expect(link.label).toBe("buy");
    expect(link.href).toContain("hampden-hlcf-classic");
  });

  it("pada na search kad shopHR nije isti domain kao URL", () => {
    const d = base({
      name: "Hampden HLCF Classic 60%",
      priceUrl:
        "https://allez.hr/shop/svi-proizvodi/hampden-hlcf-classic-estate-pure-single-jamaican-rum-60-vol-07l-u-poklon-kutiji",
      shopHR: "Lidl",
    });
    expect(drinkBuyLink(d).label).toBe("search");
  });
});
