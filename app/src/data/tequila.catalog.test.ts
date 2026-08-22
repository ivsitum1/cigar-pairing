// app/src/data/tequila.catalog.test.ts
import { describe, expect, it } from "vitest";
import type { Drink } from "../types";
import tequilasJson from "./tequilas.json";

const tequilas = tequilasJson as Drink[];

const TEQUILA_CURATED_IDS = [
  "tq-don-julio-blanco",
  "tq-don-julio-reposado",
  "tq-don-julio-anejo",
  "tq-don-julio-1942",
  "tq-patron-silver",
  "tq-patron-reposado",
  "tq-patron-anejo",
  "tq-casamigos-reposado",
  "tq-casamigos-anejo",
  "tq-casamigos-mezcal",
  "tq-espolon-blanco",
  "tq-clase-azul-reposado",
] as const;

describe("tequila catalog", () => {
  it("pairable boce imaju HR cigarHint i bilješku", () => {
    for (const t of tequilas.filter((d) => d.pairable && !d.meta)) {
      expect(t.cigarHint?.hr?.length ?? 0, t.id).toBeGreaterThanOrEqual(40);
      expect(t.notes?.hr?.length ?? 0, t.id).toBeGreaterThanOrEqual(40);
    }
  });

  it("referentni set ima punu HR+EN kopiju", () => {
    for (const id of TEQUILA_CURATED_IDS) {
      const t = tequilas.find((d) => d.id === id);
      expect(t, id).toBeDefined();
      expect(t!.notes.hr.length, id).toBeGreaterThanOrEqual(80);
      expect(t!.notes.en.length, id).toBeGreaterThanOrEqual(80);
      expect(t!.cigarHint?.hr?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(t!.cigarHint?.en?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(t!.profileEstimated, id).not.toBe(true);
    }
  });

  it("shopHR odgovara priceUrl hostu", () => {
    for (const t of tequilas) {
      const url = t.priceUrl;
      if (!url) continue;
      const host = new URL(url).hostname.replace(/^www\./, "");
      const shop = (t.shopHR ?? "").toLowerCase();
      if (shop.includes("allez")) expect(host).toContain("allez.hr");
      if (shop.includes("ecuga")) expect(host).toContain("ecuga.com");
    }
  });
});
