import { describe, expect, it } from "vitest";
import type { Cigar } from "../types";
import cigarsJson from "../data/cigars.json";
import { cigarDescription, isGeneratedNote, stripGeneratedNote } from "./cigarNote";

const cigars = cigarsJson as unknown as Cigar[];

const byId = (id: string): Cigar => {
  const hit = cigars.find((c) => c.id === id);
  if (!hit) throw new Error(`missing ${id}`);
  return hit;
};

describe("generirane bilješke nisu opis", () => {
  it("prepoznaje sažetak atributa iz pipelinea", () => {
    expect(
      isGeneratedNote(
        "Nikaragva, Habano pokrov — jače snage, punijeg tijela. Okusi: cedrovina, začini, koža.",
        "hr",
      ),
    ).toBe(true);
    expect(
      isGeneratedNote(
        "Habano wrapper (Nicaragua); fuller and expressive. Notes of cedar, spice, leather.",
        "en",
      ),
    ).toBe(true);
    expect(
      isGeneratedNote(
        "Dominican Republic, Ecuador wrapper — medium in strength, fuller-bodied. Notes: cocoa, coffee.",
        "en",
      ),
    ).toBe(true);
  });

  it("pravi urednički opis prolazi netaknut", () => {
    const real =
      "Black Gold je najtamnija redovna 1502 — bogata, čokoladno-zemljana, uz jaču kavu i dulji finiš.";
    expect(isGeneratedNote(real, "hr")).toBe(false);
    expect(stripGeneratedNote(real, "hr")).toBe(real);
  });

  it("zadržava uredničku rečenicu zalijepljenu iza generiranog uvoda", () => {
    expect(
      stripGeneratedNote(
        "Corojo wrapper (Honduras); powerful, for seasoned smokers. Notes of pepper, spice, leather. Gatekeeper robusto; pepper-forward.",
        "en",
      ),
    ).toBe("Gatekeeper robusto; pepper-forward.");
  });

  it("cigarDescription vraća null kad pravog opisa nema", () => {
    const generatedOnly = cigars.find(
      (c) => isGeneratedNote(c.notes.hr, "hr") && isGeneratedNote(c.notes.en, "en"),
    )!;
    expect(cigarDescription(generatedOnly, "hr")).toBeNull();
  });

  it("ne posuđuje drugi jezik kad domaći nema opis", () => {
    expect(
      cigarDescription(
        {
          notes: {
            hr: "Honduras, Corojo pokrov — pune snage, punog tijela. Okusi: papar.",
            en: "Corojo wrapper (Honduras); powerful. Notes of pepper. Gatekeeper robusto; pepper-forward.",
          },
        },
        "hr",
      ),
    ).toBeNull();
  });
});

describe("kurirani opisi", () => {
  const CURATED = [
    "cig-cao-bones",
    "cig-arturo-fuente-opus-x",
    "cig-partagas-lusitanias",
    "cig-romeo-y-julieta-churchills",
    "cig-davidoff-yamasa",
    "cig-la-aroma-de-cuba-mi-amor",
    "cig-joya-de-nicaragua-clasico-medio-siglo",
    "cig-maestranza-baron",
    "cig-la-instructora-perfection",
    "cig-cumpay-robusto",
  ];

  it("linije koje se kupuju u HR imaju pravi dvojezični opis", () => {
    for (const id of CURATED) {
      const cigar = byId(id);
      expect(isGeneratedNote(cigar.notes.hr, "hr"), id).toBe(false);
      expect(isGeneratedNote(cigar.notes.en, "en"), id).toBe(false);
      expect(cigar.notes.hr.length, id).toBeGreaterThanOrEqual(60);
      expect(cigar.notes.en.length, id).toBeGreaterThanOrEqual(60);
    }
  });

  it("većina HR dostupnih cigara ima opis na HR", () => {
    const available = cigars.filter((c) => c.availabilityHR.length > 0);
    // Samo notes.hr (bez EN posudbe). Omjer ~0.68 u korpusu; prag 0.65 drži
    // prostor za tjedni reconcile bez kuriranih HR opisa.
    const described = available.filter((c) => cigarDescription(c, "hr") != null);
    expect(available.length).toBeGreaterThan(300);
    expect(described.length / available.length).toBeGreaterThanOrEqual(0.65);
  });
});
