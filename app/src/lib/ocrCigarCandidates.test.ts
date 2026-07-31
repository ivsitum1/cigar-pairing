import { describe, it, expect } from "vitest";
import { buildCigarOcrCandidates } from "./ocrCigarCandidates";
import { parseReceiptText } from "./receiptParse";
import cigarsData from "../data/cigars.json";
import type { Cigar } from "../types";

describe("buildCigarOcrCandidates", () => {
  it("expands Cusano Bundle Selection into vitola-scoped ids", () => {
    const cusano = (cigarsData as Cigar[]).find(
      (c) => c.id === "cig-cusano-bundle-selection",
    );
    expect(cusano).toBeTruthy();
    const cands = buildCigarOcrCandidates([cusano!]);
    const ids = cands.map((c) => c.id);
    expect(ids).toContain("cig-cusano-bundle-selection");
    expect(ids).toContain("cig-cusano-bundle-selection@robusto");
    expect(ids).toContain("cig-cusano-bundle-selection@figurado");
  });

  it("keeps Robusto and Figurado as separate receipt rows", () => {
    const cands = buildCigarOcrCandidates(cigarsData as Cigar[]);
    const rows = parseReceiptText(
      [
        "Bundle Selection by Cusano Robusto/16 1,00 Kom 25% 5,80 5,80",
        "Bundle Selection by Cusano Figurado/16 1,00 Kom 25% 5,70 5,70",
      ].join("\n"),
      cands,
    );
    const found = rows.map((r) => r.candidate?.id);
    expect(found).toContain("cig-cusano-bundle-selection@robusto");
    expect(found).toContain("cig-cusano-bundle-selection@figurado");
  });
});
