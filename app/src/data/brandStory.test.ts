// Priča o kući i „u čemu su naj" — čuvar sadržaja, ne količine.
//
// Pravilo je da se piše samo ondje gdje je priča stvarna; prazno je dopušteno,
// polovično nije. Ovi testovi love upravo polovično: potpis bez priče, priču
// samo na jednom jeziku, ili rečenicu koja ponavlja blurb umjesto da doda išta.
import { describe, expect, it } from "vitest";
import brandsJson from "./brands.json";
import cigarsData from "./cigars.json";
import type { Cigar } from "../types";

type LocalizedText = { hr: string; en: string };
type Brand = {
  country: string;
  founded: string;
  blurb: LocalizedText;
  signature?: LocalizedText;
  story?: LocalizedText;
};

const brands = brandsJson as unknown as Record<string, Brand>;
const cigars = cigarsData as Cigar[];
const entries = Object.entries(brands);
const withStory = entries.filter(([, b]) => b.story);

describe("priča o kući", () => {
  it("ima ih, i svaka je dvojezična", () => {
    expect(withStory.length).toBeGreaterThanOrEqual(25);
    for (const [name, b] of withStory) {
      expect(b.story!.hr.length, `${name} hr`).toBeGreaterThan(150);
      expect(b.story!.en.length, `${name} en`).toBeGreaterThan(150);
    }
  });

  it("priča i potpis idu zajedno — pola posla ne prolazi", () => {
    for (const [name, b] of entries) {
      if (b.story) expect(b.signature, `${name}: priča bez potpisa`).toBeDefined();
      if (b.signature) expect(b.story, `${name}: potpis bez priče`).toBeDefined();
    }
  });

  it("potpis je jedna rečenica, ne esej", () => {
    for (const [name, b] of entries) {
      if (!b.signature) continue;
      for (const lang of ["hr", "en"] as const) {
        const text = b.signature[lang];
        expect(text.length, `${name} ${lang}`).toBeGreaterThan(30);
        expect(text.length, `${name} ${lang}`).toBeLessThanOrEqual(200);
      }
    }
  });

  it("ne ponavlja blurb", () => {
    for (const [name, b] of withStory) {
      expect(b.story!.hr, name).not.toBe(b.blurb.hr);
      expect(b.signature!.hr, name).not.toBe(b.blurb.hr);
    }
  });

  it("piše se za kuće koje se u Hrvatskoj mogu kupiti", () => {
    const hrBrands = new Set(
      cigars.filter((c) => (c.availabilityHR ?? []).length > 0).map((c) => c.brand),
    );
    // barem dvije trećine ispričanih kuća mora biti nešto što stvarno možeš uzeti
    const local = withStory.filter(([name]) => hrBrands.has(name)).length;
    expect(local / withStory.length).toBeGreaterThan(0.66);
  });

  it("svaka ispričana kuća postoji u katalogu cigara", () => {
    const known = new Set(cigars.map((c) => c.brand));
    for (const [name] of withStory) {
      expect(known.has(name), `${name} nema nijednu cigaru`).toBe(true);
    }
  });
});
