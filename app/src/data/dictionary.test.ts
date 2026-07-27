import { describe, it, expect } from "vitest";
import dictionary from "./dictionary.json";

const CATEGORIES = new Set(["cigar", "drink", "pairing", "table"]);

describe("club dictionary", () => {
  it("has bilingual title and intro", () => {
    expect(dictionary.title.hr.length && dictionary.title.en.length).toBeTruthy();
    expect(dictionary.intro.hr.length && dictionary.intro.en.length).toBeTruthy();
  });

  it("has expansive bilingual entries with valid links", () => {
    expect(dictionary.entries.length).toBeGreaterThanOrEqual(250);
    const ids = new Set(dictionary.entries.map((e) => e.id));
    expect(ids.size).toBe(dictionary.entries.length);
    for (const e of dictionary.entries) {
      expect(CATEGORIES.has(e.category), e.id).toBe(true);
      expect(e.term.hr.length && e.term.en.length, e.id).toBeTruthy();
      expect(e.def.hr.length && e.def.en.length, e.id).toBeTruthy();
      expect(e.body.hr.length && e.body.en.length, e.id).toBeTruthy();
      expect(Array.isArray(e.aliases), e.id).toBe(true);
      expect(Array.isArray(e.seeAlso), e.id).toBe(true);
      for (const id of e.seeAlso) {
        expect(ids.has(id), `${e.id}->${id}`).toBe(true);
      }
      for (const d of e.doNotConfuse ?? []) {
        expect(ids.has(d.with), `${e.id} confuse ${d.with}`).toBe(true);
        expect(d.note.hr.length && d.note.en.length, e.id).toBeTruthy();
      }
    }
  });
});
