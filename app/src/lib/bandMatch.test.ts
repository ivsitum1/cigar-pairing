import { describe, it, expect } from "vitest";
import { fuseOcrAndBand } from "./bandMatch";
import type { OcrCandidate } from "./ocrMatch";

const candidates: OcrCandidate[] = [
  { id: "cig-a", label: "Partagas Serie D No.4", brand: "Partagas" },
  { id: "cig-b", label: "Cohiba Behike", brand: "Cohiba" },
];

describe("fuseOcrAndBand", () => {
  it("prefers strong text match", () => {
    const hit = fuseOcrAndBand("PARTAGAS SERIE D No.4 HABANA", candidates, [
      { cigarId: "cig-b", score: 0.99, refId: "x" },
    ]);
    expect(hit?.candidate.id).toBe("cig-a");
    expect(hit?.source).toBe("text");
  });

  it("uses band when text is weak", () => {
    const hit = fuseOcrAndBand("xyzabc", candidates, [
      { cigarId: "cig-b", score: 0.92, refId: "y" },
    ]);
    expect(hit?.candidate.id).toBe("cig-b");
    expect(hit?.source).toBe("band");
  });

  it("fuses when both agree", () => {
    const hit = fuseOcrAndBand("PARTAGAS SERIE D", candidates, [
      { cigarId: "cig-a", score: 0.8, refId: "z" },
    ]);
    expect(hit?.candidate.id).toBe("cig-a");
    expect(["fusion", "text"]).toContain(hit?.source);
  });
});
