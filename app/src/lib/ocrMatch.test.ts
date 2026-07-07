import { describe, it, expect } from "vitest";
import { matchOcrText, tokenize } from "./ocrMatch";
import cigarsData from "../data/cigars.json";
import rumsData from "../data/rums.json";

const cigarCandidates = (cigarsData as { id: string; brand: string; line: string }[]).map(
  (c) => ({ id: c.id, label: `${c.brand} ${c.line}`, brand: c.brand }),
);
const rumCandidates = (rumsData as { id: string; name: string }[]).map((r) => ({
  id: r.id,
  label: r.name,
}));

describe("OCR matcher", () => {
  // postojeci slucajevi (preseljeni iz OcrScan.test.ts)
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

  // novi: fuzzy tolerancija na OCR greske
  it("tolerira jednu krivu OCR zamjenu u brendu", () => {
    const ocr = "PARTAQAS\nSERIE D No.4"; // g -> q
    const m = matchOcrText(ocr, cigarCandidates);
    expect(m?.candidate.label.toLowerCase()).toContain("partag");
  });

  it("tolerira 0 umjesto O", () => {
    const ocr = "M0NTECRIST0\nOPEN EAGLE";
    const m = matchOcrText(ocr, cigarCandidates);
    expect(m?.candidate.label.toLowerCase()).toContain("montecristo");
  });

  it("kratki tokeni se ne matchaju fuzzy (nema laznih pogodaka)", () => {
    // 3-znakovni tokeni moraju biti egzaktni; smece ne smije proci prag
    expect(matchOcrText("ron dom abc", rumCandidates)).toBeNull();
  });

  // novi: dvofazni brend -> linija
  it("prepoznati brend suzuje kandidate", () => {
    const synth = [
      { id: "right", label: "Cohiba Panetela", brand: "Cohiba" },
      { id: "wrong", label: "Panetela Larga Panetela Fina", brand: "Fonseca" },
    ];
    // bez brend-faze "wrong" bi skupio vise bodova preko linije;
    // s brend-fazom pool se suzi na Cohibu
    const m = matchOcrText("COHIBA PANETELA LARGA FINA", synth);
    expect(m?.candidate.id).toBe("right");
  });
});

describe("tokenize", () => {
  it("normalizira dijakritike i baca kratke tokene", () => {
    expect(tokenize("Partagás No.4")).toEqual(["partagas"]);
  });
});
