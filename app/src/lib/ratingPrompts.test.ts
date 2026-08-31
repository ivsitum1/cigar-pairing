import { describe, expect, it } from "vitest";
import ratingPrompts from "../data/ratingPrompts.json";
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
