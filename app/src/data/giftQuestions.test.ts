import { describe, expect, it } from "vitest";
import giftQuestions from "../data/giftQuestions.json";
import type { GiftAnswers } from "../lib/giftFinder";

type Question = (typeof giftQuestions)[number];

const QUESTION_IDS = ["recipient", "budget", "intensity", "drink", "shape"] as const;

describe("giftQuestions.json", () => {
  it("ima pet pitanja u planiranom redoslijedu", () => {
    expect(giftQuestions.map((q) => q.id)).toEqual([...QUESTION_IDS]);
  });

  it("svako pitanje je dvojezično i ima 'ne znam'", () => {
    for (const q of giftQuestions as Question[]) {
      expect(q.prompt.hr.length).toBeGreaterThan(3);
      expect(q.prompt.en.length).toBeGreaterThan(3);
      for (const opt of q.options) {
        expect(opt.label.hr.length).toBeGreaterThan(0);
        expect(opt.label.en.length).toBeGreaterThan(0);
      }
      expect(q.options.some((o) => o.id === "unknown")).toBe(true);
    }
  });

  it("id opcija odgovaraju GiftAnswers unionu", () => {
    const allowed: Record<string, Set<string>> = {
      recipient: new Set(["regular", "beginner", "drinks-only", "unknown"]),
      budget: new Set(["under20", "20to40", "40to60", "60to100", "unknown"]),
      drink: new Set(["whisky", "rum", "brandy", "wine", "unknown"]),
      intensity: new Set(["mild", "medium", "bold", "unknown"]),
      shape: new Set(["cigar", "bottle", "pairing", "unknown"]),
    };
    for (const q of giftQuestions as Question[]) {
      const set = allowed[q.id];
      expect(set).toBeTruthy();
      for (const opt of q.options) {
        expect(set!.has(opt.id)).toBe(true);
      }
    }
    // smoke: tipovi se slažu
    const _a: GiftAnswers = {
      recipient: "unknown",
      budget: "unknown",
      drink: "unknown",
      intensity: "unknown",
      shape: "unknown",
    };
    expect(_a.recipient).toBe("unknown");
  });
});
