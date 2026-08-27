import { describe, expect, it } from "vitest";
import type { Cigar, Vitola } from "../types";
import { cigarLinePrice, formatEur, vitolaPriceForMarket } from "./cigarPrice";
import { CIGARS } from "../data";
import { uniqueVitolas } from "./cigarVitola";

const vitola = (v: Partial<Vitola> & { name: string }): Vitola => ({
  format: null,
  smokeTimeMin: null,
  priceEUR: null,
  url: null,
  ...v,
});

const cigar = (v: Vitola[], extra: Partial<Cigar> = {}): Cigar =>
  ({
    id: "cig-test",
    brand: "Test",
    line: "Line",
    vitola: v[0]?.name ?? "",
    format: "50 x 127mm",
    country: "Nikaragva",
    wrapper: "Habano",
    strength: 3,
    body: 3,
    flavorTags: [],
    smokeTimeMin: 50,
    priceEUR: null,
    vitolas: v,
    markets: ["HR"],
    availabilityHR: [],
    notes: { hr: "", en: "" },
    ...extra,
  }) as Cigar;

describe("vitolaPriceForMarket", () => {
  it("HR uzima vlastitu cijenu vitole (humidor/havana)", () => {
    const v = vitola({ name: "Robusto", priceEUR: 9.5, url: "https://humidor.hr/x" });
    expect(vitolaPriceForMarket(v, "HR")).toMatchObject({
      price: 9.5,
      region: "HR",
      url: "https://humidor.hr/x",
    });
  });

  it("EU/USA cijena ne curi u HR prikaz", () => {
    const v = vitola({
      name: "Toro",
      regionLinks: { EU: { shop: "CigarWorld", url: "https://cigarworld.de/x", priceEUR: 11 } },
    });
    expect(vitolaPriceForMarket(v, "HR").price).toBeNull();
    expect(vitolaPriceForMarket(v, "EU").price).toBe(11);
  });

  it('"ALL" ide HR -> EU -> USA i kaže odakle je broj', () => {
    const v = vitola({
      name: "Toro",
      regionLinks: {
        EU: { shop: "CigarWorld", url: "https://cigarworld.de/x", priceEUR: 11 },
        USA: { shop: "Holt's", url: "https://holts.com/x", priceEUR: 8, priceApprox: true },
      },
    });
    expect(vitolaPriceForMarket(v, "ALL")).toMatchObject({ price: 11, region: "EU" });
    expect(vitolaPriceForMarket(v, "USA")).toMatchObject({ price: 8, approx: true });
  });
});

describe("cigarLinePrice", () => {
  it('"od X" je stvarno najniža cijena, a link vodi na tu vitolu', () => {
    const c = cigar([
      vitola({ name: "Corona", priceEUR: 12.3, url: "https://humidor.hr/corona" }),
      vitola({ name: "Petit", priceEUR: 5, url: "https://humidor.hr/petit" }),
      vitola({ name: "Toro", priceEUR: 14, url: "https://humidor.hr/toro" }),
    ]);
    const p = cigarLinePrice(c, "HR");
    expect(p).toMatchObject({ price: 5, from: true, min: 5, max: 14 });
    expect(p.url).toBe("https://humidor.hr/petit");
  });

  it("jedna cijena u liniji -> bez `od`", () => {
    const c = cigar([
      vitola({ name: "Robusto", priceEUR: 9 }),
      vitola({ name: "Toro", priceEUR: 9 }),
    ]);
    expect(cigarLinePrice(c, "HR")).toMatchObject({ price: 9, from: false });
  });

  it("bez cijena po vitolama pada na cijenu linije", () => {
    const c = cigar([vitola({ name: "Robusto" })], { priceEUR: 7.5 });
    expect(cigarLinePrice(c, "HR")).toMatchObject({ price: 7.5, from: false });
    expect(cigarLinePrice(c, "EU").price).toBeNull();
  });

  it("selectedVitola: popis pokazuje cijenu te veličine, ne najjeftiniju u liniji", () => {
    const c = cigar(
      [
        vitola({ name: "Robusto", priceEUR: 11, url: "https://humidor.hr/robusto" }),
        vitola({ name: "Lancero", priceEUR: 40, url: "https://humidor.hr/lancero" }),
      ],
      { selectedVitola: "Lancero" },
    );
    expect(cigarLinePrice(c, "HR")).toMatchObject({
      price: 40,
      from: false,
      url: "https://humidor.hr/lancero",
    });
  });
});

describe("formatEur", () => {
  it("decimale samo kad postoje", () => {
    expect(formatEur(13)).toBe("13 €");
    expect(formatEur(13.5)).toBe("13.50 €");
  });
});

describe("katalog: cijena je ista u popisu, liniji i kartici", () => {
  // Regresija: kartica je za vitolu bez HR cijene tiho pokazivala EU broj, a
  // linija je za istu vitolu pisala "provjeri cijenu".
  for (const market of ["HR", "EU", "ALL"] as const) {
    it(`${market}: cijena linije je najniža cijena njenih vitola`, () => {
      const bad: string[] = [];
      for (const c of CIGARS) {
        const line = cigarLinePrice(c, market);
        const perVitola = uniqueVitolas(c)
          .map((v) => vitolaPriceForMarket(v, market).price)
          .filter((p): p is number => p != null);
        if (perVitola.length === 0) continue;
        const min = Math.min(...perVitola);
        if (line.price == null || Math.abs(line.price - min) > 0.005) {
          bad.push(`${c.id}: linija ${line.price} vs najniža vitola ${min}`);
        }
        if (line.from !== Math.max(...perVitola) - min > 0.01) {
          bad.push(`${c.id}: "od" oznaka ne prati raspon`);
        }
      }
      expect(bad.slice(0, 10)).toEqual([]);
    });
  }
});
