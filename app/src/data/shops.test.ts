import { describe, expect, it } from "vitest";
import type { Cigar } from "../types";
import cigarsJson from "./cigars.json";
import { SHOPS } from "./shops";
import { cigarShopLinks } from "./index";

const cigars = cigarsJson as unknown as Cigar[];
const TOBACCO_PETICA = "Tobacco Petica (Branimir)";

const byId = (id: string): Cigar => {
  const hit = cigars.find((c) => c.id === id);
  if (!hit) throw new Error(`missing ${id}`);
  return hit;
};

describe("Tobacco Petica (Branimir centar)", () => {
  it("registrirana je kao HR trgovina bez web kataloga", () => {
    const shop = SHOPS.find((s) => s.id === "tobacco-petica-branimir");
    expect(shop).toBeDefined();
    expect(shop?.name).toBe(TOBACCO_PETICA);
    expect(shop?.region).toBe("HR");
    expect(shop?.walkIn).toBe(true);
    expect(shop?.productHost).toBeUndefined();
    expect(shop?.note.hr).toMatch(/Havana/);
  });

  it("Oliva Serie G Special G je ondje (Havana cijena, djelomična ponuda)", () => {
    const g = byId("cig-oliva-serie-g");
    expect(g.availabilityHR).toContain(TOBACCO_PETICA);
    expect(g.availabilityHR).toContain("Havana Cigar Shop");
    const special = g.vitolas.find((v) => v.name === "Special G");
    expect(special?.priceEUR).toBe(7.05);
  });

  it("CAO Bones, Don Tomas Bundle i Clásico su ondje dostupni", () => {
    expect(byId("cig-cao-bones").availabilityHR).toContain(TOBACCO_PETICA);
    expect(byId("cig-cao-bones").vitolas.map((v) => v.name)).toContain(
      "Chicken Foot",
    );
    expect(byId("cig-don-tomas-bundle").availabilityHR).toContain(
      TOBACCO_PETICA,
    );
    const bundleByName = Object.fromEntries(
      byId("cig-don-tomas-bundle").vitolas.map((v) => [v.name, v]),
    );
    expect(bundleByName.Rothschild?.priceEUR).toBe(2.8);
    expect(bundleByName.Robusto?.priceEUR).toBe(3.6);
    expect(bundleByName["Petit Corona"]?.priceEUR).toBe(3.6);
    expect(byId("cig-don-tomas-clasico").markets).toContain("HR");
    expect(byId("cig-don-tomas-clasico").availabilityHR).toContain(
      TOBACCO_PETICA,
    );
  });

  it("La Estrella Polar (Robusto, Gigante) je ondje dostupna", () => {
    const polar = byId("cig-la-estrella-polar");
    expect(polar.markets).toContain("HR");
    expect(polar.availabilityHR).toContain(TOBACCO_PETICA);
    const byName = Object.fromEntries(polar.vitolas.map((v) => [v.name, v]));
    expect(byName.Robusto?.priceEUR).toBe(5.2);
    expect(byName.Gigante?.priceEUR).toBe(6.2);
  });

  it("ducan bez kataloga dobiva walk-in link na naslovnicu, ne search", () => {
    for (const id of [
      "cig-cao-bones",
      "cig-don-tomas-bundle",
      "cig-don-tomas-clasico",
      "cig-la-estrella-polar",
      "cig-oliva-serie-g",
    ]) {
      const links = cigarShopLinks(byId(id));
      const petica = links.find((l) => l.shop === TOBACCO_PETICA);
      expect(petica, id).toBeDefined();
      expect(petica!.kind).toBe("walkin");
      expect(petica!.url).toContain("branimir.hr");
      expect(links.every((l) => l.kind !== "search"), id).toBe(true);
    }
  });
});

describe("availabilityHR imena", () => {
  // Ista trgovina znala je stajati pod dva imena ("Havana Shop" na 291 cigari,
  // "Havana Cigar Shop" na 7). Ime iz availabilityHR ide u prikaz i u poklon
  // („Trgovina: …"), pa mora doslovno odgovarati registru iz shops.ts.
  it("svako ime je registrirana HR trgovina", () => {
    const known = new Set(SHOPS.filter((s) => s.region === "HR").map((s) => s.name));
    const seen = new Set<string>();
    for (const c of cigars) for (const name of c.availabilityHR) seen.add(name);
    expect(seen.size).toBeGreaterThan(0);
    expect([...seen].filter((n) => !known.has(n))).toEqual([]);
  });

  it("Havana Cigar Shop je jedini oblik tog imena", () => {
    const raw = JSON.stringify(cigars);
    expect(raw).not.toContain("Havana Shop");
    const havana = cigars.filter((c) => c.availabilityHR.includes("Havana Cigar Shop"));
    expect(havana.length).toBeGreaterThan(250);
  });

  it("nijedna cigara ne navodi istu trgovinu dvaput", () => {
    for (const c of cigars) {
      expect(new Set(c.availabilityHR).size, c.id).toBe(c.availabilityHR.length);
    }
  });
});

describe("Aficionado (Zagreb)", () => {
  it("registriran je kao HR trgovina bez web kataloga", () => {
    const shop = SHOPS.find((s) => s.id === "aficionado-zg");
    expect(shop).toBeDefined();
    expect(shop?.name).toBe("Aficionado");
    expect(shop?.region).toBe("HR");
    expect(shop?.walkIn).toBe(true);
    expect(shop?.productHost).toBeUndefined();
    expect(shop?.home).toBe("https://www.aficionado.hr/");
    // bez kataloga nema smislene pretrage po proizvodu — oba vode na naslovnicu
    expect(shop?.search("cohiba")).toBe(shop?.home);
  });

  it("Aficionado walk-in gumb samo kad je ime u availabilityHR", () => {
    const hr = cigars.filter((c) => c.markets.includes("HR")).slice(0, 80);
    expect(hr.length).toBeGreaterThan(0);
    for (const c of hr) {
      const link = cigarShopLinks(c).find((l) => l.shop === "Aficionado");
      if ((c.availabilityHR ?? []).includes("Aficionado")) {
        expect(link?.kind, c.id).toBe("walkin");
        expect(link?.url).toBe("https://www.aficionado.hr/");
      } else {
        expect(link, c.id).toBeUndefined();
      }
    }
  });
});

describe("EU UK / Švicarska referentne trgovine", () => {
  it("C.Gars Ltd (UK) i La Couronne (CH) su u EU registru", () => {
    const uk = SHOPS.find((s) => s.id === "cgars-uk");
    const ch = SHOPS.find((s) => s.id === "la-couronne-ch");
    expect(uk?.region).toBe("EU");
    expect(uk?.productHost).toBe("cgarsltd.co.uk");
    expect(uk?.home).toContain("cgarsltd.co.uk");
    expect(ch?.region).toBe("EU");
    expect(ch?.productHost).toBe("cigarpassion.ch");
    expect(ch?.home).toContain("cigarpassion.ch");
  });

  it("EU cigara dobiva samo dokazane shop gumbe (bez search fallbacka)", () => {
    const eu = cigars.find((c) => c.markets.includes("EU") && c.regionLinks?.EU?.url);
    expect(eu).toBeDefined();
    const links = cigarShopLinks(eu!).filter((l) => l.region === "EU");
    expect(links.length).toBeGreaterThan(0);
    expect(links.every((l) => l.kind === "product" || l.kind === "line")).toBe(true);
    expect(links.some((l) => l.shop === "CigarWorld" || l.url.includes("cigarworld"))).toBe(
      true,
    );
    // Bez product URL-a na C.Gars / La Couronne — nema gumbi za njih
    const onlyCw = cigars.find(
      (c) =>
        c.regionLinks?.EU?.url?.includes("cigarworld.de") &&
        !JSON.stringify(c).includes("cgarsltd") &&
        !JSON.stringify(c).includes("cigarpassion"),
    );
    if (onlyCw) {
      const shops = cigarShopLinks(onlyCw)
        .filter((l) => l.region === "EU")
        .map((l) => l.shop);
      expect(shops).not.toContain("C.Gars Ltd");
      expect(shops).not.toContain("La Couronne");
    }
  });
});
