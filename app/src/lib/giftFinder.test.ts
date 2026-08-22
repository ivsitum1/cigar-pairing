import { describe, expect, it } from "vitest";
import { ALL_DRINKS, CIGARS } from "../data";
import { scorePairing } from "../engine/pairing";
import {
  allGiftAnswerCombos,
  bucketForDrink,
  cigarGiftEligible,
  drinkGiftEligible,
  findGifts,
  giftRegion,
  giftShelfApplies,
  isBlankGiftAnswers,
  MIN_GIFT_QUALITY,
  MIN_PAIRING_SCORE,
  neighbourCategories,
  OWNED_STYLES_NONE,
  uncoveredStyleBuckets,
  visibleGiftSteps,
  type GiftAnswers,
  type GiftBudget,
} from "./giftFinder";
import { BUCKETS } from "./shoppingPicks";

const CATALOG = { cigars: CIGARS, drinks: ALL_DRINKS };

const BAND_MAX: Record<GiftBudget, number> = {
  under20: 20,
  "20to40": 40,
  "40to60": 60,
  "60to100": 100,
  over100: Number.POSITIVE_INFINITY,
  unknown: 40,
};

describe("giftFinder", () => {
  it("giftRegion tretira ALL kao HR (blizina)", () => {
    expect(giftRegion("ALL")).toBe("HR");
    expect(giftRegion("HR")).toBe("HR");
    expect(giftRegion("EU")).toBe("EU");
  });

  it("cigara bez HR trgovine nije poklon u blizini", () => {
    const pricedHr = CIGARS.filter((c) => cigarGiftEligible(c, "HR"));
    expect(pricedHr.length).toBeGreaterThan(10);
    const noShop = CIGARS.find((c) => c.availabilityHR.length === 0);
    if (noShop) expect(cigarGiftEligible(noShop, "HR")).toBe(false);
  });

  it("piće bez shopHR nije HR poklon", () => {
    const ok = ALL_DRINKS.filter((d) => drinkGiftEligible(d, "HR"));
    expect(ok.length).toBeGreaterThan(50);
    expect(ok.every((d) => (d.qualityScore ?? 0) >= MIN_GIFT_QUALITY)).toBe(true);
  });

  it("Don Tomas Bundle i pića ispod 7 nisu u gift poolu", () => {
    const bundle = CIGARS.find((c) => c.id === "cig-don-tomas-bundle");
    expect(bundle).toBeTruthy();
    expect(cigarGiftEligible(bundle!, "HR")).toBe(false);
    const weak = ALL_DRINKS.find(
      (d) => d.pairable && d.qualityScore != null && d.qualityScore < MIN_GIFT_QUALITY,
    );
    if (weak) expect(drinkGiftEligible(weak, "HR")).toBe(false);
  });

  it("treće pitanje (navečer) mijenja prijedlog", () => {
    const base = {
      recipient: "regular" as const,
      budget: "20to40" as const,
      drink: "whisky" as const,
      shape: "bottle" as const,
    };
    const mild = findGifts({ ...base, intensity: "mild" }, CATALOG, "HR");
    const bold = findGifts({ ...base, intensity: "bold" }, CATALOG, "HR");
    const mildDrink = mild.find((p) => p.drink)?.drink;
    const boldDrink = bold.find((p) => p.drink)?.drink;
    expect(mildDrink).toBeTruthy();
    expect(boldDrink).toBeTruthy();
    expect(mildDrink!.id).not.toBe(boldDrink!.id);
    expect(mildDrink!.body).toBeLessThanOrEqual(2);
    expect(boldDrink!.body).toBeGreaterThanOrEqual(4);
  });

  it("budžet se nikad ne prekorači — boca, cigara i kombinacija", () => {
    const budgets: GiftBudget[] = ["under20", "20to40", "40to60", "60to100", "over100"];
    const shapes = ["bottle", "cigar", "pairing"] as const;
    for (const budget of budgets) {
      for (const shape of shapes) {
        const picks = findGifts(
          {
            recipient: "regular",
            budget,
            drink: "rum",
            intensity: "medium",
            shape,
          },
          CATALOG,
          "HR",
        );
        for (const pick of picks) {
          expect(pick.price).not.toBeNull();
          expect(pick.price!).toBeLessThanOrEqual(BAND_MAX[budget] + 0.01);
        }
      }
    }
  }, 30_000);

  it("cigara vraća cigaru, boca bocu, kombinacija oboje", () => {
    const cigar = findGifts(
      {
        recipient: "regular",
        budget: "under20",
        drink: "unknown",
        intensity: "medium",
        shape: "cigar",
      },
      CATALOG,
      "HR",
    );
    expect(cigar.some((p) => p.kind === "cigar" && p.cigar)).toBe(true);

    const bottle = findGifts(
      {
        recipient: "regular",
        budget: "20to40",
        drink: "rum",
        intensity: "medium",
        shape: "bottle",
      },
      CATALOG,
      "HR",
    );
    expect(bottle.some((p) => p.kind === "drink" && p.drink)).toBe(true);

    const pair = findGifts(
      {
        recipient: "regular",
        budget: "40to60",
        drink: "rum",
        intensity: "medium",
        shape: "pairing",
      },
      CATALOG,
      "HR",
    );
    const combo = pair.find((p) => p.kind === "pairing");
    if (combo) {
      expect(combo.cigar).toBeTruthy();
      expect(combo.drink).toBeTruthy();
      expect(combo.price!).toBeLessThanOrEqual(60.01);
    }
  });

  it("drinks-only ne predlaže cigare i ne ponavlja istu bocu", () => {
    const picks = findGifts(
      {
        recipient: "drinks-only",
        budget: "20to40",
        drink: "whisky",
        intensity: "medium",
        shape: "pairing",
      },
      CATALOG,
      "HR",
    );
    for (const p of picks) {
      expect(p.cigar).toBeUndefined();
      expect(p.cigars).toBeUndefined();
      expect(p.kind).toBe("drink");
    }
    if (picks.length === 2) expect(picks[0].id).not.toBe(picks[1].id);
  });

  // Jedan prolaz kroz svih 1600 kombinacija odgovora — sve što mora vrijediti
  // za svaki mogući upitnik provjerava se ovdje, da se katalog ne pretražuje
  // dvaput (prolaz traje oko minute). Prolaz je async i svakih stotinjak
  // kombinacija pušta event loop: inače vitest worker ne stigne javiti napredak
  // i cijeli run padne na "Timeout calling onTaskUpdate".
  it(
    "svaka kombinacija odgovora daje prijedlog u budžetu i iznad praga slaganja",
    async () => {
      const empty: string[] = [];
      const weak: string[] = [];
      let since = 0;
      for (const answers of allGiftAnswerCombos()) {
        if (++since >= 40) {
          since = 0;
          await new Promise((r) => setTimeout(r, 0));
        }
        const picks = findGifts(answers, CATALOG, "HR");
        if (picks.length === 0) empty.push(JSON.stringify(answers));
        for (const p of picks) {
          if (p.price != null) expect(p.price).toBeGreaterThan(0);
          const max = BAND_MAX[answers.budget];
          if (p.price != null && !p.fellBackBudget) {
            expect(p.price).toBeLessThanOrEqual(max + 0.01);
          }
          if (p.kind !== "pairing") continue;
          expect(p.cigar).toBeTruthy();
          expect(p.drink).toBeTruthy();
          // matchScore je isti broj koji korisnik vidi na kartici
          const real = scorePairing(p.cigar!, p.drink!).score;
          expect(p.matchScore).toBe(real);
          if (real < MIN_PAIRING_SCORE) weak.push(`${real}% ${JSON.stringify(answers)}`);
        }
      }
      expect(empty).toEqual([]);
      expect(weak).toEqual([]);
    },
    600_000,
  );

  it("radije cigara i boca zasebno nego slaba kombinacija", () => {
    // Do 20 € u HR poolu ne postoji nijedan par whisky + cigara iznad praga.
    const picks = findGifts(
      {
        recipient: "regular",
        budget: "under20",
        drink: "whisky",
        intensity: "medium",
        shape: "pairing",
      },
      CATALOG,
      "HR",
    );
    expect(picks.length).toBeGreaterThan(0);
    expect(picks.every((p) => p.kind !== "pairing")).toBe(true);
    expect(picks.every((p) => p.droppedPairing)).toBe(true);
  }, 20_000);

  // ——— 0 pogodaka → susjedna kategorija ———

  it("susjedstvo kategorija je definirano i ne vrti se u prazno", () => {
    for (const cat of ["whisky", "rum", "brandy", "wine"] as const) {
      const near = neighbourCategories(cat);
      expect(near.length).toBeGreaterThan(0);
      expect(near).not.toContain(cat);
      expect(new Set(near).size).toBe(near.length);
    }
    expect(neighbourCategories("whisky")[0]).toBe("brandy");
  });

  it("kad u traženoj kategoriji nema pogotka, ide NAJBLIŽA koja ima — s oznakom", () => {
    // Prazne ćelije u HR poklon-poolu i prvi susjed koji u njima ima bocu.
    const cases = [
      { asked: "wine", intensity: "medium", budget: "40to60", expect: "brandy" },
      // whisky do 20 €: brandy i rum su također prazni, pa se ide na treći susjed
      { asked: "whisky", intensity: "medium", budget: "under20", expect: "wine" },
    ] as const;

    for (const c of cases) {
      const picks = findGifts(
        {
          recipient: "drinks-only",
          budget: c.budget,
          drink: c.asked,
          intensity: c.intensity,
          shape: "bottle",
        },
        CATALOG,
        "HR",
      );
      expect(picks.length).toBeGreaterThan(0);
      for (const p of picks) {
        expect(p.drink).toBeTruthy();
        expect(p.drink!.category).toBe(c.expect);
        expect(p.swappedFromCategory).toBe(c.asked);
        expect(neighbourCategories(c.asked)).toContain(p.drink!.category);
        // budžet i dalje vrijedi — mijenja se kategorija, ne cijena
        if (!p.fellBackBudget) expect(p.price!).toBeLessThanOrEqual(BAND_MAX[c.budget] + 0.01);
      }
    }
  });

  it("kategorija se ne mijenja kad u traženoj ima pogodaka", () => {
    const picks = findGifts(
      {
        recipient: "regular",
        budget: "40to60",
        drink: "rum",
        intensity: "medium",
        shape: "pairing",
      },
      CATALOG,
      "HR",
    );
    const withDrink = picks.filter((p) => p.drink);
    expect(withDrink.length).toBeGreaterThan(0);
    for (const p of withDrink) {
      expect(p.drink!.category).toBe("rum");
      expect(p.swappedFromCategory).toBeUndefined();
    }
  });

  // ——— svih pet „ne znam” ———

  it("isBlankGiftAnswers prepoznaje samo potpuno prazan upitnik", () => {
    const blank: GiftAnswers = {
      recipient: "unknown",
      budget: "unknown",
      drink: "unknown",
      intensity: "unknown",
      shape: "unknown",
    };
    expect(isBlankGiftAnswers(blank)).toBe(true);
    expect(isBlankGiftAnswers({ ...blank, budget: "20to40" })).toBe(false);
  });

  it("svih pet „ne znam” daje siguran, raznolik i objašnjen izbor", () => {
    const blank: GiftAnswers = {
      recipient: "unknown",
      budget: "unknown",
      drink: "unknown",
      intensity: "unknown",
      shape: "unknown",
    };
    const picks = findGifts(blank, CATALOG, "HR");

    expect(picks.length).toBe(3);
    // svaki prijedlog je označen kao siguran profil (UI to objašnjava)
    expect(picks.every((p) => p.safeDefault)).toBe(true);
    // tri različita scenarija, ne tri varijante istoga
    expect(new Set(picks.map((p) => p.kind)).size).toBe(3);
    // boca ide ispred cigare — ne znamo ni puši li osoba
    expect(picks.map((p) => p.kind)).toEqual(["pairing", "drink", "cigar"]);

    for (const p of picks) {
      // srednji budžet, nikad preko 40 €
      expect(p.price).not.toBeNull();
      expect(p.price!).toBeLessThanOrEqual(40.01);
      // pristupačna cigara: nikad iznad snage 3
      if (p.cigar) expect(p.cigar.strength).toBeLessThanOrEqual(3);
      // bez egzotike u čaši kad ne znamo što osoba pije
      if (p.drink) expect(["whisky", "rum", "brandy", "wine"]).toContain(p.drink.category);
      // kombinacija i dalje mora proći prag
      if (p.kind === "pairing") expect(p.matchScore!).toBeGreaterThanOrEqual(MIN_PAIRING_SCORE);
    }
    // dvije različite kategorije pića u tri prijedloga
    const cats = picks.filter((p) => p.drink).map((p) => p.drink!.category);
    expect(new Set(cats).size).toBe(cats.length);
  });

  it("„ne znam” samo na jedno pitanje ne pokreće siguran profil", () => {
    const picks = findGifts(
      {
        recipient: "regular",
        budget: "60to100",
        drink: "unknown",
        intensity: "bold",
        shape: "cigar",
      },
      CATALOG,
      "HR",
    );
    expect(picks.length).toBeGreaterThan(0);
    expect(picks.some((p) => p.safeDefault)).toBe(false);
    const cigar = picks.find((p) => p.kind === "cigar");
    expect(cigar?.cigar?.strength).toBeGreaterThanOrEqual(4);
  });

  it("proturječni odgovori (početnik + jače stvari) daju najjače što je sigurno", () => {
    const picks = findGifts(
      {
        recipient: "beginner",
        budget: "under20",
        drink: "whisky",
        intensity: "bold",
        shape: "cigar",
      },
      CATALOG,
      "HR",
    );
    expect(picks.length).toBeGreaterThan(0);
    const cigar = picks.find((p) => p.cigar)?.cigar;
    expect(cigar).toBeTruthy();
    expect(cigar!.strength).toBe(3);
  });
});

describe("poklon — polica, segment, 100 €+", () => {
  it("visibleGiftSteps dodaje policu samo kad znamo piće i oblik nije cigara", () => {
    const base: GiftAnswers = {
      recipient: "regular",
      budget: "40to60",
      drink: "whisky",
      intensity: "medium",
      shape: "bottle",
    };
    expect(giftShelfApplies(base)).toBe(true);
    expect(visibleGiftSteps(base)).toEqual([
      "recipient",
      "budget",
      "intensity",
      "drink",
      "shape",
      "ownedStyles",
      "drinkPick",
    ]);
    expect(visibleGiftSteps({ ...base, shape: "cigar" })).toHaveLength(5);
    expect(visibleGiftSteps({ ...base, drink: "unknown" })).toHaveLength(5);
  });

  it("ne znam preskače prvi bucket; ništa od toga otvara sve", () => {
    const whisky = BUCKETS.whisky!;
    expect(uncoveredStyleBuckets("whisky", []).map((b) => b.id)).toEqual(
      whisky.slice(1).map((b) => b.id),
    );
    expect(uncoveredStyleBuckets("whisky", [OWNED_STYLES_NONE])).toHaveLength(whisky.length);
    expect(uncoveredStyleBuckets("whisky", ["scotch"]).map((b) => b.id)).not.toContain("scotch");
  });

  it("rupa uz scotch na polici ne predlaže scotch", () => {
    const picks = findGifts(
      {
        recipient: "drinks-only",
        budget: "40to60",
        drink: "whisky",
        intensity: "medium",
        shape: "bottle",
        ownedStyles: ["scotch"],
        drinkPick: "gap",
      },
      CATALOG,
      "HR",
    );
    const bottles = picks.filter((p) => p.drink);
    expect(bottles.length).toBeGreaterThan(0);
    for (const p of bottles) {
      const bucket = bucketForDrink(p.drink!);
      expect(bucket?.id).not.toBe("scotch");
      expect(p.why.hr).toMatch(/polici/);
    }
  });

  it("vrh i omjer u istom pojasu daju različite boce kad katalog to dopušta", () => {
    const attempts = [
      { budget: "20to40" as const, drink: "whisky" as const },
      { budget: "40to60" as const, drink: "whisky" as const },
      { budget: "60to100" as const, drink: "whisky" as const },
      { budget: "40to60" as const, drink: "rum" as const },
      { budget: "20to40" as const, drink: "rum" as const },
      { budget: "40to60" as const, drink: "brandy" as const },
    ];
    const split = attempts.some((c) => {
      const base = {
        recipient: "drinks-only" as const,
        intensity: "medium" as const,
        shape: "bottle" as const,
        ...c,
      };
      const top = findGifts({ ...base, drinkPick: "top" }, CATALOG, "HR").find((p) => p.drink);
      const value = findGifts({ ...base, drinkPick: "value" }, CATALOG, "HR").find((p) => p.drink);
      return Boolean(top?.drink && value?.drink && top.drink.id !== value.drink.id);
    });
    expect(split).toBe(true);
  });

  it("kad su svi stilovi na polici, rupa pada na vrh uz noGapLeft", () => {
    const allWhisky = (BUCKETS.whisky ?? []).map((b) => b.id);
    const picks = findGifts(
      {
        recipient: "drinks-only",
        budget: "40to60",
        drink: "whisky",
        intensity: "medium",
        shape: "bottle",
        ownedStyles: allWhisky,
        drinkPick: "gap",
      },
      CATALOG,
      "HR",
    );
    expect(picks.length).toBeGreaterThan(0);
    expect(picks.some((p) => p.noGapLeft)).toBe(true);
    const top = findGifts(
      {
        recipient: "drinks-only",
        budget: "40to60",
        drink: "whisky",
        intensity: "medium",
        shape: "bottle",
        drinkPick: "top",
      },
      CATALOG,
      "HR",
    ).find((p) => p.drink);
    const gap = picks.find((p) => p.drink);
    expect(gap?.drink?.id).toBe(top?.drink?.id);
  });

  it("over100 ne ide ispod 100 € osim uz fellBackBudget", () => {
    const picks = findGifts(
      {
        recipient: "drinks-only",
        budget: "over100",
        drink: "whisky",
        intensity: "bold",
        shape: "bottle",
      },
      CATALOG,
      "HR",
    );
    expect(picks.length).toBeGreaterThan(0);
    for (const p of picks) {
      expect(p.price).not.toBeNull();
      if (!p.fellBackBudget) expect(p.price!).toBeGreaterThanOrEqual(99.99);
      else expect(p.price!).toBeLessThanOrEqual(100.01);
    }
  });
});
