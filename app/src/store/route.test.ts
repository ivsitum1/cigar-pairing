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
});
