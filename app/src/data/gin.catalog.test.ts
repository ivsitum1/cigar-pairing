// app/src/data/gin.catalog.test.ts
import { describe, expect, it } from "vitest";
import type { Drink } from "../types";
import ginsJson from "./gins.json";

const gins = ginsJson as Drink[];

const GIN_CURATED_IDS = [
  "gin-monkey-47-schwarzwald-dry-gin-47-vol-0-5l",
  "gin-hendrick-s-gin-41-4-vol-0-7l",
  "gin-tanqueray-no-ten-47-3-vol-0-7l",
  "gin-the-botanist-islay-dry-gin-46-vol-0-7l",
  "gin-gin-mare-capri-mediterranean-gin-42-7-vol-0-7l",
  "gin-plymouth-gin",
  "gin-sipsmith-london-dry-gin-41-6-0-7-l",
  "gin-nikka-coffey-gin-47-vol-0-7l",
  "gin-four-pillars-rare-dry-gin-41-8-vol-0-7l",
  "gin-old-pilot-s-dalmatian-dry-gin-45-vol-0-7l",
  "gin-dugave-gin",
  "gin-beefeater-24",
  "gin-aviation-gin-42-0-7-l",
  "gin-roku-japanese-craft-gin-43-0-7-l",
] as const;

describe("gin catalog", () => {
  it("pairable boce imaju HR cigarHint i bilješku", () => {
    for (const g of gins.filter((d) => d.pairable && !d.meta)) {
      expect(g.cigarHint?.hr?.length ?? 0, g.id).toBeGreaterThanOrEqual(40);
      expect(g.notes?.hr?.length ?? 0, g.id).toBeGreaterThanOrEqual(40);
    }
  });

  it("referentni set ima punu HR+EN kopiju", () => {
    for (const id of GIN_CURATED_IDS) {
      const g = gins.find((d) => d.id === id);
      expect(g, id).toBeDefined();
      expect(g!.notes.hr.length, id).toBeGreaterThanOrEqual(80);
      expect(g!.notes.en.length, id).toBeGreaterThanOrEqual(80);
      expect(g!.cigarHint?.hr?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(g!.cigarHint?.en?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(g!.profileEstimated, id).not.toBe(true);
    }
  });

  it("pairable non-meta imaju dovoljno jedinstvenih HR cigarHint", () => {
    const hints = gins
      .filter((d) => d.pairable && !d.meta)
      .map((d) => d.cigarHint?.hr ?? "")
      .filter((h) => h.length >= 40);
    expect(new Set(hints).size).toBeGreaterThanOrEqual(40);
  });

  it("shopHR odgovara priceUrl hostu", () => {
    for (const g of gins) {
      const url = g.priceUrl;
      if (!url) continue;
      const host = new URL(url).hostname.replace(/^www\./, "");
      const shop = (g.shopHR ?? "").toLowerCase();
      if (shop.includes("allez")) expect(host).toContain("allez.hr");
      if (shop.includes("ecuga")) expect(host).toContain("ecuga.com");
    }
  });
});
