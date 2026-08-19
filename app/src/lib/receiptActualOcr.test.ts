/** Eval: parseReceiptText against tesseract *.actual-ocr.txt from fixtures. */
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it, expect } from "vitest";
import { buildCigarOcrCandidates } from "./ocrCigarCandidates";
import { parseReceiptText } from "./receiptParse";
import cigarsData from "../data/cigars.json";
import type { Cigar } from "../types";

const cigarCandidates = buildCigarOcrCandidates(cigarsData as Cigar[]);

const fixtureDir = join(
  dirname(fileURLToPath(import.meta.url)),
  "../../scripts/data/ocr-receipts",
);

function loadActual(stem: string): string | null {
  const p = join(fixtureDir, `${stem}.actual-ocr.txt`);
  return existsSync(p) ? readFileSync(p, "utf8") : null;
}

describe("actual tesseract OCR → receiptParse (soft)", () => {
  it("tobacco-shop-5-2023 finds Oliva / Don Tomas from noisy OCR", () => {
    const text = loadActual("tobacco-shop-5-2023-07-29");
    expect(text).toBeTruthy();
    const rows = parseReceiptText(text!, cigarCandidates);
    const ids = rows.map((r) => r.candidate?.id ?? "");
    // noisy OCR still should recover at least one strong brand line
    expect(
      ids.some(
        (id) =>
          id.includes("oliva") ||
          id.includes("don-tomas") ||
          id.includes("perdomo"),
      ),
    ).toBe(true);
  });

  it("tobacco-shop-5-2024 finds Don Tomas bundle vitola or La Estrella", () => {
    const text = loadActual("tobacco-shop-5-2024-07-30");
    expect(text).toBeTruthy();
    const rows = parseReceiptText(text!, cigarCandidates);
    const ids = rows.map((r) => r.candidate?.id ?? "");
    expect(
      ids.some(
        (id) => id === "cig-don-tomas-bundle@rothschild" || id.includes("estrella"),
      ),
    ).toBe(true);
  }, 15_000);
});
