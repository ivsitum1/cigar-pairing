import { describe, expect, it } from "vitest";
import type { Cigar } from "../types";
import { cigarItemId } from "./cigarItemId";
import {
  explainStock,
  resolveSheetFromItemId,
  type StockRow,
} from "./cigarIdentity";

const line: Cigar = {
  id: "cig-x",
  brand: "Oliva",
  line: "Serie O",
  vitola: "Robusto",
  format: "50 x 127mm",
  country: "Nikaragva",
  wrapper: "Habano",
  strength: 3,
  body: 3,
  flavorTags: [],
  smokeTimeMin: 50,
  priceEUR: 9,
  markets: ["HR"],
  availabilityHR: [],
  notes: { hr: "", en: "" },
  vitolas: [
    { name: "Robusto", format: "50 x 127mm", smokeTimeMin: 50, priceEUR: 9, url: null },
    { name: "Churchill", format: "50 x 178mm", smokeTimeMin: 85, priceEUR: 10, url: null },
  ],
};

describe("resolveSheetFromItemId", () => {
  it("goli id linije s više vitola → line sheet", () => {
    const d = resolveSheetFromItemId("cig-x", line);
    expect(d.mode).toBe("line");
  });

  it("poznat slug → detail s applyVitola, bez LineSheet", () => {
    const d = resolveSheetFromItemId("cig-x@churchill", line);
    expect(d.mode).toBe("detail");
    if (d.mode !== "detail") throw new Error("expected detail");
    expect(d.cigar.selectedVitola).toBe("Churchill");
    expect(d.cigar.vitolas).toHaveLength(1);
    expect(cigarItemId(d.cigar)).toBe("cig-x@churchill");
  });

  it("nepoznat slug → line sheet (ne lažni detail)", () => {
    const d = resolveSheetFromItemId("cig-x@ghost", line);
    expect(d.mode).toBe("line");
  });

  it("jedna vitola → detail", () => {
    const single = { ...line, vitolas: [line.vitolas[0]] };
    const d = resolveSheetFromItemId("cig-x", single);
    expect(d.mode).toBe("detail");
  });
});

describe("explainStock", () => {
  const rows: StockRow[] = [
    { itemId: "cig-x", count: 4 },
    { itemId: "cig-x@churchill", count: 2 },
    { itemId: "cig-x@robusto", count: 1 },
  ];

  it("točan pogodak vitole", () => {
    const e = explainStock("cig-x@churchill", rows);
    expect(e.exact).toBe(2);
    expect(e.unassignedLine).toBe(4);
    expect(e.siblings.map((s) => s.itemId)).toEqual(["cig-x@robusto"]);
  });

  it("goli id vidi vlastiti bazen, ne vitole kao exact", () => {
    const e = explainStock("cig-x", rows);
    expect(e.exact).toBe(4);
    expect(e.unassignedLine).toBe(0);
  });
});
