import { describe, it, expect } from "vitest";
import cigarsData from "./cigars.json";
import { CIGARS } from "./index";
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
    const melanio = CIGARS.find((c) => c.id === "cig-oliva-serie-v");
    expect(melanio).toBeDefined();
    expect(melanio!.line).toBe("Serie V / Melanio");
    const names = (melanio!.vitolas ?? []).map((v) => v.name);
    expect(names.some((n) => n.toLowerCase().includes("melanio"))).toBe(true);
    expect(names).not.toContain("Double Robusto");
  });

  it("Oliva Additional Vitolas — nema Paperboy vitole ni Paperboy link", () => {
    const extra = CIGARS.find((c) => c.id === "cig-oliva-oliva-extra");
    expect(extra).toBeDefined();
    const urls = (extra!.vitolas ?? []).map((v) => v.url).filter((u): u is string => Boolean(u));
    expect(urls.some((u) => u.toLowerCase().includes("paperboy"))).toBe(false);
    expect((extra!.priceUrl ?? "").toLowerCase()).not.toContain("paperboy");
  });

  it("Paperboy — zaseban unos s humidor cijenom", () => {
    const pb = CIGARS.find((c) => c.id === "cig-paperboy-connecticut");
    expect(pb).toBeDefined();
    expect(pb!.brand).toBe("Paperboy");
    expect(pb!.country).toBe("Dominikana");
    expect(pb!.priceEUR).toBe(4.5);
    expect(pb!.priceUrl).toContain("paperboy");
  });

  // regresija za klasu grešaka: shop product URL zalijepljen na krivi brend
  // (Paperboy->Oliva, La Instructora->Bolívar, Don Kiki->CAO, Partagás->Padrón...)
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
});
