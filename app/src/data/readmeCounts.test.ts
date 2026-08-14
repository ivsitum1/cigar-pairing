// README je nabrajao "155 rumova, 273 whiskyja … 2395 cigara" dok ih je
// stvarno bilo 321 / 275 / 2400 — brojke su odlutale kroz desetke regeneracija
// kataloga jer ih ništa nije vezalo uz podatke. Ovaj test ih veže.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { CIGARS, DRINKS } from "./index";

const HERE = dirname(fileURLToPath(import.meta.url));
const README = resolve(HERE, "..", "..", "..", "README.md");

/** "321 rum", "275 whiskyja", "2400 cigara" → broj koji README tvrdi. */
function claimed(text: string, noun: string): number | null {
  const m = new RegExp(`(\\d[\\d.\\s]*)\\s+${noun}`).exec(text);
  return m ? Number(m[1].replace(/[.\s]/g, "")) : null;
}

describe("README brojke prate podatke", () => {
  const text = readFileSync(README, "utf8");

  const cases: [string, number][] = [
    ["rum", DRINKS.rum.length],
    ["whiskyja", DRINKS.whisky.length],
    ["brandy/grappa", DRINKS.brandy.length],
    ["gin", DRINKS.gin.length],
    ["vina", DRINKS.wine.length],
    ["tequila", DRINKS.tequila.length],
    ["kava", DRINKS.coffee.length], // "38 kava" — genitiv množine, kao i ostale
    ["digestiva", DRINKS.digestif.length],
    ["cigara", CIGARS.length],
  ];

  it.each(cases)("README tvrdi točan broj za '%s'", (noun, actual) => {
    expect(
      claimed(text, noun),
      `README ne navodi broj uz '${noun}' — ako si promijenio tekst, uskladi i ovaj test`,
    ).not.toBeNull();
    expect(
      claimed(text, noun),
      `README kaže drugi broj nego podaci za '${noun}'. Osvježi README (stvarno: ${actual}).`,
    ).toBe(actual);
  });
});
