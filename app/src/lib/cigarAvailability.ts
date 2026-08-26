// Dokaz da je cigara u katalogu trgovine (ne samo markets deklaracija)
// i zasebno stanje police (inStock ping). Filter gleda dokaz; out-of-stock
// ostaje vidljiv.
import type { Cigar, Region, RegionFilter } from "../types";
import { isLineListingUrl, shopsForRegion } from "../data/shops";
import { cigarLinkStock } from "./shopStock";

export type CatalogProof = "product" | "line" | "walkin" | "none";
export type ShelfStatus = "in_stock" | "out_of_stock" | "unknown";

/** Svi URL-ovi koji pripadaju regiji (linija, vitole, priceUrl, sourceUrls). */
function urlsForRegion(c: Cigar, region: Region): string[] {
  const out: string[] = [];
  const push = (u: string | null | undefined) => {
    if (u) out.push(u);
  };
  push(c.regionLinks?.[region]?.url);
  push(region === "HR" ? c.priceUrl : undefined);
  for (const v of c.vitolas ?? []) {
    push(v.regionLinks?.[region]?.url);
    if (region === "HR") push(v.url);
  }
  for (const u of c.sourceUrls ?? []) push(u);
  return out;
}

function hostsForRegion(region: Region): string[] {
  return shopsForRegion(region)
    .map((s) => s.productHost)
    .filter((h): h is string => Boolean(h));
}

function urlMatchesRegionHost(url: string, region: Region): boolean {
  const hosts = hostsForRegion(region);
  if (hosts.some((h) => url.includes(h))) return true;
  // Holt's nema productHost — regionLinks.USA često vodi na holts.com
  if (region === "USA" && /holts\.com/i.test(url)) return true;
  return false;
}

function classifyUrl(url: string): "product" | "line" {
  return isLineListingUrl(url) ? "line" : "product";
}

/**
 * Najjači dokaz da cigara postoji u katalogu trgovine te regije.
 * product > line > walkin > none. Search URL nije dokaz.
 */
export function cigarCatalogProof(c: Cigar, region: Region): CatalogProof {
  let best: CatalogProof = "none";
  const raise = (p: CatalogProof) => {
    const rank = { none: 0, walkin: 1, line: 2, product: 3 } as const;
    if (rank[p] > rank[best]) best = p;
  };

  if (region === "HR") {
    const hrShops = shopsForRegion("HR");
    const onlineNames = new Set(
      hrShops.filter((s) => !s.walkIn).map((s) => s.name),
    );
    const walkInNames = new Set(
      hrShops.filter((s) => s.walkIn).map((s) => s.name),
    );
    for (const name of c.availabilityHR ?? []) {
      if (onlineNames.has(name)) raise("product");
      else if (walkInNames.has(name)) raise("walkin");
    }
  }

  for (const url of urlsForRegion(c, region)) {
    if (!urlMatchesRegionHost(url, region)) continue;
    raise(classifyUrl(url));
  }

  // regionLinks shop bez host matcha (npr. samo holts listing već pokriven)
  const rl = c.regionLinks?.[region];
  if (rl?.url && urlMatchesRegionHost(rl.url, region)) {
    raise(classifyUrl(rl.url));
  }

  return best;
}

/** Product URL-ovi u regiji pogodni za stock ping (ne listing). */
function productUrlsInRegion(c: Cigar, region: Region): string[] {
  const urls: string[] = [];
  for (const url of urlsForRegion(c, region)) {
    if (!urlMatchesRegionHost(url, region)) continue;
    if (isLineListingUrl(url)) continue;
    urls.push(url);
  }
  return [...new Set(urls)];
}

export function cigarShelfStatus(c: Cigar, region: Region): ShelfStatus {
  let sawOut = false;
  for (const url of productUrlsInRegion(c, region)) {
    const fields = cigarLinkStock(c, url);
    if (!fields) continue;
    if (fields.inStock === true) return "in_stock";
    if (fields.inStock === false) sawOut = true;
  }
  return sawOut ? "out_of_stock" : "unknown";
}

/** UI filter: ALL = sve; inače samo cigare s dokazom u toj regiji. */
export function cigarAvailableInRegion(
  c: Cigar,
  market: RegionFilter,
): boolean {
  if (market === "ALL") return true;
  return cigarCatalogProof(c, market) !== "none";
}
