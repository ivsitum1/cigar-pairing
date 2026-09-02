import { describe, expect, it } from "vitest";
import club101 from "../data/club101.json";
import lexicon from "../data/lexicon.json";
import ratingPrompts from "../data/ratingPrompts.json";
import { STRINGS } from "../i18n";
import { parseLessonBody, splitItemLabel } from "./parseLessonBody";
import {
  appendPromptStarter,
  appendSuggestion,
  applySkeleton,
  isBlankOrTemplateAfterColon,
  promptsFor,
  ratingScaleSummary,
  skeletonFor,
  starterKey,
} from "../lib/ratingPrompts";

describe("ratingPrompts.json", () => {
  it("ima tri konteksta s pitanjima, skeletonima i prijedlozima", () => {
    for (const key of ["pairing", "cigar", "drink"] as const) {
      const block = ratingPrompts.contexts[key];
      expect(block.questions.length).toBeGreaterThanOrEqual(3);
      expect(block.skeleton.hr.length).toBeGreaterThan(10);
      expect(block.skeleton.en.length).toBeGreaterThan(10);
      for (const q of block.questions) {
        expect(q.label.hr.length).toBeGreaterThan(0);
        expect(q.starter.hr).toMatch(/:\s*$|—\s*$/);
        expect(q.starter.en).toMatch(/:\s*$|—\s*$/);
        expect(q.suggestions.length).toBeGreaterThanOrEqual(4);
        for (const s of q.suggestions) {
          expect(s.hr.length).toBeGreaterThan(0);
          expect(s.en.length).toBeGreaterThan(0);
        }
      }
    }
  });

  it("ljestvica pokriva 1–10 bez rupa", () => {
    const bands = ratingPrompts.ratingScale;
    expect(bands[0]?.min).toBe(1);
    expect(bands[bands.length - 1]?.max).toBe(10);
    for (let i = 1; i < bands.length; i++) {
      expect(bands[i].min).toBe(bands[i - 1].max + 1);
    }
  });

  it("pairing skeleton drži most i trećinu kao u Club 101", () => {
    const sk = ratingPrompts.contexts.pairing.skeleton.hr;
    expect(sk).toMatch(/Most:/);
    expect(sk).toMatch(/Trećina:/);
    expect(sk).toMatch(/Bi li opet:/);
  });
});

describe("ratingPrompts helpers", () => {
  it("starterKey čita oznaku do dvotočke", () => {
    expect(starterKey("Most: ")).toBe("most");
    expect(starterKey("Bridge: cocoa")).toBe("bridge");
  });

  it("appendPromptStarter ne duplicira istu liniju", () => {
    const once = appendPromptStarter("", "Most: ");
    expect(once).toBe("Most: ");
    const twice = appendPromptStarter(once + "kakao", "Most: ");
    expect(twice).toBe("Most: kakao");
    const next = appendPromptStarter(twice, "Trećina: ");
    expect(next).toBe("Most: kakao\nTrećina: ");
  });

  it("applySkeleton puni samo prazno polje", () => {
    const sk = skeletonFor("cigar", "hr");
    expect(applySkeleton("", sk)).toBe(sk);
    expect(applySkeleton("  ", sk)).toBe(sk);
    expect(applySkeleton("već ima", sk)).toBe("već ima");
  });

  it("promptsFor i scale summary rade za oba jezika", () => {
    expect(promptsFor("drink").some((q) => q.id === "serve")).toBe(true);
    expect(ratingScaleSummary("hr")).toContain("shortlist");
    expect(ratingScaleSummary("en")).toContain("reference");
  });

  it("isBlankOrTemplateAfterColon prepoznaje izbornike", () => {
    expect(isBlankOrTemplateAfterColon("")).toBe(true);
    expect(isBlankOrTemplateAfterColon("  ")).toBe(true);
    expect(isBlankOrTemplateAfterColon("usklađeno / cigara jača")).toBe(true);
    expect(isBlankOrTemplateAfterColon("kakao")).toBe(false);
  });

  it("appendSuggestion puni i nadograđuje liniju", () => {
    const a = appendSuggestion("", "Most: ", "kakao");
    expect(a).toBe("Most: kakao");
    const b = appendSuggestion(a, "Most: ", "orah");
    expect(b).toBe("Most: kakao, orah");
    const c = appendSuggestion(b, "Most: ", "kakao");
    expect(c).toBe("Most: kakao, orah");
    const d = appendSuggestion("Tijela: usklađeno / cigara jača / piće jače — ", "Tijela: ", "usklađeno");
    expect(d).toBe("Tijela: usklađeno");
  });
});

/**
 * Nomenklatura špranci ima tri izvora istine i svi moraju govoriti isto:
 * ratingPrompts.json (tipke), i18n placeholderi (prazno polje) i Club 101
 * t-notebook + leksikon (tekst koji tu nomenklaturu objašnjava).
 */
describe("nomenklatura bilješke", () => {
  const CONTEXTS = ["pairing", "cigar", "drink"] as const;

  const PLACEHOLDER_KEY = {
    pairing: "coll.notePlaceholder",
    cigar: "coll.notePlaceholderCigar",
    drink: "coll.notePlaceholderDrink",
  } as const;

  const tNotebook = club101.tracks.tips.find((c) => c.id === "t-notebook")!;

  it("skeleton je točno red startera iz pitanja", () => {
    for (const ctx of CONTEXTS) {
      for (const lang of ["hr", "en"] as const) {
        const expected = promptsFor(ctx)
          .map((q) => q.starter[lang])
          .join("\n");
        expect(skeletonFor(ctx, lang), `${ctx}/${lang}`).toBe(expected);
      }
    }
  });

  it("placeholder nabraja iste linije kao starteri, istim redom", () => {
    for (const ctx of CONTEXTS) {
      for (const lang of ["hr", "en"] as const) {
        const placeholder = STRINGS[PLACEHOLDER_KEY[ctx]][lang]
          .replace(/…\s*$/, "")
          .split("·")
          .map((part) => part.trim().toLowerCase())
          .filter(Boolean);
        const starters = promptsFor(ctx).map((q) => starterKey(q.starter[lang]));
        expect(placeholder, `${ctx}/${lang}`).toEqual(starters);
      }
    }
  });

  it("t-notebook opisuje red špranci koji aplikacija stvarno umeće", () => {
    for (const lang of ["hr", "en"] as const) {
      for (const ctx of CONTEXTS) {
        const order = promptsFor(ctx)
          .map((q) => starterKey(q.starter[lang]))
          .join(", ");
        expect(tNotebook.body[lang].toLowerCase(), `${ctx}/${lang}`).toContain(order);
      }
    }
  });

  it("most nudi sve riječi koje t-notebook nabraja kao mostove", () => {
    const bridge = promptsFor("pairing").find((q) => q.id === "bridge")!;
    for (const lang of ["hr", "en"] as const) {
      const listed = tNotebook.body[lang]
        .split("\n")
        .find((line) => /^•\s*(Most|Bridge)\b/.test(line))!
        .split(":")[1]
        .split(",")
        .map((w) => w.trim().replace(/\.$/, "").toLowerCase())
        .filter(Boolean);
      const offered = bridge.suggestions.map((s) => s[lang].toLowerCase());
      for (const word of listed) {
        expect(offered, `${word} (${lang})`).toContain(word);
      }
    }
  });

  it("presuda u t-notebooku citira ljestvicu ocjene iz špranci", () => {
    for (const lang of ["hr", "en"] as const) {
      expect(tNotebook.body[lang], lang).toContain(ratingScaleSummary(lang));
    }
  });

  it("nota kreće od pet obitelji iz leksikona", () => {
    const entry = lexicon.entries.find((e) => e.id === "obitelji-nota")!;
    const catalog = parseLessonBody(entry.body).find(
      (b) => b.type === "section" && b.title.startsWith("Katalog"),
    );
    expect(catalog?.type).toBe("section");
    const families = (catalog as { items: { text: string }[] }).items
      .map((item) => splitItemLabel(item.text)?.label.toLowerCase())
      .filter((x): x is string => Boolean(x));
    expect(families).toEqual(["slatko", "tamno", "drveno", "začin", "svježe"]);

    for (const ctx of ["cigar", "drink"] as const) {
      const notes = promptsFor(ctx).find((q) => q.id === "notes")!;
      const head = notes.suggestions.slice(0, families.length).map((s) => s.hr);
      expect(head, ctx).toEqual(families);
    }
  });

  it("draw ostaje posuđenica iz HR copy canona, bez calque prijevoda", () => {
    const draw = promptsFor("cigar").find((q) => q.id === "draw")!;
    expect(draw.label.hr).toBe("Draw");
    expect(starterKey(draw.starter.hr)).toBe("draw");
    const hrText = [draw.hint.hr, ...draw.suggestions.map((s) => s.hr)].join(" ");
    expect(hrText.toLowerCase()).not.toMatch(/\bvlak\b|povlačenj/);
  });
});
