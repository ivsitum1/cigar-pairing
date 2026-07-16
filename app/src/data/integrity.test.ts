import { describe, it, expect } from "vitest";
import { ALL_DRINKS, CIGARS, DRINKS } from "./index";
import { KNOWN_TAGS, normalizeTag } from "../engine/rules";

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

  it("body/sweetness pica i body/strength cigara su u rasponu 1-5", () => {
    for (const d of ALL_DRINKS) {
      expect(d.body, `${d.id} body`).toBeGreaterThanOrEqual(1);
      expect(d.body, `${d.id} body`).toBeLessThanOrEqual(5);
      expect(d.sweetness, `${d.id} sweetness`).toBeGreaterThanOrEqual(1);
      expect(d.sweetness, `${d.id} sweetness`).toBeLessThanOrEqual(5);
    }
    for (const c of CIGARS) {
      expect(c.body, `${c.id} body`).toBeGreaterThanOrEqual(1);
      expect(c.body, `${c.id} body`).toBeLessThanOrEqual(5);
      expect(c.strength, `${c.id} strength`).toBeGreaterThanOrEqual(1);
      expect(c.strength, `${c.id} strength`).toBeLessThanOrEqual(5);
    }
  });

  it("category polja odgovaraju datoteci iz koje pice dolazi", () => {
    for (const [cat, list] of Object.entries(DRINKS)) {
      for (const d of list) expect(d.category, d.id).toBe(cat);
    }
  });

  // regresija za "Club 500 6 X 60" bug: '500' iz imena parsiran kao duljina
  it("smokeTimeMin i duljina vitole su u realnim granicama", () => {
    for (const c of CIGARS) {
      if (c.smokeTimeMin) {
        expect(c.smokeTimeMin, `${c.id} smokeTimeMin`).toBeGreaterThanOrEqual(10);
        expect(c.smokeTimeMin, `${c.id} smokeTimeMin`).toBeLessThanOrEqual(240);
      }
      for (const v of c.vitolas) {
        const mm = v.format?.match(/x\s*(\d+)mm/i);
        if (mm) expect(Number(mm[1]), `${c.id} ${v.name} format`).toBeLessThanOrEqual(300);
        if (v.smokeTimeMin) {
          expect(v.smokeTimeMin, `${c.id} ${v.name}`).toBeLessThanOrEqual(240);
        }
      }
    }
  });

  it("cijene su pozitivne i min <= max", () => {
    for (const d of ALL_DRINKS) {
      if (d.priceEUR) {
        expect(d.priceEUR.min, d.id).toBeGreaterThan(0);
        expect(d.priceEUR.max, d.id).toBeGreaterThanOrEqual(d.priceEUR.min);
      }
      if (d.qualityScore != null) {
        expect(d.qualityScore, d.id).toBeGreaterThanOrEqual(0);
        expect(d.qualityScore, d.id).toBeLessThanOrEqual(10);
      }
    }
    for (const c of CIGARS) {
      if (c.priceEUR != null) expect(c.priceEUR, c.id).toBeGreaterThan(0);
      for (const v of c.vitolas) {
        if (v.priceEUR != null) expect(v.priceEUR, `${c.id} ${v.name}`).toBeGreaterThan(0);
      }
    }
  });

  it("markets sadrze samo poznata trzista", () => {
    const known = new Set(["HR", "EU", "USA", "WW"]);
    for (const c of CIGARS) {
      for (const m of c.markets) expect(known.has(m), `${c.id}: ${m}`).toBe(true);
    }
  });

  // svaki tag u podacima mora (nakon normalizacije u rules.ts) biti poznat
  // engineu — inace tiho ne donosi bodove; novi tag = svjesno dodati u
  // COMPLEMENTS/TAG_ALIASES, ne pustiti ga da propadne
  it("svi flavor tagovi su u engine vokabularu (nakon aliasa)", () => {
    const unknown = new Set<string>();
    for (const d of ALL_DRINKS) {
      for (const t of d.flavorTags) {
        if (!KNOWN_TAGS.has(normalizeTag(t))) unknown.add(`drink:${t}`);
      }
    }
    for (const c of CIGARS) {
      for (const t of c.flavorTags) {
        if (!KNOWN_TAGS.has(normalizeTag(t))) unknown.add(`cigar:${t}`);
      }
    }
    expect([...unknown].sort()).toEqual([]);
  });
});
