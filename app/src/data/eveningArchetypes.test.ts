import { describe, expect, it } from "vitest";
import eveningArchetypes from "./eveningArchetypes.json";
import { parseLessonBody } from "../lib/parseLessonBody";

type LocalizedText = { hr: string; en: string };
type EveningArchetypes = {
  title: LocalizedText;
  intro: LocalizedText;
  entries: Array<{
    id: string;
    title: LocalizedText;
    body: LocalizedText;
    styleTags?: string[];
  }>;
};

const REQUIRED_ARCHETYPE_IDS = [
  "connecticut-amontillado",
  "maduro-tawny",
  "jamaica-full-wrapper",
  "agricole-citrus",
  "peat-strong-cuban",
  "espresso-short-vitola",
] as const;

const data = eveningArchetypes as EveningArchetypes;

describe("vecernji arhetipovi", () => {
  it("ima naslov, uvod i sest zadanih arhetipova redom", () => {
    expect(data.title.hr.length && data.title.en.length).toBeTruthy();
    expect(data.intro.hr.length && data.intro.en.length).toBeTruthy();
    expect(data.entries.length).toBeGreaterThanOrEqual(6);
    expect(data.entries.map((entry) => entry.id)).toEqual(REQUIRED_ARCHETYPE_IDS);
  });

  it("svaki arhetip je dvojezicni esej sa stilskim oznakama", () => {
    for (const entry of data.entries) {
      expect(entry.title.hr.length && entry.title.en.length, entry.id).toBeTruthy();
      expect(entry.body.hr.length, `${entry.id} hr`).toBeGreaterThan(350);
      expect(entry.body.en.length, `${entry.id} en`).toBeGreaterThan(350);
      expect(entry.styleTags?.length, entry.id).toBeGreaterThanOrEqual(2);

      for (const lang of ["hr", "en"] as const) {
        const blocks = parseLessonBody(entry.body[lang]);
        expect(
          blocks.some((block) => block.type === "section" && block.items.length >= 3),
          `${entry.id} ${lang}`,
        ).toBe(true);
      }
    }
  });

  it("ostaje na stilovima bez shop linkova i konkretnih SKU polja", () => {
    for (const entry of data.entries) {
      expect(Object.keys(entry).sort(), entry.id).toEqual(["body", "id", "styleTags", "title"]);
      expect(JSON.stringify(entry), entry.id).not.toMatch(/https?:\/\//);
    }
  });
});
