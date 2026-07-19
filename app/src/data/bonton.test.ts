import { describe, it, expect } from "vitest";
import bonton from "./bonton.json";
import { parseLessonBody } from "../lib/parseLessonBody";

describe("bonton knjiga", () => {
  it("ima naslov, epigraf i 11 poglavlja uključujući salon", () => {
    expect(bonton.title.hr.length && bonton.title.en.length).toBeTruthy();
    expect(bonton.epigraph.hr.length && bonton.epigraph.en.length).toBeTruthy();
    expect(bonton.chapters.length).toBe(11);
    expect(bonton.chapters.map((c) => c.id)).toEqual([
      "b-spirit",
      "b-space",
      "b-offer",
      "b-pace",
      "b-ash",
      "b-table",
      "b-host",
      "b-lounge",
      "b-outdoors",
      "b-gift",
      "b-close",
    ]);
  });

  it("svako poglavlje ima id i dvojezicni title/body s odjeljcima", () => {
    for (const ch of bonton.chapters) {
      expect(ch.id.length, ch.id).toBeGreaterThan(0);
      expect(ch.title.hr.length && ch.title.en.length, ch.id).toBeTruthy();
      expect(ch.body.hr.length && ch.body.en.length, ch.id).toBeTruthy();
      for (const lang of ["hr", "en"] as const) {
        const blocks = parseLessonBody(ch.body[lang]);
        expect(
          blocks.some((b) => b.type === "section" && b.items.length > 0),
          `${ch.id} ${lang}`,
        ).toBe(true);
      }
    }
  });
});
