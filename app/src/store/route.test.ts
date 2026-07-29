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

  it("kolekcija ima podprikaze humidora i kalendara", () => {
    expect(parseHash("#/collection/humidor")).toEqual({
      page: "collection",
      collection: "humidor",
    });
    expect(parseHash("#/collection/calendar")).toEqual({
      page: "collection",
      collection: "calendar",
    });
    // nepoznat podprikaz pada na samu kolekciju
    expect(parseHash("#/collection/nesto")).toEqual({ page: "collection" });
  });

  it("podprikaz se vraca u hash, osnovna kolekcija ostaje cista", () => {
    expect(routeToHash({ page: "collection", collection: "humidor" })).toBe(
      "#/collection/humidor",
    );
    expect(routeToHash({ page: "collection", collection: "collection" })).toBe(
      "#/collection",
    );
    expect(routeToHash({ page: "collection" })).toBe("#/collection");
  });
});
