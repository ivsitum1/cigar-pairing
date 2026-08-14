// Sedam kombinacija kava x cigara — imena iz lekcije moraju postojati u
// katalogu, a arhetip za svaku pripremu mora imati svoju karticu.
//
// Bez ovoga preporuka tiho istrune: linija ispadne iz kataloga pri sljedecem
// scrapeu, a lekcija je i dalje spominje kao primjer.
import { describe, expect, it } from "vitest";
import cigarsData from "./cigars.json";
import club101 from "./club101.json";
import eveningArchetypes from "./eveningArchetypes.json";
import type { Cigar } from "../types";

const cigars = cigarsData as Cigar[];

/** (marka, linija) kako stoje u tekstu lekcije. */
const EXAMPLES: [string, string][] = [
  ["Joya de Nicaragua", "Antaño 1970"],
  ["Flor de Selva", "Maduro"],
  ["Arturo Fuente", "Curly Head"],
  ["Quai d'Orsay", "Clásica"],
  ["E.P. Carrillo", "Seleccion Oscuro"],
  ["A. Flores", "Gran Reserva Desflorado"],
  ["Ramón Allones", "Specially Selected"],
];

const coffeeLesson = club101.tracks.drinks.find((c) => c.id === "d-coffee")!;

describe("kombinacije kava x cigara", () => {
  it("svaki primjer iz lekcije postoji u katalogu i dostupan je u HR", () => {
    for (const [brand, line] of EXAMPLES) {
      const hit = cigars.find((c) => c.brand === brand && c.line === line);
      expect(hit, `${brand} ${line} nema u katalogu`).toBeDefined();
      expect(
        (hit!.availabilityHR ?? []).length,
        `${brand} ${line} nije dostupna u HR`,
      ).toBeGreaterThan(0);
    }
  });

  it("lekcija stvarno spominje svaki primjer", () => {
    for (const [, line] of EXAMPLES) {
      expect(coffeeLesson.body.hr, line).toContain(line);
      expect(coffeeLesson.body.en, line).toContain(line);
    }
  });

  it("svaka priprema iz sedmorke ima svoj arhetip", () => {
    const ids = eveningArchetypes.entries.map((e) => e.id);
    for (const id of [
      "coffee-espresso",
      "coffee-lungo",
      "coffee-americano",
      "coffee-filter-light",
      "coffee-filter-dark",
      "coffee-milk",
      "coffee-turkish",
    ]) {
      expect(ids, id).toContain(id);
    }
  });
});
