// Zaliha na polici trgovine — odvojena od cijene. `fetchedAt` na cijenama
// ostaje kvartalni scrape; `stockFetchedAt` je tjedni ping poznatog URL-a.
// Ako inStock nedostaje, UI ne tvrdi ništa.
import type { Cigar, Drink } from "../types";
import { verifiedProductUrl } from "./drinkShopLinks";

export const STOCK_STALE_DAYS = 14;

export interface StockView {
  inStock: boolean;
  stale: boolean;
  fetchedAt: string;
}

export interface StockFields {
  inStock?: boolean;
  stockFetchedAt?: string;
}

export function urlsMatch(a: string | null | undefined, b: string): boolean {
  if (!a) return false;
  return normalizeShopUrl(a) === normalizeShopUrl(b);
}

function normalizeShopUrl(url: string): string {
  return url.replace(/#.*$/, "").replace(/\/+$/, "").toLowerCase();
}

export function isStockStale(stockFetchedAt: string, now = Date.now()): boolean {
  const then = Date.parse(`${stockFetchedAt}T00:00:00Z`);
  if (Number.isNaN(then)) return false;
  return now - then > STOCK_STALE_DAYS * 24 * 60 * 60 * 1000;
}

export function stockView(
  inStock: boolean | undefined,
  stockFetchedAt: string | undefined,
  now = Date.now(),
): StockView | null {
  if (inStock !== true && inStock !== false) return null;
  if (!stockFetchedAt) return null;
  return {
    inStock,
    stale: isStockStale(stockFetchedAt, now),
    fetchedAt: stockFetchedAt,
  };
}

function fromFields(obj: StockFields | undefined): StockFields | null {
  if (!obj) return null;
  if (obj.inStock !== true && obj.inStock !== false) return null;
  if (!obj.stockFetchedAt) return null;
  return { inStock: obj.inStock, stockFetchedAt: obj.stockFetchedAt };
}

/** Stock ping attached to this exact product URL, or null if never pinged. */
export function cigarLinkStock(c: Cigar, url: string): StockFields | null {
  if (fromFields(c) && urlsMatch(c.priceUrl, url)) return fromFields(c);
  for (const region of ["HR", "EU", "USA"] as const) {
    const hit = fromFields(c.regionLinks?.[region]);
    if (hit && urlsMatch(c.regionLinks?.[region]?.url, url)) return hit;
  }
  for (const v of c.vitolas ?? []) {
    const own = fromFields(v);
    if (own && urlsMatch(v.url, url)) return own;
    for (const region of ["HR", "EU", "USA"] as const) {
      const link = v.regionLinks?.[region];
      const hit = fromFields(link);
      if (hit && urlsMatch(link?.url, url)) return hit;
    }
  }
  return null;
}

export function cigarLinkStockView(
  c: Cigar,
  url: string,
  kind: "product" | "line" | "walkin" | "search",
  now = Date.now(),
): StockView | null {
  if (kind !== "product") return null;
  const fields = cigarLinkStock(c, url);
  if (!fields) return null;
  return stockView(fields.inStock, fields.stockFetchedAt, now);
}

export function drinkStockView(d: Drink, now = Date.now()): StockView | null {
  if (!verifiedProductUrl(d)) return null;
  return stockView(d.inStock, d.stockFetchedAt, now);
}
