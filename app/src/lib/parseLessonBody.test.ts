import { describe, it, expect } from "vitest";
import { parseLessonBody, splitItemLabel } from "./parseLessonBody";
import club101 from "../data/club101.json";

describe("parseLessonBody", () => {
  it("splits intro, headed bullets and closing paragraph", () => {
    const blocks = parseLessonBody(
      [
        "Uvodna rečenica o formatu.",
        "",
        "PAREJO (ravan kraj)",
        "• Robusto — ~5 × 50 (~45–60 min).",
        "• Toro — ~6 × 50.",
        "",
        "Karakteristike",
        "• Uži RG → više wrappera.",
        "",
        "Završna napomena o puro blendu.",
      ].join("\n"),
    );

    expect(blocks).toHaveLength(4);
    expect(blocks[0]).toEqual({ type: "paragraph", text: "Uvodna rečenica o formatu." });
    expect(blocks[1]).toMatchObject({
      type: "section",
      title: "PAREJO (ravan kraj)",
      items: [
        { kind: "bullet", text: "Robusto — ~5 × 50 (~45–60 min)." },
        { kind: "bullet", text: "Toro — ~6 × 50." },
      ],
    });
    expect(blocks[2]).toMatchObject({
      type: "section",
      title: "Karakteristike",
    });
    expect(blocks[3]).toEqual({
      type: "paragraph",
      text: "Završna napomena o puro blendu.",
    });
  });

  it("parses numbered sections", () => {
    const blocks = parseLessonBody(
      ["Sezona", "1. Obriši prašinu.", "2. Navlaži cedar.", "3. Pričekaj."].join("\n"),
    );
    expect(blocks).toHaveLength(1);
    expect(blocks[0]).toMatchObject({
      type: "section",
      title: "Sezona",
      items: [
        { kind: "number", text: "Obriši prašinu." },
        { kind: "number", text: "Navlaži cedar." },
        { kind: "number", text: "Pričekaj." },
      ],
    });
  });

  it("keeps mixed number and bullet items in one section", () => {
    const blocks = parseLessonBody(
      [
        "Redoslijed večeri",
        "1. Miris. 2. Gutljaj.",
        "• Espresso uz brandy.",
        "• Dva stila dovoljna.",
      ].join("\n"),
    );
    expect(blocks[0]).toMatchObject({
      type: "section",
      title: "Redoslijed večeri",
      items: [
        { kind: "number", text: "Miris. 2. Gutljaj." },
        { kind: "bullet", text: "Espresso uz brandy." },
        { kind: "bullet", text: "Dva stila dovoljna." },
      ],
    });
  });

  it("splitItemLabel finds em dash labels", () => {
    expect(splitItemLabel("Robusto — pun okus")).toEqual({
      label: "Robusto",
      rest: "pun okus",
    });
    expect(splitItemLabel("Uži RG → više wrappera")).toEqual({
      label: "Uži RG",
      rest: "više wrappera",
    });
    expect(splitItemLabel("samo tekst bez separatora")).toBeNull();
  });

  it("every club101 lesson parses into structured sections", () => {
    for (const track of Object.values(club101.tracks)) {
      for (const card of track) {
        for (const lang of ["hr", "en"] as const) {
          const blocks = parseLessonBody(card.body[lang]);
          expect(blocks.length, `${card.id} ${lang}`).toBeGreaterThanOrEqual(2);
          expect(
            blocks.some((b) => b.type === "section" && b.items.length > 0),
            `${card.id} ${lang}`,
          ).toBe(true);
        }
      }
    }
  });
});
