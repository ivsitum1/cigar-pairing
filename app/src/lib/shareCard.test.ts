import { describe, it, expect } from "vitest";
import { buildShareCardModel } from "./shareCard";
import type { Cigar, Drink, PairingReason } from "../types";

const cigar = {
  brand: "Padrón",
  line: "1964 Anniversary",
  vitola: "Robusto",
} as Cigar;

const drink = { name: "Diplomático Reserva" } as Drink;

const reasons: PairingReason[] = [
  { rule: "a", score: 18, text: { hr: "Tijela se poklapaju.", en: "Bodies match." } },
  { rule: "b", score: 7, text: { hr: "Dijele note.", en: "Shared notes." } },
  { rule: "c", score: 5, text: { hr: "Nadopunjuju se.", en: "Complementary." } },
  { rule: "neg", score: -10, text: { hr: "Loše.", en: "Bad." } },
  { rule: "serve", score: 0, text: { hr: "Kap vode.", en: "Water." } },
];

describe("buildShareCardModel", () => {
  it("slaže cigaru s vitolom i piće bez serve sufiksa (neat)", () => {
    const m = buildShareCardModel(cigar, drink, "neat", 88.4, reasons, "hr");
    expect(m.cigarLine).toBe("Padrón 1964 Anniversary · Robusto");
    expect(m.drinkLine).toBe("Diplomático Reserva");
    expect(m.score).toBe(88); // zaokruženo
  });

  it("dodaje lokalizirani serve sufiks", () => {
    expect(
      buildShareCardModel(cigar, drink, "water", 80, reasons, "hr").drinkLine,
    ).toBe("Diplomático Reserva · Kap vode");
    expect(
      buildShareCardModel(cigar, drink, "water", 80, reasons, "en").drinkLine,
    ).toBe("Diplomático Reserva · Splash of water");
  });

  it("uzima najviše 2 pozitivna razloga, redom po score (desc)", () => {
    const m = buildShareCardModel(cigar, drink, undefined, 80, reasons, "hr");
    expect(m.reasons).toEqual(["Tijela se poklapaju.", "Dijele note."]);
  });

  it("lokalizira razloge i eyebrow", () => {
    const hr = buildShareCardModel(cigar, drink, undefined, 80, reasons, "hr");
    const en = buildShareCardModel(cigar, drink, undefined, 80, reasons, "en");
    expect(hr.reasons[0]).toBe("Tijela se poklapaju.");
    expect(en.reasons[0]).toBe("Bodies match.");
    expect(hr.eyebrow).toContain("SPOJ");
    expect(en.eyebrow).toContain("PAIRING");
  });

  it("izostavlja vitolu kad je nema ili je '—'", () => {
    const noVit = { brand: "Cohiba", line: "Behike", vitola: "—" } as Cigar;
    expect(
      buildShareCardModel(noVit, drink, undefined, 70, reasons, "hr").cigarLine,
    ).toBe("Cohiba Behike");
  });
});
