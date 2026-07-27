import { describe, it, expect } from "vitest";
import { CIGARS } from "../data";
import { applyVitola, uniqueVitolas } from "./cigarVitola";
import type { Cigar, Vitola } from "../types";

const strip = (s: string) =>
  s
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();

const productSlug = (url: string): string | null => {
  const m = url.match(
    /(?:humidor\.hr|havana-cigar-shop\.com)\/(?:hr\/|en\/)?proizvod\/([^/?#]+)/i,
  );
  return m ? decodeURIComponent(m[1]) : null;
};

const tokens = (s: string) =>
  strip(s)
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 3);

/** Shape tokens that, if present in a product slug, should also appear in the vitola name. */
const SHAPE_MARKERS = [
  "robusto",
  "churchill",
  "toro",
  "torpedo",
  "belicoso",
  "perfecto",
  "corona",
  "lancero",
  "figurado",
  "piramide",
  "pyramid",
  "gordo",
  "presidente",
  "lonsdale",
  "panatela",
  "petit",
  "double",
  "tubos",
  "tubo",
  "special",
] as const;

function dimsComparable(a: Vitola, b: Vitola): boolean {
  return (
    Boolean(a.format && b.format && a.format !== "—" && b.format !== "—") ||
    (a.ring != null && b.ring != null) ||
    (a.lengthMM != null && b.lengthMM != null)
  );
}

function dimsMatch(a: Vitola, b: Vitola): boolean {
  const formatOk =
    a.format && b.format && a.format !== "—" && b.format !== "—"
      ? a.format === b.format
      : true;
  const ringOk = a.ring != null && b.ring != null ? a.ring === b.ring : true;
  const lenOk =
    a.lengthMM != null && b.lengthMM != null ? a.lengthMM === b.lengthMM : true;
  return formatOk && ringOk && lenOk;
}

describe("vitola ↔ shop link integrity (full catalog)", () => {
  it("applyVitola nikad ne zadrži priceUrl drugog formata/dimenzije", () => {
    const bad: string[] = [];
    for (const c of CIGARS) {
      const vitolas = uniqueVitolas(c);
      if (vitolas.length < 2) continue;
      const anchor = vitolas.find((v) => v.url && v.url === c.priceUrl);
      if (!anchor || !c.priceUrl) continue;

      for (const v of vitolas) {
        if (v.url) continue;
        if (!dimsComparable(anchor, v)) continue;
        if (dimsMatch(anchor, v)) continue;

        const applied = applyVitola(c, v);
        if (applied.priceUrl === c.priceUrl) {
          bad.push(
            `${c.id} :: ${v.name} still inherits ${c.priceUrl} (anchor ${anchor.name} ${anchor.format})`,
          );
        }
      }
    }
    expect(bad).toEqual([]);
  });

  it("vitola.url slug sadrži oblik iz imena kad slug uopće ima shape marker", () => {
    // False-positive filter: compound shop slugovi (toro-gordo, special-r-tubos)
    // su OK dok god sadrže oblik iz imena vitole.
    // Fail: slug ima oblik sestrinske vitole, a NE sadrži oblik ove vitole.
    const bad: string[] = [];
    for (const c of CIGARS) {
      for (const v of c.vitolas ?? []) {
        if (!v.url) continue;
        const slug = productSlug(v.url);
        if (!slug) continue;
        const slugTok = new Set(tokens(slug));
        const nameTok = new Set(tokens(v.name));
        const nameShapes = SHAPE_MARKERS.filter((m) => nameTok.has(m));
        if (nameShapes.length === 0) continue;
        if (nameShapes.some((m) => slugTok.has(m))) continue;

        for (const marker of SHAPE_MARKERS) {
          if (!slugTok.has(marker)) continue;
          const siblingOwns = (c.vitolas ?? []).some(
            (s) => s !== v && tokens(s.name).includes(marker),
          );
          if (siblingOwns) {
            bad.push(`${c.id} :: ${v.name} → ${slug} (missing own shape; has sibling ${marker})`);
          }
        }
      }
    }
    expect(bad).toEqual([]);
  });

  it("poznati cross-line / krivi SKU regressioni slučajevi", () => {
    const mb = CIGARS.find((c) => c.id === "cig-oliva-master-blends-3");
    expect(mb).toBeDefined();
    expect((mb!.priceUrl ?? "").toLowerCase()).not.toContain("serie-g");

    const serieV = CIGARS.find((c) => c.id === "cig-oliva-serie-v");
    expect(serieV).toBeDefined();
    const doubleToro = (serieV!.vitolas ?? []).find((v) => /double toro/i.test(v.name));
    expect(doubleToro?.url ?? "").toContain("double-toro");
    expect((serieV!.vitolas ?? []).some((v) => v.name === "Toro" && (v.url ?? "").includes("double-toro"))).toBe(
      false,
    );

    const donCarlos = CIGARS.find((c) => c.id === "cig-arturo-fuente-don-carlos");
    expect(donCarlos).toBeDefined();
    expect((donCarlos!.vitolas ?? []).map((v) => v.name)).not.toContain("Don Carlos");

    const nicaragua = CIGARS.find((c) => c.id === "cig-davidoff-nicaragua");
    expect(nicaragua).toBeDefined();
    const robusto = (nicaragua!.vitolas ?? []).find((v) => /^robusto$/i.test(v.name));
    expect((robusto?.url ?? "").toLowerCase()).not.toContain("tubos");
  });

  it("line priceUrl, ako je product URL, pripada nekoj vitoli ili dijeli token s brand/line", () => {
    const bad: string[] = [];
    for (const c of CIGARS) {
      if (!c.priceUrl) continue;
      const slug = productSlug(c.priceUrl);
      if (!slug) continue;
      const owned = (c.vitolas ?? []).some((v) => v.url === c.priceUrl);
      if (owned) continue;
      const pool = new Set(tokens(`${c.brand} ${c.line}`));
      const slugTok = tokens(slug);
      if (!slugTok.some((t) => pool.has(t) && t.length >= 4)) {
        bad.push(`${c.id}: orphan priceUrl ${c.priceUrl}`);
      }
    }
    expect(bad).toEqual([]);
  });

  it("Olivа Serie O/G — poznati regressioni slučajevi", () => {
    const serieO = CIGARS.find((c) => c.id === "cig-oliva-serie-o");
    expect(serieO).toBeDefined();
    const names = (serieO!.vitolas ?? []).map((v) => v.name);
    expect(names).not.toContain("Serie O Puro");
    const churchill = (serieO!.vitolas ?? []).find((v) => /churchill/i.test(v.name));
    expect(churchill?.ring).toBe(50);
    expect(churchill?.lengthMM).toBe(178);
    if (churchill) {
      const applied = applyVitola(serieO!, churchill);
      expect(applied.priceUrl).toBeNull();
    }

    const serieG = CIGARS.find((c) => c.id === "cig-oliva-serie-g");
    expect(serieG).toBeDefined();
    const gRobusto = (serieG!.vitolas ?? []).find((v) => /serie g robusto/i.test(v.name));
    expect(gRobusto?.lengthMM).toBe(114);
    if (gRobusto) {
      const applied = applyVitola(serieG!, gRobusto);
      expect(applied.priceUrl).toBeNull();
    }
  });
});

/** Audit helper — broji vitole bez URL-a koje bi prije guard-a naslijedile krivi link. */
export function countProtectedMismatches(cigars: Cigar[] = CIGARS): number {
  let n = 0;
  for (const c of cigars) {
    const vitolas = uniqueVitolas(c);
    const anchor = vitolas.find((v) => v.url && v.url === c.priceUrl);
    if (!anchor || !c.priceUrl) continue;
    for (const v of vitolas) {
      if (v.url) continue;
      if (!dimsComparable(anchor, v) || dimsMatch(anchor, v)) continue;
      n += 1;
    }
  }
  return n;
}
