import { describe, it, expect } from "vitest";
import type { PairingResult } from "../types";
import {
  brandDiverse,
  dayKey,
  softBand,
  softBandWindow,
  stableHash,
} from "./softBandRank";

type Item = { id: string; brand: string };

function r(id: string, brand: string, score: number): PairingResult<Item> {
  return { item: { id, brand }, score, reasons: [] };
}

describe("softBandRank", () => {
  it("softBand keeps only scores within margin of max", () => {
    const ranked = [r("a", "A", 90), r("b", "B", 86), r("c", "C", 84), r("d", "D", 70)];
    const band = softBand(ranked, 5);
    expect(band.map((x) => x.item.id)).toEqual(["a", "b"]);
  });

  it("brandDiverse keeps first (highest) per brand", () => {
    const ranked = [
      r("a1", "Acme", 95),
      r("a2", "Acme", 94),
      r("b1", "Beta", 93),
      r("c1", "Chi", 92),
    ];
    expect(brandDiverse(ranked).map((x) => x.item.id)).toEqual([
      "a1",
      "b1",
      "c1",
    ]);
  });

  it("same dayKey yields the same window", () => {
    const ranked = [
      r("a", "A", 90),
      r("b", "B", 90),
      r("c", "C", 89),
      r("d", "D", 88),
      r("e", "E", 87),
      r("f", "F", 86),
    ];
    const opts = {
      anchorId: "drink-x",
      dayKey: "2026-07-26",
      cycle: 0,
      keyOf: (i: Item) => i.brand,
    };
    const w1 = softBandWindow(ranked, opts);
    const w2 = softBandWindow(ranked, opts);
    expect(w1.window.map((x) => x.item.id)).toEqual(
      w2.window.map((x) => x.item.id),
    );
  });

  it("different dayKey can rotate #1 when bandSize > 1", () => {
    const ranked = Array.from({ length: 12 }, (_, i) =>
      r(`c${i}`, `Brand${i}`, 90 - (i % 3)),
    );
    // all scores 88–90 → all in band of margin 5
    const a = softBandWindow(ranked, {
      anchorId: "drink-y",
      dayKey: "2026-01-01",
      cycle: 0,
      keyOf: (i: Item) => i.brand,
    });
    const b = softBandWindow(ranked, {
      anchorId: "drink-y",
      dayKey: "2026-01-02",
      cycle: 0,
      keyOf: (i: Item) => i.brand,
    });
    expect(a.band.length).toBeGreaterThan(1);
    // Over many day keys at least one differs — check these two hashes differ
    const h1 = stableHash("drink-y|2026-01-01") % a.band.length;
    const h2 = stableHash("drink-y|2026-01-02") % a.band.length;
    if (h1 !== h2) {
      expect(a.window[0].item.id).not.toBe(b.window[0].item.id);
    } else {
      // rare collision: still assert window length / band
      expect(a.window).toHaveLength(3);
    }
  });

  it("cycle advances the window by windowSize within the pool", () => {
    const ranked = [
      r("a", "A", 90),
      r("b", "B", 90),
      r("c", "C", 90),
      r("d", "D", 90),
      r("e", "E", 90),
      r("f", "F", 90),
    ];
    const base = {
      anchorId: "drink-z",
      dayKey: "2026-07-26",
      keyOf: (i: Item) => i.brand,
    };
    const w0 = softBandWindow(ranked, { ...base, cycle: 0 });
    const w1 = softBandWindow(ranked, { ...base, cycle: 1 });
    expect(w0.window).toHaveLength(3);
    expect(w1.window).toHaveLength(3);
    expect(w0.window.map((x) => x.item.id)).not.toEqual(
      w1.window.map((x) => x.item.id),
    );
    // cycle 1 should be the next three after cycle 0 in the rotated pool
    const n = w0.total;
    const baseOffset =
      stableHash(`${base.anchorId}|${base.dayKey}`) % n;
    const expected1 = [0, 1, 2].map(
      (i) => ranked[(baseOffset + 3 + i) % n].item.id,
    );
    expect(w1.window.map((x) => x.item.id)).toEqual(expected1);
  });

  it("falls back when band is smaller than windowSize", () => {
    const ranked = [
      r("a", "A", 100),
      r("b", "B", 90),
      r("c", "C", 89),
      r("d", "D", 88),
    ];
    // band margin 5 → only "a" (100); fallback to diverse (≥3)
    const { window, band, total } = softBandWindow(ranked, {
      anchorId: "drink-fb",
      dayKey: "2026-07-26",
      cycle: 0,
      keyOf: (i: Item) => i.brand,
    });
    expect(band).toHaveLength(1);
    expect(total).toBe(4);
    expect(window).toHaveLength(3);
  });

  it("dayKey uses UTC YYYY-MM-DD", () => {
    expect(dayKey(new Date("2026-07-26T23:30:00.000Z"))).toBe("2026-07-26");
  });

  it("stableHash is deterministic", () => {
    expect(stableHash("abc")).toBe(stableHash("abc"));
    expect(stableHash("abc")).not.toBe(stableHash("abd"));
  });
});
