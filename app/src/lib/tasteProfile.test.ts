// Tvoja ocjena je jedini izvor koji je cigaru stvarno pušio — mora nadjačati
// katalog svugdje gdje se snaga i tijelo čitaju, i ne smije se dati srušiti
// pokvarenim zapisom u localStorageu.
import { beforeAll, beforeEach, describe, expect, it } from "vitest";

import type { Cigar } from "../types";
import { ALL_DRINKS, CIGARS } from "../data";
import { scorePairing } from "../engine/pairing";
import {
  clearTasteProfile,
  getTasteProfile,
  normalizeTasteProfiles,
  setTasteProfile,
} from "../store/tasteProfile";
import { withTaste, withTasteAll } from "./tasteProfile";

// isti pristup kao store/collection.test.ts — vitest vrti u "node" okruzenju
function installMemoryStorage() {
  const store = new Map<string, string>();
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    value: {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => void store.set(k, String(v)),
      removeItem: (k: string) => void store.delete(k),
      clear: () => store.clear(),
    },
  });
}

const cigar = (over: Partial<Cigar> = {}): Cigar =>
  ({
    id: "cig-test",
    brand: "Test",
    line: "Line",
    vitola: "Robusto",
    format: "50 x 127mm",
    country: "Nikaragva",
    wrapper: "Habano",
    strength: 3,
    body: 3,
    flavorTags: [],
    smokeTimeMin: 45,
    priceEUR: 10,
    availabilityHR: [],
    notes: { hr: "", en: "" },
    markets: ["HR"],
    vitolas: [],
    profileEstimated: true,
    ...over,
  }) as Cigar;

beforeAll(installMemoryStorage);

beforeEach(() => {
  localStorage.clear();
  clearTasteProfile("cig-test");
});

describe("ocjena iz prve ruke", () => {
  it("nadjačava katalogovu procjenu i gasi oznaku 'procijenjeno'", () => {
    const c = cigar({ strength: 3, body: 3 });
    setTasteProfile(c.id, 5, 2);
    const out = withTaste(c);
    expect(out.strength).toBe(5);
    expect(out.body).toBe(2);
    expect(out.profileEstimated).toBe(false);
    expect(out.profileFromUser).toBe(true);
  });

  it("bez ocjene ne dira ništa — ista referenca", () => {
    const c = cigar();
    expect(withTaste(c)).toBe(c);
  });

  it("ključ je linija, pa vrijedi i kad se bilježi vitola", () => {
    setTasteProfile("cig-test@robusto", 4, 4);
    expect(getTasteProfile("cig-test")?.strength).toBe(4);
    expect(getTasteProfile("cig-test@toro")?.strength).toBe(4);
  });

  it("izvan 1–5 se steže, a ne odbacuje", () => {
    setTasteProfile("cig-test", 9, 0);
    expect(getTasteProfile("cig-test")).toMatchObject({ strength: 5, body: 1 });
  });

  it("brisanje vraća katalogovu vrijednost", () => {
    const c = cigar({ strength: 2 });
    setTasteProfile(c.id, 5, 5);
    expect(withTaste(c).strength).toBe(5);
    clearTasteProfile(c.id);
    expect(withTaste(c).strength).toBe(2);
  });
});

describe("pokvaren zapis ne ruši app", () => {
  it("odbacuje sve što nije dva broja", () => {
    const out = normalizeTasteProfiles({
      "cig-a": { strength: 4, body: 3, at: "2026-01-01" },
      "cig-b": { strength: "jako", body: 3 },
      "cig-c": null,
      "cig-d": { strength: NaN, body: 2 },
      "cig-e": "smeće",
    });
    expect(Object.keys(out)).toEqual(["cig-a"]);
  });

  it("ne pada na praznom ni na nizu", () => {
    expect(normalizeTasteProfiles(null)).toEqual({});
    expect(normalizeTasteProfiles("x")).toEqual({});
  });
});

describe("ocjena stvarno mijenja preporuku", () => {
  it("ista cigara ocijenjena punom drukčije se boduje uz lagano piće", () => {
    const light = ALL_DRINKS.find((d) => d.pairable && d.body <= 2)!;
    const c = cigar({ strength: 1, body: 1 });
    const before = scorePairing(c, light).score;
    setTasteProfile(c.id, 5, 5);
    const after = scorePairing(withTaste(c), light).score;
    expect(after).toBeLessThan(before);
  });

  it("popis prolazi kroz istu ruku", () => {
    const real = CIGARS[0];
    setTasteProfile(real.id, 5, 1);
    const [out] = withTasteAll([real]);
    expect(out.strength).toBe(5);
    expect(out.body).toBe(1);
  });
});
