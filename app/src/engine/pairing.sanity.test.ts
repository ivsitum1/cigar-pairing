// Sanity provjere logike matchanja nad stvarnim podacima.
// Labavi pragovi — cuvaju smjer enginea (klasicni parovi visoko, promasaji
// nisko, zdrava distribucija), ne tocne brojke.
import { describe, it, expect } from "vitest";
import { ALL_DRINKS, CIGARS, cigarById } from "../data";
import { pairCigarsForDrink, scorePairing } from "./pairing";
import { curatedPairingOpinion } from "./curatedOpinion";
import type { Cigar, Drink } from "../types";

const meanScoreFor = (cigar: Cigar, drinks: Drink[]) => {
  const list = drinks.map((d) => scorePairing(cigar, d).score);
  return list.reduce((s, x) => s + x, 0) / Math.max(list.length, 1);
};
const byStyle = (re: RegExp) => ALL_DRINKS.filter((d) => re.test(d.style));

describe("sanity logike matchanja", () => {
  it("klasicni parovi rangiraju iznad promasaja", () => {
    const padron = cigarById("cig-padron-1964")!; // maduro s4 b4
    expect(meanScoreFor(padron, byStyle(/port-tawny|sherry-sweet/)))
      .toBeGreaterThan(meanScoreFor(padron, byStyle(/sparkling/)) + 10);

    const tabernacle = cigarById("cig-foundation-tabernacle")!; // s5 b5
    expect(meanScoreFor(tabernacle, byStyle(/islay-peated/)))
      .toBeGreaterThan(meanScoreFor(tabernacle, byStyle(/london-dry|premium-dry/)) + 15);

    const signature = cigarById("cig-davidoff-signature")!; // s1 b2
    expect(meanScoreFor(signature, byStyle(/sparkling|white-fresh/)))
      .toBeGreaterThan(meanScoreFor(signature, byStyle(/islay-peated/)) + 10);
  });

  it("dimljeni whisky dobiva pune cigare, ne blage", () => {
    const laph = ALL_DRINKS.find((d) => d.id === "wh-laphroaig-10")!;
    const top = pairCigarsForDrink(laph, CIGARS).slice(0, 10);
    for (const r of top) {
      expect(r.item.body, `${r.item.id} u top 10 za Laphroaig`).toBeGreaterThanOrEqual(4);
    }
  });

  it("distribucija scoreova je zdrava (nije saturirana ni sabijena)", () => {
    const scores: number[] = [];
    for (const c of CIGARS.filter((_, i) => i % 7 === 0)) {
      for (const d of ALL_DRINKS.filter((_, i) => i % 5 === 0)) {
        scores.push(scorePairing(c, d).score);
      }
    }
    scores.sort((a, b) => a - b);
    const median = scores[Math.floor(scores.length / 2)];
    const share80 = scores.filter((s) => s >= 80).length / scores.length;
    const share100 = scores.filter((s) => s === 100).length / scores.length;
    expect(median).toBeGreaterThan(25);
    expect(median).toBeLessThan(70);
    expect(share80).toBeGreaterThan(0.02); // kurirane poruke moraju postojati
    expect(share80).toBeLessThan(0.3); // ...ali 80+ mora ostati poseban
    expect(share100).toBeLessThan(0.02);
  });

  // poruka postoji samo uz match >= 80 — upozorenja u njoj su kontradikcija
  it("kurirane poruke (>= 80) nemaju negativne verdikte", () => {
    const NEG = /nije idealan|izgubio bi|bi se izgubi|pregazi|steamroll|swamp|not ideal|disappear quickly|overwhelm/i;
    const offenders: string[] = [];
    for (const c of CIGARS.filter((_, i) => i % 3 === 0)) {
      for (const d of ALL_DRINKS.filter((_, i) => i % 3 === 0)) {
        const { score, reasons } = scorePairing(c, d);
        const op = curatedPairingOpinion(c, d, reasons, score);
        if (op && (NEG.test(op.hr) || NEG.test(op.en))) {
          offenders.push(`${c.id} + ${d.id} @${score}: ${op.hr.slice(0, 90)}`);
        }
      }
    }
    expect(offenders).toEqual([]);
  });
});
