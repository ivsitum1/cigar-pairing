import { describe, it, expect } from "vitest";
import cigarsData from "./cigars.json";
import aliases from "./cigarIdAliases.json";
import type { Cigar } from "../types";

const CIGARS = cigarsData as Cigar[];

/**
 * Nomenklatura je brend → linija → vitola. Dimenzije su svojstvo vitole, ne
 * dio imena: "1502 XO Torpedo 6 1/2 x 52" je brend 1502, linija XO, vitola
 * Torpedo. Uvoz iz trgovina zna sve to sljepiti u ime linije — ovi testovi
 * paze da se ne vrati.
 */

const RING = [26, 90] as const;
const LEN_IN = [3, 12] as const;
const inRange = (n: number, [lo, hi]: readonly [number, number]) => n >= lo && n <= hi;

/** Ista pravila kao scripts/taxonomy_lib.py:_dim_from_run — čita li se niz brojeva kao mjera. */
function readsAsSize(nums: number[]): boolean {
  if (nums.length === 2) {
    const [a, b] = nums;
    return (
      (inRange(a, LEN_IN) && inRange(b, RING)) || (inRange(a, RING) && inRange(b, LEN_IN))
    );
  }
  if (nums.length === 3) {
    const [a, den, ring] = nums;
    const whole = Math.floor(a / 10);
    const num = a % 10;
    return (
      a >= 10 && a <= 99 && den >= 2 && den <= 16 && num >= 1 && num < den &&
      inRange(whole, LEN_IN) && inRange(ring, RING)
    );
  }
  if (nums.length === 4) {
    const [whole, num, den, ring] = nums;
    return (
      inRange(whole, LEN_IN) && den >= 2 && den <= 16 && num >= 1 && num < den &&
      inRange(ring, RING)
    );
  }
  return false;
}

function endsWithDimensions(line: string): boolean {
  const words = line.split(/\s+/);
  const run: number[] = [];
  for (let i = words.length - 1; i >= 0 && /^\d{1,3}$/.test(words[i]); i--) {
    run.unshift(Number(words[i]));
  }
  if (run.length === words.length) return false; // ime je samo broj ("858")
  for (let take = Math.min(4, run.length); take >= 2; take--) {
    if (readsAsSize(run.slice(run.length - take))) return true;
  }
  return false;
}

const SMALL_WORDS = new Set([
  "a", "an", "and", "at", "by", "for", "from", "in", "of", "on", "or", "the",
  "to", "vs", "with", "d'", "y", "de", "del", "la", "las", "el", "los",
]);

describe("nomenklatura linija", () => {
  it("nijedna linija ne završava dimenzijama", () => {
    const explicitDims = /\d\s*(?:[x×]\s*\d|mm\b|")/i;
    const offenders = CIGARS.filter(
      (c) => endsWithDimensions(c.line) || explicitDims.test(c.line),
    ).map((c) => `${c.id}: ${c.line}`);
    expect(offenders).toEqual([]);
  });

  it("nijedno ime linije nije ostalo u slug-obliku (sve malim slovima)", () => {
    const offenders = CIGARS.filter(
      (c) =>
        c.line === c.line.toLowerCase() &&
        // ime koje počinje brojkom ("250th") nema što velikim slovom
        c.line.split(/\s+/).some((w) => /^[a-z]/.test(w) && !SMALL_WORDS.has(w)),
    ).map((c) => `${c.id}: ${c.line}`);
    expect(offenders).toEqual([]);
  });

  it("1502 XO je jedna linija sa svojim vitolama", () => {
    const xo = CIGARS.filter((c) => c.brand === "1502" && /\bxo\b/i.test(c.line));
    expect(xo.map((c) => c.line)).toEqual(["XO"]);
    const names = xo[0].vitolas.map((v) => v.name);
    expect(names).toEqual(expect.arrayContaining(["Torpedo", "Lancero", "Salomon"]));
    // Torpedo je 6 1/2 x 52 → 165 mm, a ne procjena iz vitole
    expect(xo[0].vitolas.find((v) => v.name === "Torpedo")?.format).toBe("52 x 165mm");
  });

  it("stari id-evi s dimenzijama vode na novu liniju", () => {
    const map = (aliases as { aliases: Record<string, string> }).aliases;
    const live = new Set(CIGARS.map((c) => c.id));
    for (const old of [
      "cig-1502-xo-61-2-52",
      "cig-1502-xo-7-40",
      "cig-1502-special-edition-xo-series",
    ]) {
      expect(map[old], old).toBe("cig-1502-xo");
    }
    // svaki alias mora pokazivati na živi zapis
    const dangling = Object.entries(map)
      .filter(([, to]) => !live.has(to))
      .map(([from, to]) => `${from} → ${to}`);
    expect(dangling).toEqual([]);
  });
});
