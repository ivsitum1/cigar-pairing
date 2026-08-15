// Okusne oznake moraju biti oznake koje app poznaje.
//
// Oznake sada dolaze i iz CigarWorldova aroma-radara (merge-cigarworld-aroma.py),
// koji imena dimenzija prevodi u katalogov rjecnik. Pogresan prijevod ne bi pao
// nigdje drugdje: pairing bi takvu oznaku samo presao, a kartica bi ispisala
// sirovi kljuc umjesto imena. Zato se ovdje trazi da svaka oznaka ima i ime i
// mjesto u pravilima.
import { describe, expect, it } from "vitest";
import cigarsData from "./cigars.json";
import type { Cigar } from "../types";
import { COMPLEMENTS, TAG_LABELS, normalizeTag } from "../engine/rules";

const cigars = cigarsData as Cigar[];
const used = [...new Set(cigars.flatMap((c) => c.flavorTags ?? []))].sort();

describe("rječnik okusnih oznaka", () => {
  it("svaka oznaka ima ime na oba jezika", () => {
    for (const tag of used) {
      const entry = TAG_LABELS[normalizeTag(tag)];
      expect(entry, `${tag} nema ime — kartica bi ispisala sirovi ključ`).toBeDefined();
      expect(entry.hr.length, `${tag} hr`).toBeGreaterThan(0);
      expect(entry.en.length, `${tag} en`).toBeGreaterThan(0);
    }
  });

  it("svaka oznaka sudjeluje u pairingu", () => {
    // ili je kljuc komplementa, ili se svodi na jedan (TAG_ALIASES)
    for (const tag of used) {
      const canonical = normalizeTag(tag);
      const known = canonical in COMPLEMENTS || Object.values(COMPLEMENTS).some((v) => v.includes(canonical));
      expect(known, `${tag} ne postoji ni u jednom pravilu`).toBe(true);
    }
  });

  it("nijedan zapis ne ponavlja istu oznaku", () => {
    // Spajanja rade uniju iz vise izvora — ponavljanje bi znacilo da je jedno
    // od njih zaobislo dedup i da bi ista nota dvaput vagala u pairingu.
    for (const c of cigars) {
      const tags = c.flavorTags ?? [];
      expect(new Set(tags).size, `${c.id} ponavlja oznaku`).toBe(tags.length);
    }
  });
});
