import { describe, expect, it } from "vitest";
import { parseHash, routeToHash } from "./route";

describe("hash route helpers", () => {
  it("round-trips the HR guide club subroute", () => {
    expect(parseHash("#/club/hr-guide")).toEqual({ page: "club", club: "hr-guide" });
    expect(routeToHash({ page: "club", club: "hr-guide" })).toBe("#/club/hr-guide");
  });

  it("round-trips the evening archetypes club subroute", () => {
    expect(parseHash("#/club/archetypes")).toEqual({ page: "club", club: "archetypes" });
    expect(routeToHash({ page: "club", club: "archetypes" })).toBe("#/club/archetypes");
  });

  it("round-trips the dictionary club subroute", () => {
    expect(parseHash("#/club/dictionary")).toEqual({ page: "club", club: "dictionary" });
    expect(routeToHash({ page: "club", club: "dictionary" })).toBe("#/club/dictionary");
  });

  it("round-trips catalog brand / line / vitola deep links", () => {
    expect(parseHash("#/catalog/brand/la-galera")).toEqual({
      page: "catalog",
      catalog: { level: "brand", brandSlug: "la-galera" },
    });
    expect(
      routeToHash({
        page: "catalog",
        catalog: { level: "brand", brandSlug: "la-galera" },
      }),
    ).toBe("#/catalog/brand/la-galera");

    expect(parseHash("#/catalog/line/cig-la-galera-habano")).toEqual({
      page: "catalog",
      catalog: { level: "line", cigarId: "cig-la-galera-habano" },
    });
    expect(
      routeToHash({
        page: "catalog",
        catalog: { level: "line", cigarId: "cig-la-galera-habano" },
      }),
    ).toBe("#/catalog/line/cig-la-galera-habano");

    expect(parseHash("#/catalog/vitola/cig-la-galera-habano/chaveta")).toEqual({
      page: "catalog",
      catalog: {
        level: "vitola",
        cigarId: "cig-la-galera-habano",
        vitolaSlug: "chaveta",
      },
    });
    expect(
      routeToHash({
        page: "catalog",
        catalog: {
          level: "vitola",
          cigarId: "cig-la-galera-habano",
          vitolaSlug: "chaveta",
        },
      }),
    ).toBe("#/catalog/vitola/cig-la-galera-habano/chaveta");
  });

  // Marka pića je zasebna razina: prostori imena marki cigara i pića se ne
  // dijele, pa `#/catalog/brand/nikka` i `#/catalog/drink-brand/nikka` moraju
  // ostati dvije različite adrese.
  it("round-trips catalog drink-brand deep link", () => {
    expect(parseHash("#/catalog/drink-brand/foursquare")).toEqual({
      page: "catalog",
      catalog: { level: "drinkBrand", brandSlug: "foursquare" },
    });
    expect(
      routeToHash({
        page: "catalog",
        catalog: { level: "drinkBrand", brandSlug: "foursquare" },
      }),
    ).toBe("#/catalog/drink-brand/foursquare");

    expect(parseHash("#/catalog/brand/nikka")).not.toEqual(
      parseHash("#/catalog/drink-brand/nikka"),
    );
  });

  it("kolekcija ima podprikaze humidora, shortlista i kalendara", () => {
    expect(parseHash("#/collection/humidor")).toEqual({
      page: "collection",
      collection: "humidor",
    });
    expect(parseHash("#/collection/collection")).toEqual({
      page: "collection",
      collection: "collection",
    });
    expect(parseHash("#/collection/calendar")).toEqual({
      page: "collection",
      collection: "calendar",
    });
    // prazan podput = humidor (prvi tab)
    expect(parseHash("#/collection")).toEqual({
      page: "collection",
      collection: "humidor",
    });
    // nepoznat podprikaz pada na humidor
    expect(parseHash("#/collection/nesto")).toEqual({
      page: "collection",
      collection: "humidor",
    });
  });

  it("podprikaz se uvijek vraca u hash", () => {
    expect(routeToHash({ page: "collection", collection: "humidor" })).toBe(
      "#/collection/humidor",
    );
    expect(routeToHash({ page: "collection", collection: "collection" })).toBe(
      "#/collection/collection",
    );
    expect(routeToHash({ page: "collection" })).toBe("#/collection/humidor");
  });

  // Neispravan postotni kod je rusio boot u bijeli ekran: parseHash se zove
  // na module scopeu, pa je URIError isao neuhvacen kroz cijelu aplikaciju.
  it("neispravan postotni kod ne baca (ostaje sirov segment)", () => {
    expect(() => parseHash("#/catalog/line/%")).not.toThrow();
    expect(() => parseHash("#/pairing/cigar/%E0%A4%A")).not.toThrow();
    expect(() => parseHash("#/catalog/vitola/ok/%ZZ")).not.toThrow();

    expect(parseHash("#/catalog/line/%")).toEqual({
      page: "catalog",
      catalog: { level: "line", cigarId: "%" },
    });
  });

  it("ispravan postotni kod se i dalje dekodira", () => {
    expect(parseHash("#/catalog/line/cig-a%20b")).toEqual({
      page: "catalog",
      catalog: { level: "line", cigarId: "cig-a b" },
    });
  });

  it("round-trips shopping gift subroute", () => {
    expect(parseHash("#/shopping/gift")).toEqual({ page: "shopping", shopping: "gift" });
    expect(routeToHash({ page: "shopping", shopping: "gift" })).toBe("#/shopping/gift");
    expect(parseHash("#/shopping")).toEqual({ page: "shopping" });
    expect(routeToHash({ page: "shopping" })).toBe("#/shopping");
  });
});
