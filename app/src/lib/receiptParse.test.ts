/** Parse receipt OCR into catalog matches. */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it, expect } from "vitest";
import { parseReceiptText, cleanReceiptProductName } from "./receiptParse";
import type { OcrCandidate } from "./ocrMatch";
import cigarsData from "../data/cigars.json";

const cigarCandidates: OcrCandidate[] = (
  cigarsData as { id: string; brand: string; line: string }[]
).map((c) => ({
  id: c.id,
  label: `${c.brand} ${c.line}`,
  brand: c.brand,
}));

const fixtureDir = join(
  dirname(fileURLToPath(import.meta.url)),
  "../../scripts/data/ocr-receipts",
);

const readOcr = (name: string) =>
  readFileSync(join(fixtureDir, name), "utf8");

const ids = (rows: ReturnType<typeof parseReceiptText>) =>
  rows.map((r) => r.candidate?.id);

describe("cleanReceiptProductName", () => {
  it("strips box count, Kom qty leftover, and prices", () => {
    expect(
      cleanReceiptProductName("Oliva Serie V Torpedo/24 25% 15,85 15,85"),
    ).toMatch(/oliva serie v torpedo/i);
    expect(cleanReceiptProductName("OLIVA CONN. RESERV ROBUSTO/20")).toMatch(
      /connecticut reserve/i,
    );
  });
});

describe("parseReceiptText", () => {
  it("matches product lines and skips totals", () => {
    const text = `
RAČUN 001
Partagas Serie D No.4
2 x Cohiba Siglo VI
UKUPNO 120,00 EUR
HVALA
`;
    const rows = parseReceiptText(text, cigarCandidates);
    expect(rows.length).toBeGreaterThanOrEqual(1);
  });

  it("returns empty for noise-only receipt", () => {
    expect(parseReceiptText("UKUPNO 10 EUR\nPDV 2", cigarCandidates)).toEqual([]);
  });

  it("Camelot Havana fixture: Oliva / Joya / Cusano (+ qty 5)", () => {
    const rows = parseReceiptText(
      readOcr("camelot-havana-2026-07-10.ocr.txt"),
      cigarCandidates,
    );
    const found = ids(rows);
    expect(found).toContain("cig-oliva-serie-v");
    expect(found).toContain("cig-oliva-serie-v-melanio");
    expect(found).toContain("cig-joya-de-nicaragua-joya-black");
    expect(found).toContain("cig-joya-de-nicaragua-joya-silver");
    expect(found).toContain("cig-cusano-bundle-selection");
    const cusano = rows.find((r) => r.candidate?.id === "cig-cusano-bundle-selection");
    expect(cusano?.qty).toBe(5);
    // candy / totals not present
    expect(found.every((id) => id && !/cedevita/i.test(id))).toBe(true);
  });

  it("Tobacco shop 5 (2023): Oliva + Perdomo; skips Cedevita and chicken foot", () => {
    const rows = parseReceiptText(
      readOcr("tobacco-shop-5-2023-07-29.ocr.txt"),
      cigarCandidates,
    );
    const found = ids(rows);
    expect(found).toContain("cig-oliva-serie-o");
    expect(found).toContain("cig-oliva-serie-g");
    expect(found).toContain("cig-oliva-connecticut-reserve");
    expect(found.some((id) => id?.startsWith("cig-perdomo-20th"))).toBe(true);
    expect(found.some((id) => id?.startsWith("cig-don-tomas"))).toBe(true);
    expect(rows.every((r) => !/cedevita|chicken/i.test(r.raw))).toBe(true);
  });

  it("Tobacco shop 5 (2024): Don Tomas bundle qty 10 + La Estrella Polar", () => {
    const rows = parseReceiptText(
      readOcr("tobacco-shop-5-2024-07-30.ocr.txt"),
      cigarCandidates,
    );
    const found = ids(rows);
    expect(found).toContain("cig-don-tomas-bundle");
    expect(found).toContain("cig-la-estrella-polar");
    const bundle = rows.find((r) => r.candidate?.id === "cig-don-tomas-bundle");
    expect(bundle?.qty).toBe(10);
  });

  it("rescues noisy Don Tomas tokens instead of falling onto generic vitolas", () => {
    const rows = parseReceiptText(
      [
        "DOVTOMAS CHRCHLL 1 KOM 3,90 3,90",
        "DOVTOLIAS ROTHSGHLD 1 KOM 3,60 3,60",
        "DONTOLIA> BUNDLE NIC ROTHSCHILD 10 KOM",
      ].join("\n"),
      cigarCandidates,
    );
    const found = ids(rows);
    expect(found.some((id) => id?.startsWith("cig-don-tomas"))).toBe(true);
    expect(found.every((id) => !id?.includes("romeo-y-julieta"))).toBe(true);
    expect(found.every((id) => !id?.includes("quorum"))).toBe(true);
  });

  it("deduplicates receipt rows and upgrades selection when later barcode confirms", () => {
    const candidates: OcrCandidate[] = [
      {
        id: "cig-oliva-serie-g@special-g",
        label: "Oliva Serie G Special G",
        brand: "Oliva",
      },
      {
        id: "cig-oliva-serie-g@double-robusto",
        label: "Oliva Serie G Double Robusto",
        brand: "Oliva",
      },
    ];

    // 814539011624 => Double Robusto (barcode hint conflicts with OCR-selected Special G)
    // 814539011594 => Special G (barcode confirms the same chosen id)
    const rows = parseReceiptText(
      [
        "OLIVA SERIE G SPECIAL G 1 KOM 3,60 3,60 814539011624",
        "OLIVA SERIE G SPECIAL G 1 KOM 3,60 3,60 814539011594",
      ].join("\n"),
      candidates,
    );

    expect(rows).toHaveLength(1);
    const r = rows[0];
    expect(r.candidate?.id).toBe("cig-oliva-serie-g@special-g");
    expect(r.qty).toBe(2);
    expect(r.selected).toBe(true);
    expect(r.barcodeCandidate?.id).toBe("cig-oliva-serie-g@special-g");
  });
});
