import { describe, expect, it } from "vitest";
import hrGuide from "./hrGuide.json";
import { parseLessonBody } from "../lib/parseLessonBody";

const REQUIRED_SECTION_IDS = [
  "zakon-praksa-duhan",
  "karta-pice",
  "karta-duhan-referentno",
  "cijena-link-app",
  "prvi-kit",
  "sezona-zaliha",
  "poklon",
] as const;

type LocalizedText = { hr: string; en: string };
type HrGuide = {
  title: LocalizedText;
  intro: LocalizedText;
  sections: Array<{
    id: string;
    title: LocalizedText;
    body: LocalizedText;
  }>;
};

const guide = hrGuide as HrGuide;

describe("HR vodic kupnje", () => {
  it("ima sedam zadanih odjeljaka redom", () => {
    expect(guide.title.hr.length && guide.title.en.length).toBeTruthy();
    expect(guide.intro.hr.length && guide.intro.en.length).toBeTruthy();
    expect(guide.sections.map((section) => section.id)).toEqual(REQUIRED_SECTION_IDS);
  });

  it("svaki odjeljak je dvojezican i praktican katalog", () => {
    for (const section of guide.sections) {
      expect(section.title.hr.length && section.title.en.length, section.id).toBeTruthy();
      expect(section.body.hr.length, `${section.id} hr`).toBeGreaterThan(250);
      expect(section.body.en.length, `${section.id} en`).toBeGreaterThan(250);
      for (const lang of ["hr", "en"] as const) {
        const blocks = parseLessonBody(section.body[lang]);
        expect(
          blocks.some((block) => block.type === "section" && block.items.length >= 3),
          `${section.id} ${lang}`,
        ).toBe(true);
      }
    }
  });

  it("objasnjava da Kupi znaci pouzdan product URL, inace Trazi online", () => {
    const section = guide.sections.find((item) => item.id === "cijena-link-app");
    expect(section).toBeTruthy();
    expect(section?.body.hr).toContain("Kupi");
    expect(section?.body.hr).toContain("pouzdan product URL");
    expect(section?.body.hr).toContain("Traži online");
    expect(section?.body.hr).toContain("drinkBuyLink");
    expect(section?.body.en).toContain("Buy");
    expect(section?.body.en).toContain("trusted product URL");
    expect(section?.body.en).toContain("Search online");
    expect(section?.body.en).toContain("drinkBuyLink");
  });
});
