import { describe, it, expect } from "vitest";
import {
  lookupBarcode,
  lookupBarcodeInText,
  normalizeBarcodeDigits,
} from "./ocrBarcode";

describe("ocrBarcode", () => {
  it("normalizira UPC/EAN varijante", () => {
    expect(normalizeBarcodeDigits("8 14539 01162 4")).toEqual(
      expect.arrayContaining(["814539011624"]),
    );
  });

  it("mapira poznati Oliva Serie G barkod (Double Robusto)", () => {
    expect(lookupBarcode("814539011624")).toBe("cig-oliva-serie-g@double-robusto");
  });

  it("mapira Oliva Serie G Special G (3.75 x 48 perfecto)", () => {
    expect(lookupBarcode("814539011594")).toBe("cig-oliva-serie-g@special-g");
    const hit = lookupBarcodeInText("OLIVA SERIE G\n8 14539 01159 4");
    expect(hit?.itemId).toBe("cig-oliva-serie-g@special-g");
  });

  it("nalazi barkod u OCR tekstu s razmacima", () => {
    const hit = lookupBarcodeInText("SERIE G\n8 14539 01162 4\nextra");
    expect(hit?.itemId).toBe("cig-oliva-serie-g@double-robusto");
  });

  it("mapira Perdomo 20th sticker barkod", () => {
    expect(lookupBarcode("816229015691")).toBe(
      "cig-perdomo-20th-anniversary@robusto",
    );
  });
});
