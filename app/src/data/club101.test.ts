import { describe, it, expect } from "vitest";
import club101 from "./club101.json";

const TRACKS = ["cigars", "drinks", "accessories"] as const;

describe("club 101 vodici", () => {
  it("ima tri trake s najmanje 4 kartice", () => {
    for (const track of TRACKS) {
      expect(club101.tracks[track].length, track).toBeGreaterThanOrEqual(4);
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

  it("shop linkovi su https kad postoje", () => {
    for (const track of TRACKS) {
      for (const card of club101.tracks[track]) {
        const links = "shopLinks" in card ? card.shopLinks : undefined;
        for (const link of links ?? []) {
          expect(link.url.startsWith("https://"), `${card.id} ${link.url}`).toBe(true);
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
});
