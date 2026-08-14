import { describe, expect, it } from "vitest";
import type { Cigar, Vitola } from "../types";
import {
  groupStockByLine,
  stockNeedsVitola,
  stockVitolaName,
  vitolaStockId,
  vitolasNotInStock,
} from "./humidorVitola";

const vitola = (name: string): Vitola => ({
  name,
  format: "Parejo",
  ring: 50,
  lengthMM: 127,
  smokeTimeMin: 50,
  priceEUR: 9,
  url: null,
});

const line = (id: string, vitolas: Vitola[]): Cigar =>
  ({
    id,
    brand: "Marka",
    line: "Linija",
    vitola: vitolas[0]?.name ?? "Robusto",
    format: "Parejo",
    country: "Nikaragva",
    wrapper: "Habano",
    strength: 3,
    body: 3,
    smokeTimeMin: 50,
    flavors: [],
    vitolas,
  }) as unknown as Cigar;

const MULTI = line("cig-x", [vitola("Robusto"), vitola("Figurado"), vitola("Toro")]);
const SINGLE = line("cig-solo", [vitola("Robusto")]);

describe("ključ zalihe po vitoli", () => {
  it("vitola dobiva svoj ključ na liniji s više formata", () => {
    expect(vitolaStockId(MULTI, vitola("Robusto"))).toBe("cig-x@robusto");
    expect(vitolaStockId(MULTI, vitola("Figurado"))).toBe("cig-x@figurado");
  });

  it("linija s jednim formatom ostaje na golom ključu", () => {
    expect(vitolaStockId(SINGLE, vitola("Robusto"))).toBe("cig-solo");
  });
});

describe("stockNeedsVitola", () => {
  it("goli ključ na liniji s više formata traži vitolu", () => {
    expect(stockNeedsVitola(MULTI, "cig-x")).toBe(true);
  });

  it("ključ s vitolom je razriješen", () => {
    expect(stockNeedsVitola(MULTI, "cig-x@toro")).toBe(false);
  });

  it("linija s jednim formatom nema što birati", () => {
    expect(stockNeedsVitola(SINGLE, "cig-solo")).toBe(false);
  });

  it("nepoznata cigara se ne dira", () => {
    expect(stockNeedsVitola(undefined, "cig-nepoznat")).toBe(false);
  });
});

describe("stockVitolaName", () => {
  it("čita ime vitole iz ključa", () => {
    expect(stockVitolaName(MULTI, "cig-x@figurado")).toBe("Figurado");
  });

  it("goli ključ na liniji s više formata nema određenu vitolu", () => {
    expect(stockVitolaName(MULTI, "cig-x")).toBeNull();
  });

  it("goli ključ jednoformatne linije nosi baš taj format", () => {
    expect(stockVitolaName(SINGLE, "cig-solo")).toBe("Robusto");
  });

  it("vitola izbačena iz kataloga ostaje vidljiva kao slug", () => {
    expect(stockVitolaName(MULTI, "cig-x@lancero")).toBe("lancero");
  });
});

describe("vitolasNotInStock", () => {
  it("nudi samo formate kojih još nema u kutiji", () => {
    const names = vitolasNotInStock(MULTI, ["cig-x@robusto"]).map((v) => v.name);
    expect(names).toEqual(["Figurado", "Toro"]);
  });

  it("prazna kutija nudi sve formate", () => {
    expect(vitolasNotInStock(MULTI, [])).toHaveLength(3);
  });
});

describe("groupStockByLine", () => {
  it("vitole iste linije stoje pod jednim naslovom", () => {
    const groups = groupStockByLine([
      { itemId: "cig-x@robusto", count: 3 },
      { itemId: "cig-y", count: 1 },
      { itemId: "cig-x@figurado", count: 2 },
      { itemId: "cig-x@toro", count: 1 },
    ]);

    expect(groups.map((g) => g.cigarId)).toEqual(["cig-x", "cig-y"]);
    expect(groups[0].total).toBe(6);
    expect(groups[0].entries.map((e) => e.itemId)).toEqual([
      "cig-x@robusto",
      "cig-x@figurado",
      "cig-x@toro",
    ]);
    expect(groups[1].total).toBe(1);
  });

  it("stara zaliha po liniji stoji uz vitole iste linije", () => {
    const groups = groupStockByLine([
      { itemId: "cig-x", count: 4 },
      { itemId: "cig-x@toro", count: 1 },
    ]);
    expect(groups).toHaveLength(1);
    expect(groups[0].total).toBe(5);
  });

  it("druga linija s istim prefiksom ostaje svoja grupa", () => {
    const groups = groupStockByLine([
      { itemId: "cig-x@toro", count: 1 },
      { itemId: "cig-x-reserva", count: 2 },
    ]);
    expect(groups.map((g) => g.cigarId)).toEqual(["cig-x", "cig-x-reserva"]);
  });
});
