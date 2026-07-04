import { describe, it, expect } from "vitest";
import { matchOcrText } from "./OcrScan";
import cigarsData from "../data/cigars.json";
import rumsData from "../data/rums.json";

const cigarCandidates = (cigarsData as { id: string; brand: string; line: string }[]).map(
  (c) => ({ id: c.id, label: `${c.brand} ${c.line}` }),
);
const rumCandidates = (rumsData as { id: string; name: string }[]).map((r) => ({
  id: r.id,
  label: r.name,
}));

describe("OCR matcher", () => {
  it("prepoznaje bocu iz OCR teksta s bukom", () => {
    const ocr = "HAMPDEN\nESTATE\n8 YEARS\nPure Single Jamaican Rum 46% vol";
    const m = matchOcrText(ocr, rumCandidates);
    expect(m?.candidate.id).toBe("rum-hampden-estate-8");
  });

  it("prepoznaje cigaru iz teksta bande", () => {
    const ocr = "PARTAGAS\nSERIE D No.4\nHABANA CUBA";
    const m = matchOcrText(ocr, cigarCandidates);
    expect(m?.candidate.label.toLowerCase()).toContain("partag");
  });

  it("vraca null za nepovezan tekst", () => {
    expect(matchOcrText("xyzabc qwerty", rumCandidates)).toBeNull();
    expect(matchOcrText("", rumCandidates)).toBeNull();
  });
});
