import { describe, it, expect } from "vitest";
import club from "./club.json";

describe("klub sadrzaj", () => {
  it("kviz ima 50+ pitanja, svako s 4 odgovora, tocnim indeksom i objasnjenjem", () => {
    expect(club.quiz.length).toBeGreaterThanOrEqual(79);
    for (const q of club.quiz) {
      expect(q.a.length, q.q.hr).toBe(4);
      expect(q.correct, q.q.hr).toBeGreaterThanOrEqual(0);
      expect(q.correct, q.q.hr).toBeLessThan(4);
      expect(q.q.hr.length && q.q.en.length, q.q.hr).toBeTruthy();
      expect(q.why.hr.length && q.why.en.length, q.q.hr).toBeTruthy();
      for (const a of q.a) expect(a.hr.length && a.en.length, q.q.hr).toBeTruthy();
    }
  });

  it("zanimljivosti: 45+ dvojezicnih", () => {
    expect(club.facts.length).toBeGreaterThanOrEqual(80);
    for (const f of club.facts) expect(f.hr.length && f.en.length).toBeTruthy();
  });

  it("citati: 20+, svi s autorom i dvojezicnim tekstom", () => {
    expect(club.quotes.length).toBeGreaterThanOrEqual(20);
    for (const q of club.quotes) {
      expect(q.author.length).toBeGreaterThan(0);
      expect(q.text.hr.length && q.text.en.length, q.author).toBeTruthy();
    }
  });
});
