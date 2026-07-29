import { describe, it, expect } from "vitest";
import { scorePairing, pairDrinksForCigar } from "./pairing";
import {
  OCCASION_BAND_MARGIN,
  occasionAffinity,
  occasionKeep,
  occasionReasons,
  rankByOccasion,
} from "./occasion";
import { WEIGHTS } from "./rules";
import type { Cigar, Drink, DrinkCategory } from "../types";
import cigarsData from "../data/cigars.json";
import rumsData from "../data/rums.json";
import { ALL_DRINKS } from "../data";

const cigars = cigarsData as Cigar[];
const rums = rumsData as unknown as Drink[];

const byId = <T extends { id: string }>(arr: T[], id: string): T => {
  const found = arr.find((x) => x.id === id);
  if (!found) throw new Error(`missing ${id}`);
  return found;
};

const CATEGORIES: DrinkCategory[] = [
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
  "digestif",
];

/** Isti izbor kao u PairingPage: po jedno pice po kategoriji. */
function topPerCategory(
  cigar: Cigar,
  occasion: "morning" | "afternoon" | "evening" | undefined,
): Record<string, string | undefined> {
  const ranked = pairDrinksForCigar(
    cigar,
    ALL_DRINKS.filter((d) => d.pairable),
    undefined,
    occasion,
  );
  const out: Record<string, string | undefined> = {};
  for (const cat of CATEGORIES) {
    const list = rankByOccasion(
      ranked.filter((r) => r.item.category === cat),
      cigar,
      occasion,
    );
    out[cat] = list[0]?.item.id;
  }
  return out;
}

describe("occasion soft-only (par > vrijeme)", () => {
  it("occasionKeep ne reže pool", () => {
    const keep = occasionKeep("evening", 1);
    expect(keep({ body: 1, category: "rum" } as Drink)).toBe(true);
    expect(keep({ body: 5, category: "rum" } as Drink)).toBe(true);
  });

  it("ukupni |occasion delta| < bodyPerStep (ne pregazi body-match)", () => {
    const delta = occasionReasons("morning", {
      cigar: { strength: 1, body: 1 },
      drink: { body: 1, category: "rum", style: "agricole", flavorTags: [] },
    }).reduce((s, r) => s + r.score, 0);
    const clash = occasionReasons("morning", {
      cigar: { strength: 1, body: 1 },
      drink: { body: 5, category: "brandy", style: "cognac-xo", flavorTags: [] },
    }).reduce((s, r) => s + r.score, 0);
    expect(Math.abs(delta)).toBeLessThan(WEIGHTS.bodyPerStep);
    expect(Math.abs(clash)).toBeLessThan(WEIGHTS.bodyPerStep);
    expect(WEIGHTS.occasionFit + WEIGHTS.occasionMild).toBeLessThan(
      WEIGHTS.bodyPerStep,
    );
  });

  it("bolji body-match pobjeđuje occasion preferenciju", () => {
    // blaga cigara: lagani rum (dobar par) vs puni rum (loš par) uvečer
    const macanudo = byId(cigars, "cig-macanudo-cafe");
    const light = rums.find((d) => d.pairable && d.body <= 2)!;
    const full = rums.find((d) => d.pairable && d.body >= 4)!;
    const ranked = pairDrinksForCigar(
      macanudo,
      [light, full],
      undefined,
      "evening",
    );
    expect(ranked[0].item.id).toBe(light.id);
    expect(ranked[0].score).toBeGreaterThan(ranked[1].score);
  });

  it("Ashton Cabinet: top rum uvečer i dalje ≥ 70 (ne hard-filter 41)", () => {
    const cigar = byId(cigars, "cig-ashton-cabinet");
    const ranked = pairDrinksForCigar(
      cigar,
      rums.filter((d) => d.pairable),
      undefined,
      "evening",
    ).filter((r) => r.item.category === "rum");
    expect(ranked[0].score).toBeGreaterThanOrEqual(70);
  });

  it("ista baza: jutro favorizira laganije relativno prema večeri", () => {
    const cigar = byId(cigars, "cig-partagas-serie-d");
    const light = rums.find((d) => d.pairable && d.body === 2)!;
    const fuller = rums.find((d) => d.pairable && d.body === 4)!;
    const mL = scorePairing(cigar, light, undefined, undefined, "morning").score;
    const mF = scorePairing(cigar, fuller, undefined, undefined, "morning").score;
    const eL = scorePairing(cigar, light, undefined, undefined, "evening").score;
    const eF = scorePairing(cigar, fuller, undefined, undefined, "evening").score;
    expect(mL - mF).toBeGreaterThan(eL - eF);
  });
});

describe("occasionAffinity", () => {
  const mildCigar = { strength: 2, body: 2 };
  const strongCigar = { strength: 4, body: 4 };

  const drink = (over: Partial<Drink>): Drink =>
    ({
      body: 3,
      category: "rum",
      style: "blend",
      flavorTags: [],
      ...over,
    }) as Drink;

  it("kava je jutro, digestiv je večer", () => {
    const coffee = drink({ category: "coffee", style: "filter-medium", body: 2 });
    const fernet = drink({ category: "digestif", style: "fernet", body: 4 });

    expect(occasionAffinity("morning", { cigar: mildCigar, drink: coffee })).toBeGreaterThan(
      occasionAffinity("evening", { cigar: mildCigar, drink: coffee }),
    );
    expect(occasionAffinity("evening", { cigar: strongCigar, drink: fernet })).toBeGreaterThan(
      occasionAffinity("morning", { cigar: strongCigar, drink: fernet }),
    );
  });

  it("XO konjak i Islay uvečer, agricole i fino ujutro/poslijepodne", () => {
    const xo = drink({ category: "brandy", style: "cognac-xo", body: 4 });
    const islay = drink({ category: "whisky", style: "islay-peated", body: 4 });
    const agricole = drink({ category: "rum", style: "agricole", body: 2 });
    const fino = drink({ category: "wine", style: "sherry-dry", body: 2 });

    for (const d of [xo, islay]) {
      expect(occasionAffinity("evening", { cigar: strongCigar, drink: d })).toBeGreaterThan(
        occasionAffinity("morning", { cigar: strongCigar, drink: d }),
      );
    }
    expect(occasionAffinity("morning", { cigar: mildCigar, drink: agricole })).toBeGreaterThan(
      occasionAffinity("evening", { cigar: mildCigar, drink: agricole }),
    );
    expect(occasionAffinity("afternoon", { cigar: mildCigar, drink: fino })).toBeGreaterThan(
      occasionAffinity("morning", { cigar: mildCigar, drink: fino }),
    );
  });

  it("ostaje u rasponu −2…2", () => {
    for (const occ of ["morning", "afternoon", "evening"] as const) {
      for (const d of ALL_DRINKS.filter((x) => x.pairable).slice(0, 300)) {
        const a = occasionAffinity(occ, { cigar: strongCigar, drink: d });
        expect(a).toBeGreaterThanOrEqual(-2);
        expect(a).toBeLessThanOrEqual(2);
      }
    }
  });
});

describe("rankByOccasion — razdvajanje bez žrtvovanja para", () => {
  const sample = [
    "cig-ashton-cabinet",
    "cig-macanudo-cafe",
    "cig-partagas-serie-d",
    "cig-don-tomas-bundle",
  ];

  it("jutro i večer daju različit top-1 barem u jednoj kategoriji", () => {
    for (const id of sample) {
      const cigar = byId(cigars, id);
      const morning = topPerCategory(cigar, "morning");
      const evening = topPerCategory(cigar, "evening");
      const differs = CATEGORIES.some((c) => morning[c] !== evening[c]);
      expect(differs, id).toBe(true);
    }
  });

  it("jutro i poslijepodne se također razlikuju", () => {
    for (const id of sample) {
      const cigar = byId(cigars, id);
      const morning = topPerCategory(cigar, "morning");
      const afternoon = topPerCategory(cigar, "afternoon");
      const differs = CATEGORIES.some((c) => morning[c] !== afternoon[c]);
      expect(differs, id).toBe(true);
    }
  });

  it("presloženi izbor ostaje unutar pojasa od najboljeg para", () => {
    for (const id of sample) {
      const cigar = byId(cigars, id);
      for (const occ of ["morning", "afternoon", "evening"] as const) {
        const ranked = pairDrinksForCigar(
          cigar,
          ALL_DRINKS.filter((d) => d.pairable),
          undefined,
          occ,
        );
        for (const cat of CATEGORIES) {
          const list = ranked.filter((r) => r.item.category === cat);
          if (list.length === 0) continue;
          const picked = rankByOccasion(list, cigar, occ)[0];
          expect(
            picked.score,
            `${id}/${occ}/${cat}`,
          ).toBeGreaterThanOrEqual(list[0].score - OCCASION_BAND_MARGIN);
        }
      }
    }
  });

  it('bez prilike ("any") rang ostaje netaknut', () => {
    const cigar = byId(cigars, "cig-partagas-serie-d");
    const ranked = pairDrinksForCigar(
      cigar,
      rums.filter((d) => d.pairable),
    );
    expect(rankByOccasion(ranked, cigar, undefined)).toEqual(ranked);
  });
});
