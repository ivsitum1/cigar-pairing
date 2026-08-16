import { describe, expect, it } from "vitest";
import { DRINKS } from "../data";
import {
  SCOTCH_REGIONS,
  SCOTLAND,
  scotchRegionCard,
  scotchRegionOf,
  whiskyStyleNote,
} from "./scotchRegion";

const WHISKIES = DRINKS.whisky;
const SCOTS = WHISKIES.filter((d) => d.country === SCOTLAND);

// Regije koje `region` u podacima ne imenuje — blend po definiciji miješa više
// njih, a golo "Škotska" je nezabilježeno. Te boce SMIJU ostati bez regije;
// svaka druga škotska regija koja se pojavi mora imati svoj ključ.
const REGIONLESS = new Set(["Škotska", "Škotska (blend)", "Škotska (blended malt)"]);

describe("škotske regije", () => {
  it("svaka boca s imenovanom regijom dobije ključ", () => {
    const unmapped = SCOTS.filter((d) => !REGIONLESS.has(d.region) && scotchRegionOf(d) == null);
    expect(unmapped.map((d) => `${d.id} (${d.region})`)).toEqual([]);
  });

  it("blendovi i nezabilježeno 'Škotska' namjerno nemaju regiju", () => {
    for (const d of SCOTS.filter((x) => REGIONLESS.has(x.region))) {
      expect(scotchRegionOf(d), d.id).toBeNull();
    }
  });

  it("ne pripisuje regiju boci izvan Škotske", () => {
    for (const d of WHISKIES.filter((x) => x.country !== SCOTLAND)) {
      expect(scotchRegionOf(d), d.id).toBeNull();
    }
    // Tajvanski Kavalan nosi stil "speyside-sherry" — stil nije regija
    const kavalan = WHISKIES.find((d) => d.country === "Tajvan" && d.style === "speyside-sherry");
    expect(kavalan && scotchRegionOf(kavalan)).toBeNull();
  });

  it("otoci idu u 'islands', a Islay ostaje svoj", () => {
    const by = (needle: string) => SCOTS.find((d) => d.region.startsWith(needle));
    expect(scotchRegionOf(by("Orkney")!)).toBe("islands");
    expect(scotchRegionOf(by("Skye")!)).toBe("islands");
    expect(scotchRegionOf(by("Jura")!)).toBe("islands");
    expect(scotchRegionOf(by("Islay")!)).toBe("islay");
    // "West Highlands" i "Highland, Škotska (liker)" su oboje Highland
    expect(scotchRegionOf(by("West Highlands")!)).toBe("highland");
  });

  it("svaki ključ ima dvojezičnu karticu s nazivom, sažetkom i tijelom", () => {
    for (const r of SCOTCH_REGIONS) {
      const card = scotchRegionCard(r);
      expect(card, r).toBeTruthy();
      for (const lang of ["hr", "en"] as const) {
        expect(card.label[lang].length, `${r} label ${lang}`).toBeGreaterThan(0);
        expect(card.summary[lang].length, `${r} summary ${lang}`).toBeGreaterThan(20);
        expect(card.body[lang].length, `${r} body ${lang}`).toBeGreaterThan(250);
        // tijelo se crta LessonBodyjem — bez bulleta ispadne zid teksta
        expect(card.body[lang], `${r} body ${lang} bullets`).toContain("•");
      }
    }
  });

  it("svaka regija u katalogu ima barem jednu bocu", () => {
    for (const r of SCOTCH_REGIONS) {
      expect(SCOTS.some((d) => scotchRegionOf(d) === r), r).toBe(true);
    }
  });

  it("svaka vrsta whiskyja u katalogu ima kratku pouku", () => {
    const styles = [...new Set(WHISKIES.map((d) => d.style))];
    const missing = styles.filter((s) => whiskyStyleNote(s) == null);
    expect(missing).toEqual([]);
  });

  it("pouke uz vrste su dvojezične", () => {
    for (const s of new Set(WHISKIES.map((d) => d.style))) {
      const note = whiskyStyleNote(s)!;
      expect(note.hr.length, `${s} hr`).toBeGreaterThan(20);
      expect(note.en.length, `${s} en`).toBeGreaterThan(20);
    }
  });
});
