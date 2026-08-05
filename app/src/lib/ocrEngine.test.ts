import { describe, it, expect } from "vitest";
import { isUsableOcr } from "./ocrEngine";
import type { OcrEngineResult } from "./ocrTypes";

const base = (over: Partial<OcrEngineResult>): OcrEngineResult => ({
  text: "",
  lines: [],
  engine: "tesseract",
  source: "offline",
  ...over,
});

describe("isUsableOcr", () => {
  it("rejects empty / digit-only", () => {
    expect(isUsableOcr(null)).toBe(false);
    expect(isUsableOcr(base({ text: "12 34" }))).toBe(false);
    expect(isUsableOcr(base({ text: "ab" }))).toBe(false);
  });

  it("accepts brand-like text", () => {
    expect(isUsableOcr(base({ text: "Hampden Estate 8" }))).toBe(true);
  });

  it("rejects low average paddle confidence", () => {
    expect(
      isUsableOcr(
        base({
          text: "Oliva Serie V",
          lines: [
            { text: "Oliva", confidence: 0.1 },
            { text: "Serie", confidence: 0.1 },
            { text: "V", confidence: 0.1 },
          ],
        }),
      ),
    ).toBe(false);
  });
});
