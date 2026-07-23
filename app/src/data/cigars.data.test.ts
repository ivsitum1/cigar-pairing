import { describe, it, expect } from "vitest";
import cigarsData from "./cigars.json";
import brandsData from "./brands.json";
import { CIGARS, cigarLinkForMarket, cigarPriceForMarket, cigarShopLinks, cigarShopLinkPrice, ALL_BRANDS, BRAND_CATALOG } from "./index";
import type { Cigar } from "../types";

describe("cigars.json integrity", () => {
  it("nema dupliciranih id-eva u izvornom JSON-u", () => {
    const ids = (cigarsData as Cigar[]).map((c) => c.id);
    const unique = new Set(ids);
    expect(unique.size).toBe(ids.length);
  });

  it("CIGARS nakon dedupe ima jedinstvene id-eve", () => {
    const ids = CIGARS.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("Oliva Serie O — ima više vitola i traži odabir", () => {
    const serieO = CIGARS.find((c) => c.id === "cig-oliva-serie-o");
    expect(serieO).toBeDefined();
    expect(serieO!.line).toBe("Serie O");
    expect(serieO!.vitola.toLowerCase()).not.toContain("tubos");
    const names = (serieO!.vitolas ?? []).map((v) => v.name);
    expect(names).toContain("Serie O Robusto");
    expect(names).toContain("Tubos");
    expect(names).toContain("Serie O Puro");
    expect(names).toContain("Serie O Churchill");
    expect(names.length).toBeGreaterThanOrEqual(4);
  });

  it("Oliva Serie V / Melanio — Melanio vitole, ne Double Robusto", () => {
    const melanio = CIGARS.find((c) => c.id === "cig-oliva-serie-v-melanio");
    expect(melanio).toBeDefined();
    expect(melanio!.line).toBe("Serie V / Melanio");
    const names = (melanio!.vitolas ?? []).map((v) => v.name);
    expect(names.some((n) => n.toLowerCase().includes("melanio"))).toBe(true);
    expect(names).not.toContain("Double Robusto");
  });

  it("Oliva — nema Paperboy vitole/URL-a; Additional Vitolas uklonjen", () => {
    expect(CIGARS.find((c) => c.id === "cig-oliva-oliva-extra")).toBeUndefined();
    expect(CIGARS.find((c) => c.brand === "Oliva" && c.line === "Additional Vitolas")).toBeUndefined();
    for (const c of CIGARS.filter((x) => x.brand === "Oliva")) {
      expect((c.priceUrl ?? "").toLowerCase()).not.toContain("paperboy");
      for (const v of c.vitolas ?? []) {
        expect((v.url ?? "").toLowerCase()).not.toContain("paperboy");
        expect(v.name.toLowerCase()).not.toContain("paperboy");
      }
    }
  });

  it("Nub vitole žive pod Nub brendom, ne pod Olivom", () => {
    for (const c of CIGARS.filter((x) => x.brand === "Oliva")) {
      const nubVitolas = (c.vitolas ?? []).filter((v) => v.name.toLowerCase().includes("nub"));
      expect(nubVitolas).toEqual([]);
    }
    const nubCt = CIGARS.find((c) => c.id === "cig-nub-connecticut");
    expect(nubCt).toBeDefined();
    expect((nubCt!.vitolas ?? []).map((v) => v.name)).toContain("460");
  });

  it("Paperboy — zaseban unos s humidor cijenom", () => {
    const pb = CIGARS.find((c) => c.id === "cig-paperboy-connecticut");
    expect(pb).toBeDefined();
    expect(pb!.brand).toBe("Paperboy");
    expect(pb!.country).toBe("Dominikanska Republika");
    expect(pb!.priceEUR).toBe(4.5);
    expect(pb!.priceUrl).toContain("paperboy");
  });

  // regresija za klasu grešaka: shop product URL zalijepljen na krivi brend
  // (Paperboy->Oliva, La Instructora->Bolívar, Don Kiki->CAO, Partagás->Padrón...)
  it("nema search-only Humidor URL-ova (?s= / post_type=product)", () => {
    const bad: string[] = [];
    for (const c of CIGARS) {
      const urls: { where: string; url: string }[] = [];
      if (c.priceUrl) urls.push({ where: "priceUrl", url: c.priceUrl });
      for (const v of c.vitolas ?? []) {
        if (v.url) urls.push({ where: `vitola:${v.name}`, url: v.url });
      }
      for (const { where, url } of urls) {
        if (url.includes("?s=") || url.includes("post_type=product")) {
          bad.push(`${c.id} ${where}: ${url}`);
        }
      }
    }
    expect(bad).toEqual([]);
  });

  it("shop product URL-ovi dijele barem jedan token s brendom/linijom/vitolama", () => {
    const strip = (s: string) =>
      s.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    const productSlug = (url: string): string | null => {
      const m = url.match(
        /(?:humidor\.hr|havana-cigar-shop\.com)\/(?:hr\/|en\/)?proizvod\/([^/]+)/,
      );
      return m ? m[1] : null;
    };
    const violations: string[] = [];
    for (const c of CIGARS) {
      const tokens = new Set(
        strip([c.brand, c.line, ...(c.vitolas ?? []).map((v) => v.name)].join(" "))
          .split(/[^a-z0-9]+/)
          .filter((t) => t.length >= 4),
      );
      const urls: string[] = [];
      if (c.priceUrl) urls.push(c.priceUrl);
      for (const v of c.vitolas ?? []) if (v.url) urls.push(v.url);
      for (const url of urls) {
        const slug = productSlug(decodeURIComponent(url));
        if (!slug) continue; // search/brand stranice ne provjeravamo
        const slugTokens = slug.split(/[^a-z0-9]+/i).map(strip).filter((t) => t.length >= 4);
        if (!slugTokens.some((t) => tokens.has(t))) {
          violations.push(`${c.id}: ${url}`);
        }
      }
    }
    expect(violations).toEqual([]);
  });

  it("nema ugniježđenih vitola-duplikata (Serie G Double Robusto)", () => {
    expect(CIGARS.find((c) => c.id === "cig-oliva-serie-g-double-robusto-5-x-54")).toBeUndefined();
    expect(CIGARS.find((c) => c.id === "cig-oliva-serie-g-special-g")).toBeUndefined();
  });

  it("Oliva Serie G — odabir po id-u vraća istu liniju", () => {
    const serieG = CIGARS.find((c) => c.id === "cig-oliva-serie-g");
    expect(serieG).toBeDefined();
    expect(serieG!.line).toBe("Serie G");
    expect(serieG!.vitola.toLowerCase()).toBe("special g");
  });

  it("Arturo Fuente Gran Reserva — zadana vitola, ~12 €, Cuban Corona na Humidoru", () => {
    const gr = CIGARS.find((c) => c.id === "cig-arturo-fuente-gran-reserva");
    expect(gr).toBeDefined();
    const mp = cigarPriceForMarket(gr!, "HR");
    expect(mp.price).toBeGreaterThanOrEqual(12);
    expect(mp.price).toBeLessThanOrEqual(13);
    const link = cigarLinkForMarket(gr!, "HR");
    expect(link).toContain("arturo-fuente-cuban-corona");
    expect(link).toContain("humidor.hr");
    expect(link).not.toContain("cubanitos");
    expect(gr!.priceUrl).toContain("arturo-fuente-cuban-corona");
  });

  it("Holt's all-cigar-brands listing nije exact product link", () => {
    const mont = CIGARS.find((c) => c.id === "cig-oliva-monticello");
    expect(mont).toBeDefined();
    // listing ostaje na liniji, ne na svakoj vitoli
    for (const v of mont!.vitolas ?? []) {
      expect(v.regionLinks?.USA?.url ?? "").not.toMatch(/all-cigar-brands/);
    }
    expect(mont!.regionLinks?.USA?.url).toContain("oliva-monticello.html");
    const holts = cigarShopLinks(mont!).find((l) => l.shop === "Holt's");
    expect(holts).toBeDefined();
    expect(holts!.exact).toBe(false);
  });

  it("Serie V / Melanio priceUrl nije Serie O", () => {
    for (const id of ["cig-oliva-serie-v", "cig-oliva-serie-v-melanio"] as const) {
      const c = CIGARS.find((x) => x.id === id);
      expect(c).toBeDefined();
      expect((c!.priceUrl ?? "").toLowerCase()).not.toContain("serie-o");
      expect((c!.priceUrl ?? "").toLowerCase()).toMatch(/serie-v/);
      expect((c!.priceUrl ?? "").toLowerCase()).not.toMatch(/sampler/);
    }
  });

  it("Serie V Melanio ima CigarWorld Robusto/Churchill i Holts line listing", () => {
    const m = CIGARS.find((c) => c.id === "cig-oliva-serie-v-melanio");
    expect(m).toBeDefined();
    expect(m!.line).toContain("Melanio");
    const robusto = m!.vitolas?.find((v) => /robusto/i.test(v.name));
    const churchill = m!.vitolas?.find((v) => /^churchill$/i.test(v.name));
    expect(robusto?.format).toBe("52 x 127mm");
    expect(robusto?.regionLinks?.EU?.url).toContain("melanio-boxpressed-robusto");
    expect(churchill?.format).toBe("50 x 178mm");
    expect(churchill?.regionLinks?.EU?.url).toContain("melanio-boxpressed-churchill");
    expect(m!.regionLinks?.USA?.url).toContain("oliva-serie-v-melanio.html");
    expect(CIGARS.find((c) => c.id === "cig-oliva-monticello-double")).toBeUndefined();
    expect(CIGARS.find((c) => c.id === "cig-alec-bradley-sanctum-double")).toBeUndefined();
  });

  it("USA kupnja ide na Holt's search po nazivu, ne na Google site: (0 pogodaka)", () => {
    const withUsa = CIGARS.find((c) => c.markets.includes("USA"));
    expect(withUsa).toBeDefined();
    const usa = cigarLinkForMarket(withUsa!, "USA");
    expect(usa).toContain("holts.com");
    expect(usa).toContain(encodeURIComponent(`${withUsa!.brand} ${withUsa!.line}`.trim()));
    expect(usa).not.toContain("google.com");
    expect(usa).not.toContain("site%3A");
  });

  it("cigarShopLinks — po regiji tocne trgovine i izravni HR link gdje postoji", () => {
    // HR: Humidor + Havana; EU: CigarWorld; USA: Holt's + Cigars Daily
    const withAll = CIGARS.find(
      (c) =>
        c.markets.includes("HR") &&
        c.markets.includes("EU") &&
        c.markets.includes("USA"),
    );
    expect(withAll).toBeDefined();
    const links = cigarShopLinks(withAll!);
    const hosts = (region: string) =>
      links.filter((l) => l.region === region).map((l) => new URL(l.url).host);
    expect(hosts("HR").some((h) => h.includes("humidor.hr"))).toBe(true);
    expect(hosts("HR").some((h) => h.includes("havana-cigar-shop.com"))).toBe(true);
    expect(hosts("EU").some((h) => h.includes("cigarworld.de"))).toBe(true);
    expect(hosts("USA").some((h) => h.includes("holts.com"))).toBe(true);
    expect(hosts("USA").some((h) => h.includes("cigarsdaily.com"))).toBe(true);
    // regije koje cigara ne pokriva se ne pojavljuju
    const hrOnly = CIGARS.find((c) => !c.markets.includes("EU") && !c.markets.includes("USA"));
    if (hrOnly) {
      expect(cigarShopLinks(hrOnly).every((l) => l.region === "HR")).toBe(true);
    }
  });

  it("market unosi (catalogSource) — čist brend/linija/vitola, format, profil", () => {
    const mkt = CIGARS.filter((c) => c.catalogSource === "market");
    expect(mkt.length).toBeGreaterThan(0);
    const bad: string[] = [];
    for (const c of mkt) {
      if (!c.brand || !c.line || !c.vitola) bad.push(`${c.id}: prazan brand/line/vitola`);
      if (/[()\[\]{}]/.test(c.line)) bad.push(`${c.id}: zagrade u liniji '${c.line}'`);
      if (!/\d+\s*x\s*\d+mm/.test(c.format)) bad.push(`${c.id}: format '${c.format}'`);
      if (c.profileEstimated !== true) bad.push(`${c.id}: nije profileEstimated`);
      if (!c.vitolas?.length) bad.push(`${c.id}: nema vitola`);
      if (!c.regionLinks || Object.keys(c.regionLinks).length === 0)
        bad.push(`${c.id}: nema regionLinks`);
    }
    expect(bad).toEqual([]);
  });

  it("embargo — nijedna kubanka nema USA tržište/regionLinks", () => {
    const cuban = CIGARS.filter((c) => /kub|cuba/i.test(c.country));
    expect(cuban.length).toBeGreaterThan(0);
    const bad = cuban.filter(
      (c) => c.markets.includes("USA") || c.regionLinks?.USA,
    );
    expect(bad.map((c) => c.id)).toEqual([]);
  });

  it("regionLinks — host odgovara regiji; EU/USA link postoji (listing ≠ exact)", () => {
    const hostByRegion: Record<string, string[]> = {
      HR: ["humidor.hr", "havana-cigar-shop.com"],
      EU: ["cigarworld.de"],
      USA: ["holts.com", "cigarsdaily.com"],
    };
    const bad: string[] = [];
    for (const c of CIGARS) {
      for (const [region, link] of Object.entries(c.regionLinks ?? {})) {
        const host = new URL(link.url).host;
        if (!hostByRegion[region].some((h) => host.includes(h))) {
          bad.push(`${c.id}: ${region} -> ${host}`);
        }
        // EU/USA regionLink mora biti u cigarShopLinks; Holts listing = exact:false
        if (region !== "HR") {
          const sl = cigarShopLinks(c).find(
            (l) => l.region === region && l.url === link.url,
          );
          if (!sl) bad.push(`${c.id}: ${region} regionLink nije u cigarShopLinks`);
          const listing = /holts\.com\/cigars\/all-cigar-brands\//i.test(link.url);
          if (listing && sl?.exact) {
            bad.push(`${c.id}: Holts listing ne smije biti exact`);
          }
          if (!listing && !sl?.exact) {
            bad.push(`${c.id}: ${region} product regionLink nije exact u cigarShopLinks`);
          }
        }
      }
    }
    expect(bad).toEqual([]);
  });

  it("ALL filter prikazuje HR cijenu i HR link", () => {
    const gr = CIGARS.find((c) => c.id === "cig-arturo-fuente-gran-reserva")!;
    expect(cigarPriceForMarket(gr, "ALL").price).toBe(cigarPriceForMarket(gr, "HR").price);
    expect(cigarLinkForMarket(gr, "ALL")).toContain("humidor.hr");
  });

  it("HR buy gumb ne koristi regionLinks.HR kad se razlikuje od zadane vitole", () => {
    // Blend 15: regionLinks.HR = Short Robusto 5.9, zadana = Robusto 6.3
    const blend = CIGARS.find((c) => c.id === "cig-aj-fernandez-blend-15")!;
    expect(blend.regionLinks?.HR?.priceEUR).toBe(5.9);
    expect(cigarPriceForMarket(blend, "HR").price).toBe(6.3);
    const humidor = cigarShopLinks(blend).find((l) => l.shop === "The Humidor");
    expect(humidor?.exact).toBe(true);
    expect(humidor?.url).toContain("blend-15-robusto");
    expect(cigarShopLinkPrice(blend, humidor!).price).toBe(6.3);
  });

  it("HR buy gumb ne pokazuje cijenu na search linku iz regionLinks.HR", () => {
    // Escurio: regionLinks.HR = Primeros 7.15 na Humidoru, a vitole su na Havani
    const esc = CIGARS.find((c) => c.id === "cig-davidoff-escurio")!;
    expect(esc.regionLinks?.HR?.priceEUR).toBe(7.15);
    const humidor = cigarShopLinks(esc).find((l) => l.shop === "The Humidor");
    expect(humidor?.exact).toBe(false);
    expect(cigarShopLinkPrice(esc, humidor!).price).toBeNull();
    const havana = cigarShopLinks(esc).find((l) => l.shop === "Havana Cigar Shop");
    expect(havana?.exact).toBe(true);
    expect(cigarShopLinkPrice(esc, havana!).price).toBe(20.2);
  });

  it("HR exact link ne pada na vitolu s drugom cijenom (Cubanitos ≠ Gran Reserva)", () => {
    const gr = CIGARS.find((c) => c.id === "cig-arturo-fuente-gran-reserva")!;
    const havana = cigarShopLinks(gr).find((l) => l.shop === "Havana Cigar Shop");
    // smije biti Corona (12.3 € = zadana cijena), ne Cubanitos (5 €)
    expect(havana?.exact).toBe(true);
    expect(havana?.url ?? "").toContain("cuban-corona");
    expect(havana?.url ?? "").not.toContain("cubanitos");
    expect(cigarShopLinkPrice(gr, havana!).price).toBe(12.3);
  });

  it("HR exact buy cijena = cijena vitole na koju URL vodi", () => {
    const mismatches: string[] = [];
    for (const c of CIGARS) {
      for (const link of cigarShopLinks(c).filter((l) => l.region === "HR" && l.exact)) {
        const shown = cigarShopLinkPrice(c, link).price;
        const vitola = (c.vitolas ?? []).find((v) => v.url === link.url);
        if (vitola?.priceEUR != null && shown != null && Math.abs(vitola.priceEUR - shown) > 0.05) {
          mismatches.push(`${c.id} ${link.shop}: shown ${shown} vs vitola ${vitola.priceEUR}`);
        }
        // ne smije biti regionLinks.HR cijena ako se razlikuje od linkane vitole
        const rl = c.regionLinks?.HR;
        if (
          rl?.shop === link.shop &&
          rl.priceEUR != null &&
          vitola?.priceEUR != null &&
          Math.abs(rl.priceEUR - vitola.priceEUR) > 0.05 &&
          shown === rl.priceEUR
        ) {
          mismatches.push(`${c.id} ${link.shop}: still using regionLinks.HR ${rl.priceEUR}`);
        }
      }
    }
    expect(mismatches).toEqual([]);
  });

  it("EU/USA cijena dolazi iz regionLinks (scrape), null kad je nema — ne izmišlja se", () => {
    for (const region of ["EU", "USA"] as const) {
      const withLink = CIGARS.find((c) => c.regionLinks?.[region]?.priceEUR != null);
      if (withLink) {
        expect(cigarPriceForMarket(withLink, region).price).toBe(withLink.regionLinks![region]!.priceEUR);
      }
      const noLink = CIGARS.find((c) => !c.regionLinks?.[region]);
      if (noLink) expect(cigarPriceForMarket(noLink, region).price).toBeNull();
    }
  });

  it("brands.json i cigars.json — 1:1 pokrivenost brendova", () => {
    const cigarBrands = new Set(CIGARS.map((c) => c.brand));
    const brandKeys = new Set(Object.keys(brandsData as Record<string, unknown>));
    const missing = [...cigarBrands].filter((b) => !brandKeys.has(b));
    const orphan = [...brandKeys].filter((b) => !cigarBrands.has(b));
    expect(missing).toEqual([]);
    expect(orphan).toEqual([]);
    expect(BRAND_CATALOG.length).toBe(ALL_BRANDS.length);
    expect(BRAND_CATALOG.every((b) => b.lineCount >= 0 && b.vitolaCount >= 0)).toBe(true);
  });

  it("Padrón i Drew Estate — Additional Vitolas remapkan u imenovane linije", () => {
    expect(CIGARS.find((c) => c.id === "cig-padron-padron-extra")).toBeUndefined();
    expect(CIGARS.find((c) => c.id === "cig-drew-estate-de-extra")).toBeUndefined();

    const s1926 = CIGARS.find((c) => c.id === "cig-padron-1926-serie");
    expect(s1926).toBeDefined();
    const n1926 = (s1926!.vitolas ?? []).map((v) => v.name.toLowerCase());
    expect(n1926.some((n) => n.includes("no. 6") || n.includes("no.6"))).toBe(true);

    const family = CIGARS.find((c) => c.id === "cig-padron-family-reserve");
    expect((family!.vitolas ?? []).map((v) => v.name).join(" ")).toMatch(/45|44/);

    const liga = CIGARS.find((c) => c.id === "cig-drew-estate-liga-privada-unico-serie");
    expect(liga).toBeDefined();
    const ligaNames = (liga!.vitolas ?? []).map((v) => v.name.toLowerCase()).join(" ");
    expect(ligaNames).toMatch(/papas|fritas|seleccion/);
    expect(
      (liga!.vitolas ?? []).some(
        (v) => v.url?.includes("liga-privada-10-seleccion"),
      ),
    ).toBe(true);

    const liga9 = CIGARS.find((c) => c.id === "cig-drew-estate-liga-privada-no-9");
    expect(liga9!.priceEUR).toBe(23);
    expect(liga9!.priceUrl).toContain("liga-privada-no-9-toro");
  });

  it("Batch B — Additional Vitolas uklonjen za 7 brendova", () => {
    const brands = [
      "Macanudo",
      "Foundation Cigar Company",
      "E.P. Carrillo",
      "Davidoff",
      "Camacho",
      "CAO",
      "Alec Bradley",
    ];
    for (const brand of brands) {
      const extra = CIGARS.find((c) => c.brand === brand && c.line === "Additional Vitolas");
      expect(extra, brand).toBeUndefined();
    }
    expect(CIGARS.some((c) => c.brand === "Macanudo" && /inspirado/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Alec Bradley" && /kintsugi/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Camacho" && /escuro/i.test(c.line))).toBe(true);
  });

  it("Batch C — Rocky Patel, My Father, Tatuaje bez Additional Vitolas", () => {
    for (const brand of ["Rocky Patel", "My Father", "Tatuaje"]) {
      expect(
        CIGARS.find((c) => c.brand === brand && c.line === "Additional Vitolas"),
        brand,
      ).toBeUndefined();
    }
    const decade = CIGARS.find((c) => c.brand === "Rocky Patel" && /decade/i.test(c.line));
    expect(decade).toBeDefined();
    expect((decade!.vitolas ?? []).length).toBeGreaterThanOrEqual(3);

    expect(CIGARS.some((c) => c.brand === "My Father" && /le bijou/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "My Father" && /centurion/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Tatuaje" && /cabaiguan/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Tatuaje" && /fausto/i.test(c.line))).toBe(true);

    // Stream J absorbed the dim-suffixed SKU into the Sixty line.
    const sixty = CIGARS.find((c) => c.id === "cig-rocky-patel-sixty");
    expect(sixty).toBeDefined();
    const sixtyToro = (sixty!.vitolas ?? []).find(
      (v) => /sixty\s*toro/i.test(v.name) && (v.priceEUR ?? 0) === 26,
    );
    expect(sixtyToro?.priceEUR).toBe(26);
    expect(sixtyToro?.url ?? sixty?.priceUrl).toContain("rocky-patel-sixty");
  });

  it("Batch D — kubanke bez Additional Vitolas", () => {
    const brands = [
      "Trinidad",
      "Punch",
      "Hoyo de Monterrey",
      "Cohiba",
      "Partagás",
      "Montecristo",
      "Quai d'Orsay",
      "Juan López",
      "Bolívar",
    ];
    for (const brand of brands) {
      expect(
        CIGARS.find((c) => c.brand === brand && c.line === "Additional Vitolas"),
        brand,
      ).toBeUndefined();
    }
    expect(CIGARS.some((c) => c.brand === "Trinidad" && /reyes/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Cohiba" && /siglo/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Montecristo" && /edmundo/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Partagás" && /serie d/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Bolívar" && /belicoso/i.test(c.line))).toBe(true);
  });

  it("Batch E — preostali brendovi bez Additional Vitolas", () => {
    const brands = [
      "Perdomo",
      "Ashton",
      "Plasencia",
      "La Aurora",
      "Oliva",
      "H. Upmann",
      "Romeo y Julieta",
    ];
    for (const brand of brands) {
      expect(
        CIGARS.find((c) => c.brand === brand && c.line === "Additional Vitolas"),
        brand,
      ).toBeUndefined();
    }
    expect(CIGARS.some((c) => c.brand === "Perdomo" && /lot 23/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Perdomo" && /esteli/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Ashton" && /symmetry/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Plasencia" && /alma del cielo/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "La Aurora" && /preferidos/i.test(c.line))).toBe(true);
    expect(CIGARS.some((c) => c.brand === "Oliva" && /serie g/i.test(c.line))).toBe(true);

    const magnum = CIGARS.find((c) => c.id === "cig-h-upmann-magnum");
    expect(magnum).toBeDefined();
    expect((magnum!.vitolas ?? []).some((v) => /magnum 54/i.test(v.name))).toBe(true);

    const classic = CIGARS.find((c) => c.id === "cig-romeo-y-julieta-classic");
    expect(classic).toBeDefined();
    expect((classic!.vitolas ?? []).some((v) => /puritos/i.test(v.name))).toBe(true);
  });

  it("AJ Fernandez — Blend 15, Last Call, Enclave, New World točne linije", () => {
    const ajf = CIGARS.filter((c) => c.brand === "AJ Fernandez");
    const byLine = Object.fromEntries(ajf.map((c) => [c.line, c]));

    expect(byLine["Blend 15"]).toBeDefined();
    expect((byLine["Blend 15"].vitolas ?? []).map((v) => v.name)).toEqual(
      expect.arrayContaining(["Short Robusto", "Robusto", "Toro"]),
    );

    const lastCall = byLine["Last Call"];
    expect(lastCall).toBeDefined();
    const lcNames = (lastCall.vitolas ?? []).map((v) => v.name);
    expect(lcNames).toEqual(expect.arrayContaining(["Habano Geniales", "Maduro Chiquitas"]));
    expect(lcNames.some((n) => n.toLowerCase().includes("pequenas"))).toBe(false);

    const enclave = byLine["Enclave"];
    expect(enclave).toBeDefined();
    const encNames = (enclave.vitolas ?? []).map((v) => v.name);
    expect(encNames.some((n) => n.toLowerCase().includes("churchill"))).toBe(false);
    expect(encNames).toEqual(
      expect.arrayContaining([
        "Broadleaf Robusto",
        "Broadleaf Toro",
        "Habano Robusto",
        "Habano Figurado",
        "Connecticut Robusto",
        "Connecticut Figurado",
      ]),
    );

    const nw = byLine["New World"];
    expect(nw).toBeDefined();
    expect((nw.vitolas ?? []).length).toBeGreaterThanOrEqual(10);
    const nwUrls = new Set((nw.vitolas ?? []).map((v) => v.url).filter(Boolean));
    expect(nwUrls.size).toBeGreaterThan(1);
    expect(
      [...nwUrls].every((u) => (u as string).includes("petit-corona-6-pack")),
    ).toBe(false);

    expect(CIGARS.find((c) => c.id === "cig-aj-fernandez-aj-extra")).toBeUndefined();
    for (const c of ajf) {
      if (c.line !== "Additional Vitolas") continue;
      const names = (c.vitolas ?? []).map((v) => v.name.toLowerCase()).join(" ");
      expect(names).not.toMatch(/last call|new world|enclave|dias|bellas artes/);
    }
  });

  it("zadana vitola priceUrl nije najjeftinija vitola kad se razlikuju", () => {
    const mismatches: string[] = [];
    for (const c of CIGARS) {
      const priced = (c.vitolas ?? []).filter((v) => v.priceEUR != null);
      if (priced.length < 2 || !c.priceUrl) continue;
      const cheapest = Math.min(...priced.map((v) => v.priceEUR as number));
      if (c.priceEUR != null && c.priceEUR > cheapest + 0.5) continue;
      const mp = cigarPriceForMarket(c, "HR");
      if (mp.price != null && mp.price <= cheapest + 0.5 && priced.some((v) => (v.priceEUR as number) > cheapest + 2)) {
        const defaultNamed = c.vitolas?.find((v) => v.name === c.vitola || v.name === c.line);
        if (defaultNamed && (defaultNamed.priceEUR as number) > cheapest + 2) {
          mismatches.push(c.id);
        }
      }
    }
    expect(mismatches).toEqual([]);
  });
});
