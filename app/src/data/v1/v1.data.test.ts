import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import {
  OfferSchema,
  ProductSchema,
  ShopSchema,
  VitolaSchema,
} from "../schema";
import { CIGARS, ALL_DRINKS, cigarCountByRegion } from "../index";
import cigarIdAliasesJson from "../cigarIdAliases.json";
import drinkIdAliasesJson from "../drinkIdAliases.json";

const here = dirname(fileURLToPath(import.meta.url));

function load<T>(name: string): T {
  return JSON.parse(readFileSync(join(here, name), "utf-8")) as T;
}

type Product = ReturnType<typeof ProductSchema.parse>;
type Vitola = ReturnType<typeof VitolaSchema.parse>;
type Shop = ReturnType<typeof ShopSchema.parse>;
type Offer = ReturnType<typeof OfferSchema.parse>;

const products = load<Product[]>("products.json");
const vitolas = load<Vitola[]>("vitolas.json");
const shops = load<Shop[]>("shops.json");
const offers = load<Offer[]>("offers.json");

describe("v1 data layer", () => {
  it("validates all products against ProductSchema", () => {
    for (const p of products) {
      const r = ProductSchema.safeParse(p);
      expect(r.success, r.success ? "" : JSON.stringify(r.error.issues.slice(0, 3))).toBe(
        true,
      );
    }
  });

  it("validates all vitolas against VitolaSchema", () => {
    for (const v of vitolas) {
      const r = VitolaSchema.safeParse(v);
      expect(r.success, r.success ? "" : JSON.stringify(r.error.issues.slice(0, 3))).toBe(
        true,
      );
    }
  });

  it("validates all shops against ShopSchema", () => {
    for (const s of shops) {
      const r = ShopSchema.safeParse(s);
      expect(r.success, r.success ? "" : JSON.stringify(r.error.issues.slice(0, 3))).toBe(
        true,
      );
    }
  });

  it("validates all offers against OfferSchema", () => {
    for (const o of offers) {
      const r = OfferSchema.safeParse(o);
      expect(r.success, r.success ? "" : JSON.stringify(r.error.issues.slice(0, 3))).toBe(
        true,
      );
    }
  });

  it("product id set equals current cigars + drinks (no loss, no new)", () => {
    const expected = new Set([
      ...CIGARS.map((c) => c.id),
      ...ALL_DRINKS.map((d) => d.id),
    ]);
    const got = new Set(products.map((p) => p.id));
    expect(got.size).toBe(expected.size);
    for (const id of expected) expect(got.has(id), id).toBe(true);
    for (const id of got) expect(expected.has(id), id).toBe(true);
  });

  it("every vitola from cigars.json exists as productId@slug", () => {
    const slug = (label: string) =>
      label
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[''`]/g, "")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");

    const got = new Set(vitolas.map((v) => v.id));
    for (const c of CIGARS) {
      for (const v of c.vitolas ?? []) {
        const id = `${c.id}@${slug(v.name)}`;
        expect(got.has(id), id).toBe(true);
      }
    }
  });

  it("every cigar/drink alias resolves to an existing product", () => {
    const ids = new Set(products.map((p) => p.id));
    const cigarAliases = (cigarIdAliasesJson as { aliases: Record<string, string> })
      .aliases;
    const drinkAliases = (drinkIdAliasesJson as { aliases: Record<string, string> })
      .aliases;
    for (const [from, to] of Object.entries(cigarAliases)) {
      expect(ids.has(to), `cigar alias ${from} → ${to}`).toBe(true);
    }
    for (const [from, to] of Object.entries(drinkAliases)) {
      if (from.startsWith("_")) continue;
      expect(ids.has(to), `drink alias ${from} → ${to}`).toBe(true);
    }
  });

  it("offers are unique on (shop, product, vitola, url) and walkIn shops have no url", () => {
    const walkIn = new Set(
      shops.filter((s) => s.type === "walkIn").map((s) => s.id),
    );
    const keys = new Set<string>();
    for (const o of offers) {
      const k = `${o.shopId}|${o.productId}|${o.vitolaId ?? ""}|${o.url ?? ""}`;
      expect(keys.has(k), k).toBe(false);
      keys.add(k);
      if (walkIn.has(o.shopId)) {
        expect(o.url == null || o.url === "", o.id).toBe(true);
      }
    }
    expect(offers.length).toBe(keys.size);
  });

  it("every offer.shopId exists; every shop.region is HR|EU|USA", () => {
    const shopIds = new Set(shops.map((s) => s.id));
    for (const o of offers) {
      expect(shopIds.has(o.shopId), o.shopId).toBe(true);
    }
    for (const s of shops) {
      expect(["HR", "EU", "USA"]).toContain(s.region);
    }
    expect(shops.some((s) => s.id === "wine-searcher")).toBe(false);
  });

  it("Aficionado is walkIn / manual / aficionado", () => {
    const a = shops.find((s) => s.id === "aficionado-zg");
    expect(a).toBeTruthy();
    expect(a!.type).toBe("walkIn");
    expect(a!.source).toBe("manual");
    expect(a!.adapter).toBe("aficionado");
  });

  it("region product counts from offers >= cigarCountByRegion", () => {
    const shopRegion = new Map(shops.map((s) => [s.id, s.region]));
    const cigarIds = new Set(CIGARS.map((c) => c.id));
    const byRegion: Record<"HR" | "EU" | "USA", Set<string>> = {
      HR: new Set(),
      EU: new Set(),
      USA: new Set(),
    };
    for (const o of offers) {
      if (!cigarIds.has(o.productId)) continue;
      const region = shopRegion.get(o.shopId);
      if (region === "HR" || region === "EU" || region === "USA") {
        byRegion[region].add(o.productId);
      }
    }
    expect(byRegion.HR.size).toBeGreaterThanOrEqual(cigarCountByRegion.HR);
    expect(byRegion.EU.size).toBeGreaterThanOrEqual(cigarCountByRegion.EU);
    expect(byRegion.USA.size).toBeGreaterThanOrEqual(cigarCountByRegion.USA);
  });
});
