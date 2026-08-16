// localStorage je tuđi teritorij: stari zapis, ručna izmjena ili zapis iz
// drugog appa ne smiju proći kao prijava. Potpis mora izgledati kao potpis.
import { describe, expect, it } from "vitest";
import { normalizeAccount } from "./account";

describe("čitanje zapisane prijave", () => {
  it("prima uredan zapis", () => {
    const out = normalizeAccount({
      name: "  Ivan   Šitum ",
      tasterId: "g_abc123abc123",
      at: "2026-08-16T10:00:00.000Z",
    });
    expect(out).toEqual({
      name: "Ivan Šitum",
      tasterId: "g_abc123abc123",
      at: "2026-08-16T10:00:00.000Z",
    });
  });

  it("odbija sve što nije potpis našeg oblika", () => {
    for (const tasterId of [
      undefined,
      "",
      "Ivan",
      "g_ABC123ABC123",
      "g_abc123",
      "g_abc123abc123x",
      "abc123abc123",
      42,
    ]) {
      expect(normalizeAccount({ name: "Ivan", tasterId }), String(tasterId)).toBeNull();
    }
  });

  it("odbija zapis koji uopće nije objekt", () => {
    expect(normalizeAccount(null)).toBeNull();
    expect(normalizeAccount("g_abc123abc123")).toBeNull();
  });

  it("zapis bez datuma dobije današnji, ne pada", () => {
    const out = normalizeAccount({ name: "Ivan", tasterId: "g_abc123abc123" });
    expect(out?.tasterId).toBe("g_abc123abc123");
    expect(Number.isNaN(Date.parse(out!.at))).toBe(false);
  });
});
