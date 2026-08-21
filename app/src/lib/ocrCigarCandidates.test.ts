import { describe, it, expect } from "vitest";
import { buildCigarOcrCandidates } from "./ocrCigarCandidates";
import { parseReceiptText } from "./receiptParse";
import { matchOcrText } from "./ocrMatch";
import cigarsData from "../data/cigars.json";
import type { Cigar } from "../types";

const allCands = () => buildCigarOcrCandidates(cigarsData as Cigar[]);

describe("buildCigarOcrCandidates", () => {
  it("expands every multi-vitola line, not only Cusano", () => {
    const cands = allCands();
    const scoped = cands.filter((c) => c.id.includes("@"));
    expect(scoped.length).toBeGreaterThan(1000);
    expect(cands.some((c) => c.id === "cig-cusano-bundle-selection@figurado")).toBe(
      true,
    );
    expect(cands.some((c) => c.id.startsWith("cig-don-tomas-bundle@"))).toBe(true);
    expect(cands.some((c) => c.id === "cig-oliva-serie-v@torpedo")).toBe(true);
  });

  it("keeps Cusano Robusto and Figurado as separate receipt rows", () => {
    const rows = parseReceiptText(
      [
        "Bundle Selection by Cusano Robusto/16 1,00 Kom 25% 5,80 5,80",
        "Bundle Selection by Cusano Figurado/16 1,00 Kom 25% 5,70 5,70",
      ].join("\n"),
      allCands(),
    );
    const found = rows.map((r) => r.candidate?.id);
    expect(found).toContain("cig-cusano-bundle-selection@robusto");
    expect(found).toContain("cig-cusano-bundle-selection@figurado");
  });

  it("keeps Don Tomas Churchill and Rothschild separate", () => {
    const rows = parseReceiptText(
      [
        "DON TOMAS CHURCHILL 1 KOM 3,90 3,90",
        "DON TOMAS ROTHSCHILD 1 KOM 3,60 3,60",
        "DON TOMAS CHURCHILL 1 KOM 3,90 3,90",
      ].join("\n"),
      allCands(),
    );
    const found = rows.map((r) => r.candidate?.id);
    expect(found).toContain("cig-don-tomas-bundle@churchill");
    expect(found).toContain("cig-don-tomas-bundle@rothschild");
    const churchill = rows.find(
      (r) => r.candidate?.id === "cig-don-tomas-bundle@churchill",
    );
    expect(churchill?.qty).toBe(2);
  });

  it("scopes Oliva Serie V Torpedo to vitola id", () => {
    const m = matchOcrText("Oliva Serie V Torpedo/24", allCands());
    expect(m?.candidate.id).toBe("cig-oliva-serie-v@torpedo");
  });

  it("uses barcode hint when receipt row text is too weak on its own", () => {
    const rows = parseReceiptText(
      "ARTIKL 8720400383184 1 KOM 3,60 3,60",
      allCands(),
    );
    expect(rows[0]?.candidate?.id).toBe("cig-don-tomas-bundle@rothschild");
    expect(rows[0]?.barcodeCandidate?.id).toBe("cig-don-tomas-bundle@rothschild");
    expect(rows[0]?.selected).toBe(true);
  });
});
