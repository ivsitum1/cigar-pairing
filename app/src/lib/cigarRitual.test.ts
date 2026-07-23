import { describe, it, expect } from "vitest";
import { ritualHint } from "./cigarRitual";

describe("ritualHint", () => {
  it("null kad trajanje nije poznato ili je 0", () => {
    expect(ritualHint(null, "hr")).toBeNull();
    expect(ritualHint(undefined, "hr")).toBeNull();
    expect(ritualHint(0, "hr")).toBeNull();
  });

  it("kratko (≤30) — brz ritam", () => {
    const h = ritualHint(25, "hr");
    expect(h?.icon).toBe("⚡");
    expect(h?.text).toContain("Kratka");
    expect(h?.text).toContain("25");
  });

  it("srednje (31–74)", () => {
    const h = ritualHint(50, "hr");
    expect(h?.icon).toBe("⏱");
    expect(h?.text).toContain("50");
  });

  it("dugo (≥75) — sporo pijuckanje", () => {
    const h = ritualHint(90, "hr");
    expect(h?.icon).toBe("⏳");
    expect(h?.text).toContain("Duga");
    expect(h?.text).toContain("90");
  });

  it("granice 30 i 75", () => {
    expect(ritualHint(30, "hr")?.icon).toBe("⚡");
    expect(ritualHint(31, "hr")?.icon).toBe("⏱");
    expect(ritualHint(74, "hr")?.icon).toBe("⏱");
    expect(ritualHint(75, "hr")?.icon).toBe("⏳");
  });

  it("engleska varijanta", () => {
    expect(ritualHint(90, "en")?.text).toContain("Long cigar");
    expect(ritualHint(20, "en")?.text).toContain("Short cigar");
  });
});
