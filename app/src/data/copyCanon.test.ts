import { describe, expect, it } from "vitest";
import { parseLessonBody, splitItemLabel } from "../lib/parseLessonBody";
import { promptsFor } from "../lib/ratingPrompts";
import club from "./club.json";
import club101 from "./club101.json";
import dictionary from "./dictionary.json";
import lexicon from "./lexicon.json";
import ratingPrompts from "./ratingPrompts.json";

/**
 * HR copy canon (.cursor/rules/hr-copy-canon.mdc) provjeren nad sadržajem.
 * Kuriranu prozu piše više izvora — Club, 101, leksikon, rječnik, šprance —
 * i bez ovoga svaki od njih polako izmisli vlastitu nomenklaturu.
 */

/** Sva HR/EN proza iz kuriranih datoteka, kao [oznaka, tekst]. */
function curatedProse(): [string, string][] {
  const out: [string, string][] = [];
  const walk = (label: string, node: unknown) => {
    if (typeof node === "string") {
      out.push([label, node]);
      return;
    }
    if (Array.isArray(node)) {
      node.forEach((child, i) => walk(`${label}[${i}]`, child));
      return;
    }
    if (node && typeof node === "object") {
      for (const [key, value] of Object.entries(node)) {
        if (key === "aliases") continue; // aliasi su tražilice, ne tekuća proza
        walk(`${label}.${key}`, value);
      }
    }
  };
  walk("club", club);
  walk("club101", club101);
  walk("lexicon", lexicon);
  walk("dictionary", dictionary);
  walk("ratingPrompts", ratingPrompts);
  return out;
}

describe("HR copy canon — trećine", () => {
  // Riječi su često razdvojene („Prva, druga i zadnja trećina”, „usklađivanje u
  // drugoj”), pa se traži supojava unutar iste rečenice, a ne susjedstvo.
  const forbidden = (...patterns: RegExp[]) =>
    curatedProse()
      .filter(([, text]) => patterns.some((re) => re.test(text)))
      .map(([label]) => label);

  it("srednja trećina se ne zove „druga” ni „second third”", () => {
    expect(
      forbidden(
        /\bdrug[aeuoi][a-zšđčćž]*\b[^.!?]{0,80}?treć/i,
        /treć[a-zšđčćž]*[^.!?]{0,80}?\bdrug[aeuoi][a-zšđčćž]*\b/i,
        /\bsecond\b[^.!?]{0,80}?thirds?\b/i,
        // „…the first third; the second builds…” — redni broj bez imenice
        /\bthirds?\b[^.!?]{0,80}?\bsecond\b/i,
      ),
    ).toEqual([]);
  });

  it("zadnja trećina se ne zove „završna” — završetak ostaje piću", () => {
    expect(
      forbidden(
        /\bzavršn[a-zšđčćž]*\b[^.!?]{0,80}?treć/i,
        /treć[a-zšđčćž]*[^.!?]{0,80}?\bzavršn[a-zšđčćž]*\b/i,
      ),
    ).toEqual([]);
  });

  it("rječnik i leksikon dijele istu trijadu", () => {
    const thirds = dictionary.entries.find((e) => e.id === "thirds")!;
    expect(thirds.def.hr).toContain("prvu, srednju i zadnju trećinu");
    expect(thirds.def.en).toContain("first, middle, and final thirds");

    const trecine = lexicon.entries.find((e) => e.id === "trecine")!;
    for (const word of ["Prva trećina", "Srednja trećina", "Zadnja trećina"]) {
      expect(trecine.body, word).toContain(word);
    }

    const draw = club101.tracks.cigars.find((c) => c.id === "c-draw")!;
    for (const word of ["Prva —", "Srednja —", "Zadnja —"]) {
      expect(draw.body.hr, word).toContain(word);
    }

    const chips = promptsFor("pairing").find((q) => q.id === "thirds")!;
    expect(chips.suggestions.slice(0, 3).map((s) => s.hr)).toEqual([
      "prva",
      "srednja",
      "zadnja",
    ]);
    expect(chips.suggestions.slice(0, 3).map((s) => s.en)).toEqual([
      "first",
      "middle",
      "final",
    ]);
  });
});

describe("HR copy canon — obitelji nota", () => {
  /** Pet obitelji, pročitanih iz leksikona koji im je dom. */
  const families = (() => {
    const entry = lexicon.entries.find((e) => e.id === "obitelji-nota")!;
    const catalog = parseLessonBody(entry.body).find(
      (b) => b.type === "section" && b.title.startsWith("Katalog"),
    );
    expect(catalog?.type).toBe("section");
    return (catalog as { items: { text: string }[] }).items
      .map((item) => splitItemLabel(item.text)?.label.toLowerCase())
      .filter((x): x is string => Boolean(x));
  })();

  it("leksikon drži točno pet obitelji", () => {
    expect(families).toEqual(["slatko", "tamno", "drveno", "začin", "svježe"]);
  });

  it("rječnik definira isti skup, ne vlastiti", () => {
    const entry = dictionary.entries.find((e) => e.id === "flavor-family")!;
    expect(entry.term.hr).toBe("Obitelj nota");
    for (const family of families) {
      expect(entry.def.hr.toLowerCase(), family).toContain(family);
    }
    // stari, neusklađeni katalog ne smije se vratiti
    expect(entry.def.hr.toLowerCase()).not.toMatch(/orašasto|biljno|dimno/);
    // „obitelj okusa" preživljava samo kao alias za pretragu
    expect(entry.aliases).toContain("obitelj okusa");
  });

  it("šprance nude iste obitelji kao prve ponude na liniji Nota", () => {
    for (const context of ["cigar", "drink"] as const) {
      const notes = promptsFor(context).find((q) => q.id === "notes")!;
      expect(
        notes.suggestions.slice(0, families.length).map((s) => s.hr),
        context,
      ).toEqual(families);
    }
  });
});
