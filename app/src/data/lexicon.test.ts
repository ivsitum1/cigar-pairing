import { describe, it, expect } from "vitest";
import lexicon from "./lexicon.json";
import { parseLessonBody } from "../lib/parseLessonBody";

const REQUIRED_ENTRY_IDS = [
  "most",
  "gin-koktel-most",
  "tijelo-tijelo",
  "snaga-vs-tijelo",
  "trecine",
  "obitelji-nota",
  "ritam",
  "rijeci-za-stol",
  "mini-vjezbe",
] as const;

describe("pairing leksikon", () => {
  it("ima naslov, uvod i najmanje 8 unosa", () => {
    expect(lexicon.title.hr.length && lexicon.title.en.length).toBeTruthy();
    expect(lexicon.intro.hr.length && lexicon.intro.en.length).toBeTruthy();
    expect(lexicon.entries.length).toBeGreaterThanOrEqual(8);
    expect(lexicon.entries.map((entry) => entry.id)).toEqual(REQUIRED_ENTRY_IDS);
  });

  it("svaki unos ima id, hrvatski naslov i katalog u tijelu", () => {
    for (const entry of lexicon.entries) {
      expect(entry.id.length, entry.id).toBeGreaterThan(0);
      expect(entry.title.hr.length, entry.id).toBeGreaterThan(0);
      expect(entry.body.length, entry.id).toBeGreaterThan(0);
      expect(entry.body, entry.id).toContain("\n\n");
      expect(
        parseLessonBody(entry.body).some((block) => block.type === "section" && block.items.length > 0),
        entry.id,
      ).toBe(true);
    }
  });
});
