import { describe, expect, it } from "vitest";
import { urlFitsVitola } from "./vitolaLinkMatch";
import { CIGARS, cigarShopLinks, cigarShopLinkPrice } from "../data";
import { applyVitola, uniqueVitolas } from "./cigarVitola";

const CW_GORDO =
  "https://www.cigarworld.de/en/zigarren/nicaragua/aj-fernandez-bellas-artes-maduro-gordo-90015088_53601";

describe("urlFitsVitola", () => {
  it("slug s imenom vitole prolazi", () => {
    expect(
      urlFitsVitola(
        "https://www.cigarworld.de/en/zigarren/nicaragua/aj-fernandez-20th-anniversary-toro-90017069_59577",
        "Toro",
        "AJ Fernandez 20th Anniversary",
      ),
    ).toBe(true);
  });

  it("slug koji imenuje drugu vitolu pada", () => {
    const ctx = "AJ Fernandez Bellas Artes";
    expect(urlFitsVitola(CW_GORDO, "Maduro Robusto", ctx)).toBe(false);
    expect(urlFitsVitola(CW_GORDO, "Hybrid Toro", ctx)).toBe(false);
    expect(urlFitsVitola(CW_GORDO, "Maduro Lancero", ctx)).toBe(false);
  });

  it("slug bez ijedne oznake veličine ne opovrgava ništa", () => {
    expect(
      urlFitsVitola(
        "https://www.neptunecigar.com/cigars/aging-room-quattro-nicaragua-espressivo",
        "Robusto",
        "Aging Room Quattro Nicaragua Espressivo",
      ),
    ).toBe(true);
  });

  it("množina i sitne varijante prolaze, slični oblici ne", () => {
    expect(urlFitsVitola("https://x.hr/proizvod/linija-robustos", "Robusto", "Linija")).toBe(
      true,
    );
    expect(urlFitsVitola("https://x.hr/proizvod/linija-torpedo", "Toro", "Linija")).toBe(false);
  });

  it("ime bez značajnih riječi ne može opovrgnuti link", () => {
    expect(urlFitsVitola("https://x.hr/proizvod/linija-toro", "No. 2", "Linija")).toBe(true);
  });
});

describe("AJ Fernandez — vitola više ne nasljeđuje link druge vitole", () => {
  const bellasArtes = CIGARS.find((c) => c.id === "cig-aj-fernandez-bellas-artes")!;

  it("linija ima EU link na Maduro Gordo (podatak ostaje kakav jest)", () => {
    expect(bellasArtes.regionLinks?.EU?.url).toBe(CW_GORDO);
  });

  it("odabir vitole ne prenosi taj link ni njegovu cijenu", () => {
    for (const v of uniqueVitolas(bellasArtes)) {
      const applied = applyVitola(bellasArtes, v);
      if (v.regionLinks?.EU?.url) continue; // vitola ima svoj scrapani link
      expect(applied.regionLinks?.EU?.url, v.name).not.toBe(CW_GORDO);
    }
  });

  it("CigarWorld gumb postaje pretraga koja nosi ime odabrane vitole", () => {
    const robusto = uniqueVitolas(bellasArtes).find((v) => v.name === "Maduro Robusto")!;
    const applied = applyVitola(bellasArtes, robusto);
    const eu = cigarShopLinks(applied).find((l) => l.shop === "CigarWorld")!;
    expect(eu.url).not.toBe(CW_GORDO);
    expect(eu.exact).toBe(false);
    expect(decodeURIComponent(eu.url)).toContain("Maduro Robusto");
  });

  it("Neptune bira proizvod baš te vitole iz sourceUrls linije", () => {
    const cases: [string, string][] = [
      ["Maduro Robusto", "bellas-artes-maduro-robusto"],
      ["Hybrid Toro", "bellas-artes-toro"],
      ["Maduro Lancero", "bellas-artes-maduro-lancero"],
    ];
    for (const [name, slug] of cases) {
      const v = uniqueVitolas(bellasArtes).find((x) => x.name === name)!;
      const applied = applyVitola(bellasArtes, v);
      const neptune = cigarShopLinks(applied).find((l) => l.shop === "Neptune Cigar")!;
      expect(neptune.url, name).toContain(slug);
    }
  });

  it("Holt's stranica linije ostaje, ali bez cijene odabrane vitole", () => {
    const robusto = uniqueVitolas(bellasArtes).find((v) => v.name === "Maduro Robusto")!;
    const applied = applyVitola(bellasArtes, robusto);
    const holts = cigarShopLinks(applied).find((l) => l.shop === "Holt's")!;
    expect(holts.kind).toBe("line");
    expect(holts.exact).toBe(false);
    expect(cigarShopLinkPrice(applied, holts).price).toBeNull();
  });

  it("dvije različite vitole ne dobiju isti EU/USA link", () => {
    const vitolas = uniqueVitolas(bellasArtes);
    const urls = vitolas.map((v) => {
      const applied = applyVitola(bellasArtes, v);
      return cigarShopLinks(applied)
        .filter((l) => l.region !== "HR")
        .map((l) => l.url)
        .join("|");
    });
    expect(new Set(urls).size).toBe(vitolas.length);
  });
});
