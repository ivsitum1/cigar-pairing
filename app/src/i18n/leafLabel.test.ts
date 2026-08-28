import { describe, expect, it } from "vitest";
import { leafLabel, leafMetaParts, leafOriginDisplay } from "./leafLabel";

describe("leafLabel", () => {
  it("prevodi goli engleski zemljopis u HR", () => {
    expect(leafLabel("Nicaragua", "hr")).toBe("Nikaragva");
    expect(leafLabel("Nicaraguan", "hr")).toBe("nikaragvanski");
    expect(leafLabel("Dominican Republic", "hr")).toBe("Dominikanska Republika");
    expect(leafLabel("Ecuador", "hr")).toBe("Ekvador");
    expect(leafLabel("Mexican San Andres", "hr")).toBe("meksički San Andres");
    expect(leafLabel("Brazilian", "hr")).toBe("brazilski");
  });

  it("na EN pretvara HR zemljopis i ostavlja engleske tokene", () => {
    expect(leafLabel("Nikaragva", "en")).toBe("Nicaragua");
    expect(leafLabel("Dominikanska Republika", "en")).toBe("Dominican Republic");
    expect(leafLabel("Nicaragua", "en")).toBe("Nicaragua");
    expect(leafLabel("Ecuador Habano", "en")).toBe("Ecuador Habano");
  });

  it("u složenim stringovima mijenja samo geo dijelove", () => {
    expect(leafLabel("Ecuador Habano", "hr")).toBe("Ekvador Habano");
    expect(leafLabel("San Andres, Brazilian Habano", "hr")).toBe(
      "San Andres, brazilski Habano",
    );
    expect(leafLabel("Habano (Nicaragua)", "hr")).toBe("Habano (Nikaragva)");
    expect(leafLabel("Connecticut", "hr")).toBe("Connecticut");
    expect(leafLabel("Maduro", "hr")).toBe("Maduro");
  });

  it("leafMetaParts ne ponavlja list kad je isto što i zemlja", () => {
    expect(leafMetaParts("Nicaragua", "Nikaragva", "hr")).toEqual(["Nikaragva"]);
    expect(leafMetaParts("Habano", "Nikaragva", "hr")).toEqual([
      "Habano",
      "Nikaragva",
    ]);
    expect(leafMetaParts("Nicaragua", "Nikaragva", "en")).toEqual(["Nicaragua"]);
  });

  it("leafOriginDisplay ne ponavlja isto podrijetlo i naziv", () => {
    expect(leafOriginDisplay("Nikaragva", "Nicaragua", "hr")).toBe("Nikaragva");
    expect(leafOriginDisplay("Nikaragva", "Habano", "hr")).toBe("Nikaragva · Habano");
    expect(leafOriginDisplay("Meksiko", "Mexican San Andres", "hr")).toBe(
      "Meksiko · meksički San Andres",
    );
  });
});
