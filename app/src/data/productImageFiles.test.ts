import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import local from "./productImagesLocal.json";

/**
 * Manifest obrađenih slika i sadržaj `public/img/products/` moraju se poklapati.
 *
 * `productImage.test.ts` čuva smjer manifest → katalog (nema zapisa za id koji
 * katalog ne zna). Ovaj čuva smjer manifest ↔ disk, koji nitko nije provjeravao:
 * zapis bez datoteke daje slomljenu sliku na kartici, datoteka bez zapisa se
 * isporučuje uzalud. Pri nekoliko tisuća slika taj se raskorak ne vidi očima.
 */
const ROOT = "public/img/products";
const KINDS = ["cigars", "drinks"] as const;

type Manifest = Record<string, { w: number; h: number; t: string }>;
const manifest = (kind: (typeof KINDS)[number]): Manifest =>
  ((local as Record<string, unknown>)[kind] ?? {}) as Manifest;

describe("obrađene fotografije: manifest ↔ disk", () => {
  it.each(KINDS)("svaki zapis u %s ima svoju .webp datoteku", (kind) => {
    const missing = Object.keys(manifest(kind)).filter(
      (id) => !existsSync(join(ROOT, kind, `${id}.webp`)),
    );
    expect(missing).toEqual([]);
  });

  it.each(KINDS)("nijedna datoteka u %s nije bez zapisa u manifestu", (kind) => {
    const known = new Set(Object.keys(manifest(kind)));
    const orphans = readdirSync(join(ROOT, kind))
      .filter((f) => f.endsWith(".webp"))
      .filter((f) => !known.has(f.slice(0, -".webp".length)));
    expect(orphans).toEqual([]);
  });

  it.each(KINDS)("%s: dimenzije i postupak su upotrebljivi", (kind) => {
    const bad = Object.entries(manifest(kind))
      .filter(([, v]) => !(v.w > 0 && v.h > 0) || !["cutout", "framed"].includes(v.t))
      .map(([id]) => id);
    expect(bad).toEqual([]);
  });

  it("u products/ nema drugih mapa osim cigars i drinks", () => {
    const entries = readdirSync(ROOT, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name)
      .sort();
    expect(entries).toEqual([...KINDS].sort());
  });
});
