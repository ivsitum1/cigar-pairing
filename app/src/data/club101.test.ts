import { describe, it, expect } from "vitest";
import club101 from "./club101.json";

const TRACKS = ["cigars", "drinks", "accessories", "tips"] as const;

describe("club 101 vodici", () => {
  it("ima cetiri trake s najmanje 6 kartica (tips 6+)", () => {
    for (const track of TRACKS) {
      const min = track === "tips" ? 6 : 7;
      expect(club101.tracks[track].length, track).toBeGreaterThanOrEqual(min);
    }
  });

  it("svaka kartica ima id i dvojezicni title/body", () => {
    for (const track of TRACKS) {
      for (const card of club101.tracks[track]) {
        expect(card.id.length, card.id).toBeGreaterThan(0);
        expect(card.title.hr.length && card.title.en.length, card.id).toBeTruthy();
        expect(card.body.hr.length && card.body.en.length, card.id).toBeTruthy();
      }
    }
  });

  it("shop linkovi su https kategorije kad postoje", () => {
    for (const track of TRACKS) {
      for (const card of club101.tracks[track]) {
        const links = "shopLinks" in card ? card.shopLinks : undefined;
        for (const link of links ?? []) {
          expect(link.url.startsWith("https://"), `${card.id} ${link.url}`).toBe(true);
          expect(link.url.includes("allez.hr/") || link.url.includes("humidor.hr/"), link.url).toBe(
            true,
          );
          // ne smiju biti goli homepage-i
          expect(link.url === "https://allez.hr" || link.url === "https://humidor.hr", link.url).toBe(
            false,
          );
          expect(link.label.hr.length && link.label.en.length, card.id).toBeTruthy();
        }
      }
    }
  });

  it("pribor traka pokriva casu, humidor, rezac, pepeljaru i dekanter", () => {
    const ids = club101.tracks.accessories.map((c) => c.id);
    expect(ids).toEqual(
      expect.arrayContaining(["a-glasses", "a-humidor", "a-cutter", "a-ashtray", "a-decanter"]),
    );
  });

  it("trikovitraka postoji", () => {
    expect(club101.tracks.tips.length).toBeGreaterThanOrEqual(6);
  });

  it("pica 101 pokriva gin, stolno vino, kavu i tekilu", () => {
    const drinkIds = club101.tracks.drinks.map((c) => c.id);
    expect(drinkIds).toEqual(
      expect.arrayContaining(["d-gin-pairing", "d-wine-table", "d-coffee", "d-tequila"]),
    );
    expect(club101.tracks.tips.map((c) => c.id)).toContain("t-coffee-espresso");
    expect(club101.tracks.tips.find((c) => c.id === "t-notebook")?.body.hr).toContain(
      "Predložak bilješke",
    );

    const wine = club101.tracks.drinks.find((c) => c.id === "d-wine-table");
    expect(wine?.body.hr.toLowerCase()).toMatch(/tanin/);
    expect(wine?.body.en.toLowerCase()).toMatch(/tannin/);

    const coffee = club101.tracks.drinks.find((c) => c.id === "d-coffee");
    expect(coffee?.body.hr.toLowerCase()).toMatch(/espresso/);
    expect(coffee?.body.en.toLowerCase()).toMatch(/espresso/);

    const tequila = club101.tracks.drinks.find((c) => c.id === "d-tequila");
    expect(tequila?.body.hr.toLowerCase()).toMatch(/blanco/);
    expect(tequila?.body.en.toLowerCase()).toMatch(/blanco/);
  });

  it("pica 101 pokriva biljne digestive", () => {
    const ids = club101.tracks.drinks.map((c) => c.id);
    expect(ids).toContain("d-digestif");
    const card = club101.tracks.drinks.find((c) => c.id === "d-digestif");
    expect(card?.body.hr.toLowerCase()).toMatch(/becherovka|pelinkovac|chartreuse|fernet/);
    expect(card?.body.en.toLowerCase()).toMatch(/becherovka|pelinkovac|chartreuse|fernet/);
    expect(card!.body.hr.length).toBeGreaterThanOrEqual(650);
    expect(card!.body.en.length).toBeGreaterThanOrEqual(650);
  });

  it("triple grill 2026-07-30: degustacijski redoslijed i higijena alata", () => {
    expect(club101.tracks.drinks.map((c) => c.id)).toContain("d-tasting-order");
    expect(club101.tracks.cigars.map((c) => c.id)).toContain("c-tool-hygiene");
    const tasting = club101.tracks.drinks.find((c) => c.id === "d-tasting-order");
    expect(tasting?.body.hr.toLowerCase()).toMatch(/blago|nepce|glencairn|voda/);
    expect(tasting?.body.en.toLowerCase()).toMatch(/milder|palate|glencairn|water/);
  });

  it("lekcije imaju katalog-dubinu (liste tipova / karakteristike)", () => {
    for (const track of TRACKS) {
      for (const card of club101.tracks[track]) {
        const min = track === "tips" ? 350 : 650;
        expect(card.body.hr.length, `${card.id} hr`).toBeGreaterThanOrEqual(min);
        expect(card.body.en.length, `${card.id} en`).toBeGreaterThanOrEqual(min);
        // bullet katalog ili numerirane tocke
        expect(
          /•|\n\d+\./.test(card.body.hr) && /•|\n\d+\./.test(card.body.en),
          card.id,
        ).toBe(true);
      }
    }
  });
});
