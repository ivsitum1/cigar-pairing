import { describe, it, expect } from "vitest";
import { ALL_DRINKS, CIGARS } from "./index";

// Cuva integritet generiranih indeksa nakon regeneracije pipeline-ima.
describe("integritet podataka", () => {
  it("svi ID-jevi cigara su jedinstveni", () => {
    const ids = CIGARS.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("svi ID-jevi pica su jedinstveni (rum+whisky+brandy+gin+kava)", () => {
    const ids = ALL_DRINKS.map((d) => d.id);
    const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
    expect(dupes).toEqual([]);
  });

  it("svako pice ima obavezna polja za UI/engine", () => {
    for (const d of ALL_DRINKS) {
      expect(d.name?.length, d.id).toBeGreaterThan(0);
      expect(typeof d.body, d.id).toBe("number");
      expect(typeof d.sweetness, d.id).toBe("number");
      expect(Array.isArray(d.flavorTags), d.id).toBe(true);
      expect(typeof d.pairable, d.id).toBe("boolean");
    }
  });

  // neutralna uredjivacka politika: deklaracija umjesto osude
  it("nema pezorativnih izraza u notes/region — sve neutralno", () => {
    const banned = /ne za cigaru|jeftin|precijenjen|purist|apsurdn/i;
    for (const d of ALL_DRINKS) {
      const txt = `${d.notes?.hr ?? ""} ${d.notes?.en ?? ""} ${d.region ?? ""} ${d.additiveDetail ?? ""}`;
      expect(banned.test(txt), `${d.id}: ${txt}`).toBe(false);
    }
  });

  it("sva pica su pairable — engine posteno boduje, ne cenzurira", () => {
    for (const d of ALL_DRINKS) {
      expect(d.pairable, d.id).toBe(true);
    }
  });

  it("svaka cigara ima barem jednu vitolu i markets", () => {
    for (const c of CIGARS) {
      expect(c.vitolas.length, c.id).toBeGreaterThan(0);
      expect(c.markets.length, c.id).toBeGreaterThan(0);
    }
  });
});
