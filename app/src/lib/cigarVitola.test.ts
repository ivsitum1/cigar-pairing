import { describe, it, expect } from "vitest";
import { applyVitola, needsVitolaPick, resolveDefaultVitola, uniqueVitolas } from "./cigarVitola";
import type { Cigar } from "../types";

const serieO: Cigar = {
  id: "cig-oliva-serie-o",
  brand: "Oliva",
  line: "Serie O",
  vitola: "Serie O Robusto",
  format: "50 x 127mm",
  country: "Nikaragva",
  wrapper: "Habano",
  strength: 3,
  body: 3,
  flavorTags: [],
  smokeTimeMin: 50,
  priceEUR: 9.2,
  priceUrl: "https://humidor.hr/hr/proizvod/oliva-serie-o-robusto-5-x-50/",
  availabilityHR: ["The Humidor"],
  notes: { hr: "", en: "" },
  markets: ["HR", "EU", "WW"],
  vitolas: [
    {
      name: "Serie O Robusto",
      format: "50 x 127mm",
      smokeTimeMin: 50,
      priceEUR: 9.2,
      url: "https://humidor.hr/hr/proizvod/oliva-serie-o-robusto-5-x-50/",
    },
    { name: "Tubos", format: "50 x 152mm", smokeTimeMin: 55, priceEUR: 13.4, url: null },
    { name: "Serie O Churchill", format: "50 x 178mm", smokeTimeMin: 85, priceEUR: 9.0, url: null },
  ],
};

describe("cigarVitola", () => {
  it("uniqueVitolas uklanja duplikate", () => {
    const dup: Cigar = {
      ...serieO,
      vitolas: [...(serieO.vitolas ?? []), { name: "Tubos", format: "50 x 152mm", smokeTimeMin: 55, priceEUR: 13.4, url: null }],
    };
    expect(uniqueVitolas(dup)).toHaveLength(3);
  });

  it("needsVitolaPick za Serie O", () => {
    expect(needsVitolaPick(serieO)).toBe(true);
    expect(needsVitolaPick({ ...serieO, vitolas: [serieO.vitolas![0]] })).toBe(false);
  });

  it("applyVitola postavlja cijenu i format", () => {
    const tubos = serieO.vitolas![1];
    const applied = applyVitola(serieO, tubos);
    expect(applied.vitola).toBe("Tubos");
    expect(applied.priceEUR).toBe(13.4);
    expect(applied.format).toBe("50 x 152mm");
  });

  it("applyVitola prikazuje SAMO odabranu vitolu (ne cijeli popis)", () => {
    const applied = applyVitola(serieO, serieO.vitolas![1]);
    expect(applied.vitolas).toHaveLength(1);
    expect(applied.vitolas[0].name).toBe("Tubos");
    expect(needsVitolaPick(applied)).toBe(false);
  });

  it("applyVitola ne nasljeđuje priceUrl kad vitola nema url i format ne odgovara", () => {
    const churchill = serieO.vitolas![2];
    const applied = applyVitola(serieO, churchill);
    expect(applied.vitola).toBe("Serie O Churchill");
    expect(applied.priceUrl).toBeNull();
  });

  it("resolveDefaultVitola preferira vitolu istog imena kao linija", () => {
    const cigar: Cigar = {
      ...serieO,
      line: "Gran Reserva",
      vitola: "Corona",
      vitolas: [
        { name: "Cubanitos", format: "—", smokeTimeMin: 30, priceEUR: 5, url: "https://shop/cubanitos" },
        { name: "Gran Reserva", format: "45 x 133mm", smokeTimeMin: 50, priceEUR: 12.3, url: "https://humidor.hr/hr/proizvod/cuban-corona" },
        { name: "Corona", format: "—", smokeTimeMin: 45, priceEUR: 12.3, url: "https://havana/cuban-corona" },
      ],
    };
    const picked = resolveDefaultVitola(cigar);
    expect(picked?.name).toBe("Gran Reserva");
    expect(picked?.url).toContain("humidor.hr");
  });
});
