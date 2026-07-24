import { describe, it, expect } from "vitest";
import {
  classifyVitola,
  cigarShapes,
  firstVitolaOfShape,
  SHAPE_FAMILIES,
  type ShapeFamily,
} from "./vitolaShape";
import type { Cigar, Vitola } from "../types";

const vitola = (partial: Partial<Vitola> & Pick<Vitola, "name">): Vitola => ({
  format: null,
  smokeTimeMin: null,
  priceEUR: null,
  url: null,
  ...partial,
});

const baseCigar = (overrides: Partial<Cigar> = {}): Cigar => ({
  id: "cig-test",
  brand: "Test",
  line: "Line",
  vitola: "Robusto",
  format: "",
  country: "NI",
  wrapper: "Habano",
  strength: 4,
  body: 3,
  flavorTags: [],
  smokeTimeMin: 55,
  priceEUR: null,
  vitolas: [],
  markets: [],
  availabilityHR: [],
  notes: { hr: "", en: "" },
  ...overrides,
});

describe("classifyVitola — po nazivu", () => {
  const cases: [string, ShapeFamily][] = [
    ["Robusto", "robusto"],
    ["Short Robusto", "robusto"],
    ["Double Robusto", "robusto"],
    ["Toro", "toro"],
    ["Gran Toro", "toro"],
    ["Cañonazo", "toro"],
    ["Corona", "corona"],
    ["Petit Corona", "corona"],
    ["Half Corona", "corona"],
    ["Corona Gorda", "corona"],
    ["Churchill", "churchill"],
    ["Double Corona", "churchill"],
    ["Lonsdale", "churchill"],
    ["Presidente", "churchill"],
    ["Gordo", "gordo"],
    ["Gigante", "gordo"],
    ["Lancero", "lancero"],
    ["Panetela", "lancero"],
    ["Torpedo", "figurado"],
    ["Belicoso", "figurado"],
    ["Piramide", "figurado"],
    ["Perfecto", "figurado"],
    ["Diadema", "figurado"],
  ];
  it.each(cases)("%s → %s", (name, family) => {
    expect(classifyVitola(vitola({ name }))).toBe(family);
  });
});

describe("classifyVitola — prioritet i granice", () => {
  it("shape polje ima prednost pred nazivom", () => {
    expect(classifyVitola(vitola({ name: "Neki maketing naziv", shape: "Toro" }))).toBe("toro");
  });

  it("Corona Gorda ostaje corona (ne gordo)", () => {
    expect(classifyVitola(vitola({ name: "Corona Gorda" }))).toBe("corona");
  });

  it("figurado ima prednost — Belicoso nije corona", () => {
    expect(classifyVitola(vitola({ name: "Belicoso Fino" }))).toBe("figurado");
  });

  it("geometrija: debeo ring bez naziva → gordo", () => {
    expect(classifyVitola(vitola({ name: "??", ring: 60, lengthMM: 150 }))).toBe("gordo");
  });

  it("geometrija: tanak ring bez naziva → lancero", () => {
    expect(classifyVitola(vitola({ name: "??", ring: 38, lengthMM: 178 }))).toBe("lancero");
  });

  it("geometrija: srednji ring, dugačko → toro; kratko → robusto", () => {
    expect(classifyVitola(vitola({ name: "??", ring: 50, lengthMM: 165 }))).toBe("toro");
    expect(classifyVitola(vitola({ name: "??", ring: 50, lengthMM: 127 }))).toBe("robusto");
  });

  it("bez ikakvog signala → null", () => {
    expect(classifyVitola(vitola({ name: "??" }))).toBeNull();
  });
});

describe("cigarShapes / firstVitolaOfShape", () => {
  const cigar = baseCigar({
    vitolas: [
      vitola({ name: "Robusto", ring: 50, lengthMM: 124 }),
      vitola({ name: "Churchill", ring: 47, lengthMM: 178 }),
      vitola({ name: "Toro", ring: 52, lengthMM: 152 }),
    ],
  });

  it("skuplja sve obitelji linije", () => {
    expect(cigarShapes(cigar)).toEqual(new Set(["robusto", "churchill", "toro"]));
  });

  it("vraća prvu vitolu tražene obitelji", () => {
    expect(firstVitolaOfShape(cigar, "churchill")?.name).toBe("Churchill");
    expect(firstVitolaOfShape(cigar, "gordo")).toBeUndefined();
  });

  it("SHAPE_FAMILIES sadrži svih 7 obitelji bez duplikata", () => {
    expect(new Set(SHAPE_FAMILIES).size).toBe(7);
  });
});
