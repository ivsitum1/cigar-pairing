import { describe, expect, it } from "vitest";
import { smokerProfile, smokerStyle, type TriedCigar } from "./smokerProfile";

const cigar = (over: Partial<TriedCigar> = {}): TriedCigar => ({
  itemId: "cig-a",
  strength: 3,
  body: 3,
  country: "Nikaragva",
  wrapper: "Habano",
  flavorTags: ["kakao"],
  shape: "robusto",
  rating: null,
  ...over,
});

describe("smokerStyle", () => {
  it("dvije cigare nisu stil", () => {
    expect(smokerStyle(2, 4.5, 4.5)).toBe("novice");
    expect(smokerStyle(0, null, null)).toBe("novice");
  });

  it("jačina iznad svega", () => {
    expect(smokerStyle(10, 4, 2)).toBe("strong");
  });

  it("blago, puno i uravnoteženo", () => {
    expect(smokerStyle(10, 2, 2)).toBe("mild");
    expect(smokerStyle(10, 3, 4)).toBe("full");
    expect(smokerStyle(10, 3, 3)).toBe("balanced");
  });
});

describe("smokerProfile", () => {
  it("prazan profil ne izmišlja brojke", () => {
    const p = smokerProfile([], 0, []);
    expect(p).toMatchObject({
      tried: 0,
      rated: 0,
      avgRating: null,
      avgStrength: null,
      avgBody: null,
      topShape: null,
      topCountry: null,
      topWrapper: null,
      topDrink: null,
      best: null,
      style: "novice",
    });
    expect(p.topFlavors).toEqual([]);
  });

  it("broji probano, ocijenjeno i prosjek ocjena", () => {
    const p = smokerProfile(
      [
        cigar({ itemId: "cig-a", rating: 8 }),
        cigar({ itemId: "cig-b", rating: 6 }),
        cigar({ itemId: "cig-c" }),
      ],
      4,
      [],
    );
    expect(p.tried).toBe(3);
    expect(p.rated).toBe(2);
    expect(p.avgRating).toBe(7);
    expect(p.triedDrinks).toBe(4);
  });

  it("nalazi najčešći format, zemlju, pokrov i okuse", () => {
    const p = smokerProfile(
      [
        cigar({ shape: "toro", country: "Kuba", wrapper: "Habano", flavorTags: ["kakao", "kava"] }),
        cigar({ shape: "toro", country: "Kuba", wrapper: "Maduro", flavorTags: ["kakao"] }),
        cigar({ shape: "robusto", country: "Nikaragva", wrapper: "Habano", flavorTags: ["cedar"] }),
      ],
      0,
      [],
    );
    expect(p.topShape).toEqual({ value: "toro", count: 2 });
    expect(p.topCountry).toEqual({ value: "Kuba", count: 2 });
    expect(p.topWrapper).toEqual({ value: "Habano", count: 2 });
    expect(p.topFlavors).toEqual([
      { value: "kakao", count: 2 },
      { value: "cedar", count: 1 },
      { value: "kava", count: 1 },
    ]);
  });

  it("linija bez odabranog formata ne ulazi u statistiku oblika", () => {
    const p = smokerProfile(
      [cigar({ shape: null }), cigar({ shape: null }), cigar({ shape: "corona" })],
      0,
      [],
    );
    expect(p.topShape).toEqual({ value: "corona", count: 1 });
  });

  it("dnevnik daje broj večeri i najčešće piće", () => {
    const p = smokerProfile(
      [cigar()],
      0,
      [
        { cigarId: "cig-a", drinkId: "rum-1", rating: 9 },
        { cigarId: "cig-a", drinkId: "rum-1", rating: 8 },
        { cigarId: "cig-b", drinkId: null, rating: null },
      ],
    );
    expect(p.evenings).toBe(3);
    expect(p.topDrink).toEqual({ value: "rum-1", count: 2 });
  });

  it("pamti najbolje ocijenjenu cigaru", () => {
    const p = smokerProfile(
      [
        cigar({ itemId: "cig-a", rating: 7 }),
        cigar({ itemId: "cig-b@toro", rating: 9.5 }),
        cigar({ itemId: "cig-c", rating: 9 }),
      ],
      0,
      [],
    );
    expect(p.best).toEqual({ itemId: "cig-b@toro", rating: 9.5 });
  });

  it("prosjeci jačine i tijela vode stil", () => {
    const p = smokerProfile(
      [
        cigar({ strength: 4, body: 4 }),
        cigar({ strength: 4, body: 5 }),
        cigar({ strength: 5, body: 5 }),
      ],
      0,
      [],
    );
    expect(p.avgStrength).toBeCloseTo(4.33, 2);
    expect(p.avgBody).toBeCloseTo(4.67, 2);
    expect(p.style).toBe("strong");
  });
});
