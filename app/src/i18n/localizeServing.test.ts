import { describe, it, expect } from "vitest";
import { localizeServing } from "./index";

describe("localizeServing", () => {
  it("HR ostavlja original", () => {
    expect(localizeServing("Čisto", "hr")).toBe("Čisto");
    expect(localizeServing("Cisto", "hr")).toBe("Cisto");
  });

  it("EN: točan ključ i dijakritika-fold (Čisto → Neat)", () => {
    expect(localizeServing("Cisto", "en")).toBe("Neat");
    expect(localizeServing("Čisto", "en")).toBe("Neat");
    expect(localizeServing("Cisto / kap vode", "en")).toBe("Neat / drop of water");
    expect(localizeServing("Čisto / kap vode", "en")).toBe("Neat / drop of water");
  });

  it("EN: token-fallback za kombinacije izvan mape", () => {
    expect(localizeServing("Čisto / Caipirinha", "en")).toBe("Neat / Caipirinha");
  });

  it("EN: nepoznat string ostaje netaknut", () => {
    expect(localizeServing("Neki nepoznati način", "en")).toBe("Neki nepoznati način");
  });
});
