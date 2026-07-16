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
});
