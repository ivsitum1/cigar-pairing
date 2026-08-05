import { describe, it, expect } from "vitest";
import type { PairingResult } from "../types";
import {
  brandDiverse,
  dayKey,
  softBand,
  softBandWindow,
  stableBestRotate,
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

  it("stableTop pins cycle 0 to the head of the pool", () => {
    const ranked = [
      r("a", "A", 90),
      r("b", "B", 90),
      r("c", "C", 90),
      r("d", "D", 90),
      r("e", "E", 90),
      r("f", "F", 90),
    ];
    const w0 = softBandWindow(ranked, {
      anchorId: "drink-stable",
      dayKey: "2026-07-26",
      cycle: 0,
      stableTop: true,
      keyOf: (i: Item) => i.brand,
    });
    expect(w0.window.map((x) => x.item.id)).toEqual(["a", "b", "c"]);
    const w1 = softBandWindow(ranked, {
      anchorId: "drink-stable",
      dayKey: "2026-07-26",
      cycle: 1,
      stableTop: true,
      keyOf: (i: Item) => i.brand,
    });
    expect(w1.window.map((x) => x.item.id)).toEqual(["d", "e", "f"]);
  });

  it("dayKey uses UTC YYYY-MM-DD", () => {
    expect(dayKey(new Date("2026-07-26T23:30:00.000Z"))).toBe("2026-07-26");
  });

  it("stableHash is deterministic", () => {
    expect(stableHash("abc")).toBe(stableHash("abc"));
    expect(stableHash("abc")).not.toBe(stableHash("abd"));
  });
});

describe("stableBestRotate", () => {
  const keyOf = (i: Item) => i.brand;

  it("cycle 0 is always absolute #1", () => {
    const ranked = [
      r("best", "A", 92),
      r("b", "B", 91),
      r("c", "C", 90),
      r("d", "D", 70),
    ];
    const a = stableBestRotate(ranked, 0, { keyOf });
    const b = stableBestRotate(ranked, 0, { keyOf });
    expect(a.pick?.item.id).toBe("best");
    expect(b.pick?.item.id).toBe("best");
    expect(a.total).toBe(3); // soft band 92–87 keeps A,B,C; D out
  });

  it("prvi krug uzima po jedno iz svakog kljuca, pa ide u dubinu", () => {
    const ranked = [
      r("a1", "Demerara", 90),
      r("a2", "Demerara", 89), // isti kljuc — dolazi na red u drugom krugu
      r("b1", "Cuba", 88),
      r("c1", "Agricole", 87),
      r("d1", "Spiced", 70), // izvan pojasa
    ];
    const at = (cycle: number) => stableBestRotate(ranked, cycle, { keyOf });
    expect(at(0).pick?.item.id).toBe("a1");
    expect(at(1).pick?.item.id).toBe("b1");
    expect(at(2).pick?.item.id).toBe("c1");
    expect(at(3).pick?.item.id).toBe("a2");
    expect(at(4).pick?.item.id).toBe("a1"); // krug se zatvara
    expect(at(0).pool.map((x) => x.item.id)).toEqual(["a1", "b1", "c1", "a2"]);
  });

  it("pojas rezu boce ispod margine kad ih ima dovoljno", () => {
    const ranked = [
      r("a1", "A", 90),
      r("b1", "B", 88),
      r("c1", "C", 87),
      r("d1", "D", 60),
    ];
    expect(stableBestRotate(ranked, 0, { keyOf }).pool.map((x) => x.item.id)).toEqual([
      "a1",
      "b1",
      "c1",
    ]);
  });

  it("usamljen vrh se dopuni ispod margine — gumb uvijek ima ponudu", () => {
    const ranked = [r("a1", "A", 90), r("b1", "B", 70), r("c1", "C", 65), r("d", "D", 60)];
    const out = stableBestRotate(ranked, 0, { keyOf });
    expect(out.pool.map((x) => x.item.id)).toEqual(["a1", "b1", "c1"]);
    expect(stableBestRotate(ranked, 1, { keyOf }).pick?.item.id).toBe("b1");
  });

  it("tieSeed rotira medu bodovno izjednacenima na vrhu", () => {
    // isti profil, isti bodovi — engine ih doista ne razlikuje
    const ranked = [
      r("xo1", "XO", 76),
      r("xo2", "XO", 76),
      r("xo3", "XO", 76),
      r("vsop", "VSOP", 74),
    ];
    const picks = new Set(
      ["cig-1|2026-08-05", "cig-2|2026-08-05", "cig-3|2026-08-05"].map(
        (seed) => stableBestRotate(ranked, 0, { keyOf, tieSeed: seed }).pick?.item.id,
      ),
    );
    expect(picks.size).toBeGreaterThan(1);
    // isto sjeme → isti izbor (stabilno kroz re-render i kroz dan)
    const twice = ["a", "a"].map(
      () =>
        stableBestRotate(ranked, 0, { keyOf, tieSeed: "cig-1|2026-08-05" }).pick?.item
          .id,
    );
    expect(twice[0]).toBe(twice[1]);
    // bez sjemena ostaje stari, potpuno stabilan #1
    expect(stableBestRotate(ranked, 0, { keyOf }).pick?.item.id).toBe("xo1");
  });

  it("tieSeed ne dira vrh kad izjednacenih nema", () => {
    const ranked = [r("a", "A", 90), r("b", "B", 88)];
    expect(
      stableBestRotate(ranked, 0, { keyOf, tieSeed: "bilo sto" }).pick?.item.id,
    ).toBe("a");
  });

  it("empty ranked yields empty pick", () => {
    const out = stableBestRotate([], 0, { keyOf });
    expect(out.pick).toBeUndefined();
    expect(out.total).toBe(0);
  });
});
