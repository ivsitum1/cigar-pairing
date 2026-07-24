import type { Cigar, Drink, DrinkCategory, Region, RegionFilter, Vitola } from "../types";
import { shopsForRegion, REGIONS } from "./shops";
import rums from "./rums.json";
import whiskies from "./whiskies.json";
import brandies from "./brandies.json";
import gins from "./gins.json";
import wines from "./wines.json";
import coffees from "./coffees.json";
import tequilas from "./tequilas.json";
import cigarsJson from "./cigars.json";
import shoppingJson from "./shopping.json";
import brandsJson from "./brands.json";
import cigarIdAliasesJson from "./cigarIdAliases.json";
import { resolveDefaultVitola } from "../lib/cigarVitola";

export const DRINKS: Record<DrinkCategory, Drink[]> = {
  rum: rums as unknown as Drink[],
  whisky: whiskies as unknown as Drink[],
  brandy: brandies as unknown as Drink[],
  wine: wines as unknown as Drink[],
  coffee: coffees as unknown as Drink[],
  tequila: tequilas as unknown as Drink[],
  gin: gins as unknown as Drink[],
};

function cigarRichness(c: Cigar): number {
  return (
    (c.vitolas?.length ?? 0) * 10 +
    (c.flavorTags?.length ?? 0) +
    (c.notes?.hr ? 1 : 0)
  );
}

/** Jedan zapis po id — sprječava pogrešan klik kad export ima duplikate. */
function dedupeCigars(cigars: Cigar[]): Cigar[] {
  const best = new Map<string, Cigar>();
  for (const c of cigars) {
    const prev = best.get(c.id);
    if (!prev || cigarRichness(c) > cigarRichness(prev)) {
      best.set(c.id, c);
    }
  }
  return [...best.values()].sort(
    (a, b) => a.brand.localeCompare(b.brand) || a.line.localeCompare(b.line),
  );
}

export const ALL_DRINKS: Drink[] = [
  ...DRINKS.rum,
  ...DRINKS.whisky,
  ...DRINKS.brandy,
  ...DRINKS.wine,
  ...DRINKS.coffee,
  ...DRINKS.tequila,
  ...DRINKS.gin,
];

export const CIGARS: Cigar[] = dedupeCigars(cigarsJson as Cigar[]);

export interface ShoppingTier {
  tier: string;
  owned: boolean;
  styleTarget: { hr: string; en: string };
  bottleTarget: string;
  profile: { hr: string; en: string };
  priceSource: string;
  myRating: number | null;
  notes: string;
}

export interface ShopInfo {
  name: string;
  location: string;
  note: { hr: string; en: string };
}

export interface ShoppingData {
  tiers: ShoppingTier[];
  shops: ShopInfo[];
  recommendations: {
    title: { hr: string; en: string };
    pick: string;
    detail: { hr: string; en: string };
  }[];
  miniPath: string[];
}

export const SHOPPING: ShoppingData = shoppingJson as ShoppingData;

export const drinkById = (id: string): Drink | undefined =>
  ALL_DRINKS.find((d) => d.id === id);

export const cigarById = (id: string): Cigar | undefined =>
  CIGARS.find((c) => c.id === id);

const CIGAR_ID_ALIASES: Record<string, string> =
  (cigarIdAliasesJson as { aliases?: Record<string, string> }).aliases ?? {};

/** Slug za brand / vitola deep-linkove (ASCII, kebab-case). */
export function slugifyLabel(label: string): string {
  return label
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[''`]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export const brandSlug = (brand: string): string => slugifyLabel(brand);

export const vitolaSlug = (v: Vitola | string): string =>
  slugifyLabel(typeof v === "string" ? v : v.name);

/** Prati cigarIdAliases.json do kanonskog zapisa (lanac aliasa). */
export function resolveCigarId(id: string): Cigar | undefined {
  let cur = id;
  const seen = new Set<string>();
  for (;;) {
    const hit = cigarById(cur);
    if (hit) return hit;
    if (seen.has(cur)) return undefined;
    seen.add(cur);
    const next = CIGAR_ID_ALIASES[cur];
    if (!next) return undefined;
    cur = next;
  }
}

export interface BrandInfo {
  country: string;
  founded: string;
  blurb: { hr: string; en: string };
}

const BRANDS = brandsJson as Record<string, BrandInfo>;

export const brandInfo = (brand: string): BrandInfo | undefined => BRANDS[brand];

/** Linije marke: A→Z, linija = ime marke prva (§2). */
export function linesByBrand(brand: string): Cigar[] {
  const lines = CIGARS.filter((c) => c.brand === brand);
  return [...lines].sort((a, b) => {
    const aCore = a.line === brand ? 0 : 1;
    const bCore = b.line === brand ? 0 : 1;
    if (aCore !== bCore) return aCore - bCore;
    return a.line.localeCompare(b.line);
  });
}

/** Alias za linesByBrand — postojeći importi. */
export const cigarsByBrand = (brand: string): Cigar[] => linesByBrand(brand);

// sve marke koje imaju barem jednu cigaru, sortirano
export const ALL_BRANDS: string[] = [
  ...new Set(CIGARS.map((c) => c.brand)),
].sort((a, b) => a.localeCompare(b));

const BRAND_BY_SLUG = new Map(ALL_BRANDS.map((b) => [brandSlug(b), b]));

export function brandFromSlug(slug: string): string | undefined {
  return BRAND_BY_SLUG.get(slug);
}

/** Indeks brenda za katalog / Brand Index (derivacija iz cigars + brands.json). */
export interface BrandCatalogStats {
  brand: string;
  info?: BrandInfo;
  lineCount: number;
  vitolaCount: number;
  hasAdditionalVitolas: boolean;
  minPriceEUR: number | null;
}

/** Phase 4: brand čvor s linijama (jedan zapis = jedna linija). */
export interface BrandNode {
  brand: string;
  info?: BrandInfo;
  lines: Cigar[];
  vitolaCount: number;
  minPriceEUR: number | null;
}

export function brandNode(brand: string): BrandNode {
  const lines = linesByBrand(brand);
  let vitolaCount = 0;
  let minPrice: number | null = null;
  for (const c of lines) {
    for (const v of c.vitolas ?? []) {
      vitolaCount += 1;
      if (v.priceEUR != null && (minPrice == null || v.priceEUR < minPrice)) {
        minPrice = v.priceEUR;
      }
    }
    if (c.priceEUR != null && (minPrice == null || c.priceEUR < minPrice)) {
      minPrice = c.priceEUR;
    }
  }
  return {
    brand,
    info: brandInfo(brand),
    lines,
    vitolaCount,
    minPriceEUR: minPrice,
  };
}

export const BRAND_INDEX: BrandNode[] = ALL_BRANDS.map(brandNode);

export function brandCatalogStats(brand: string): BrandCatalogStats {
  const node = brandNode(brand);
  return {
    brand: node.brand,
    info: node.info,
    lineCount: node.lines.filter((c) => c.line !== "Additional Vitolas").length,
    vitolaCount: node.vitolaCount,
    hasAdditionalVitolas: node.lines.some((c) => c.line === "Additional Vitolas"),
    minPriceEUR: node.minPriceEUR,
  };
}

export const BRAND_CATALOG: BrandCatalogStats[] = ALL_BRANDS.map(brandCatalogStats);

// Je li cigara dostupna u odabranoj regiji. "ALL" = bez filtera (sve).
export const cigarInRegion = (c: Cigar, f: RegionFilter): boolean =>
  f === "ALL" || c.markets.includes(f);

// Broj cigara dostupnih po regiji — za detaljan popis trgovina.
export const cigarCountByRegion: Record<Region, number> = {
  HR: CIGARS.filter((c) => c.markets.includes("HR")).length,
  EU: CIGARS.filter((c) => c.markets.includes("EU")).length,
  USA: CIGARS.filter((c) => c.markets.includes("USA")).length,
};

// Izravan link na proizvod za dani host — samo URL koji odgovara prikazanoj
// cijeni (zadana vitola / priceUrl / vitola iste cijene). Ne padati na
// proizvoljnu vitolu istog hosta (npr. Cubanitos umjesto Gran Reserva).
function exactProductUrl(c: Cigar, host: string): string | null {
  const dv = resolveDefaultVitola(c);
  if (dv?.url && dv.url.includes(host)) return dv.url;
  if (c.priceUrl?.includes(host)) return c.priceUrl;
  const display = dv?.priceEUR ?? c.priceEUR ?? null;
  if (display != null) {
    const samePrice = (c.vitolas ?? []).find(
      (v) =>
        v.url?.includes(host) &&
        v.priceEUR != null &&
        Math.abs(v.priceEUR - display) < 0.05,
    );
    if (samePrice?.url) return samePrice.url;
  }
  return null;
}

export interface CigarShopLink {
  region: Region;
  shop: string;
  url: string;
  exact: boolean; // true = izravan link na proizvod; false = pretraga / listing linije
}

/** Holt's /all-cigar-brands/*.html je listing linije, ne SKU jedne vitole. */
export function isLineListingUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  return /holts\.com\/cigars\/all-cigar-brands\/[^/?#]+\.html/i.test(url);
}

// Linkovi na trgovine za sve regije u kojima je cigara dostupna. HR koristi
// izravan link na proizvod gdje postoji (humidor/havana), inače pretragu;
// EU/USA: scrapani regionLinks kad postoje (listing = exact:false), inače search.
export function cigarShopLinks(c: Cigar): CigarShopLink[] {
  const q = encodeURIComponent(`${c.brand} ${c.line}`.trim());
  const out: CigarShopLink[] = [];
  for (const region of REGIONS) {
    if (!c.markets.includes(region)) continue;
    // scrapani izravan link na proizvod za EU/USA (HR ostaje na vlastitim
    // product linkovima iz vitola/priceUrl kao izvoru istine)
    const rl = region === "HR" ? undefined : c.regionLinks?.[region];
    let usedShop: string | null = null;
    if (rl?.url) {
      out.push({
        region,
        shop: rl.shop,
        url: rl.url,
        exact: !isLineListingUrl(rl.url),
      });
      usedShop = rl.shop;
    }
    for (const shop of shopsForRegion(region)) {
      if (shop.name === usedShop) continue; // vec dodan kao izravan link
      const exact = shop.productHost ? exactProductUrl(c, shop.productHost) : null;
      out.push({
        region,
        shop: shop.name,
        url: exact ?? shop.search(q),
        exact: exact != null && !isLineListingUrl(exact),
      });
    }
  }
  return out;
}

// URL primarne trgovine za odabranu regiju. Za "ALL" (ili regiju bez trgovine)
// bira HR izravni link ako postoji, pa prvo dostupno, pa Google fallback.
export function cigarLinkForMarket(c: Cigar, region: RegionFilter): string {
  const links = cigarShopLinks(c);
  if (region !== "ALL") {
    const inRegion = links.filter((l) => l.region === region);
    if (inRegion.length) return (inRegion.find((l) => l.exact) ?? inRegion[0]).url;
  }
  const hr = links.filter((l) => l.region === "HR");
  if (hr.length) return (hr.find((l) => l.exact) ?? hr[0]).url;
  if (links.length) return links[0].url;
  return `https://www.google.com/search?q=${encodeURIComponent(`${c.brand} ${c.line} cigar`)}`;
}

// Cijena SAMO kad je pouzdana (HR = humidor po vitoli). "ALL" prikazuje HR
// cijenu (jedina koju stvarno imamo). EU/USA -> null (ne izmišljamo broj).
// "fromMany" = ima više vitola s cijenama pa je ovo najniža ("od X €").
export function cigarPriceForMarket(
  c: Cigar,
  region: RegionFilter,
): { price: number | null; fromMany: boolean; approx?: boolean } {
  // EU/USA: scrapana "od" cijena na razini linije (USD->EUR nosi approx)
  if (region === "EU" || region === "USA") {
    const rl = c.regionLinks?.[region];
    if (rl?.priceEUR != null) return { price: rl.priceEUR, fromMany: false, approx: rl.priceApprox };
    return { price: null, fromMany: false };
  }
  if (region !== "HR" && region !== "ALL") return { price: null, fromMany: false };

  const defaultVitola = resolveDefaultVitola(c);
  if (defaultVitola?.priceEUR != null) {
    const priced = (c.vitolas ?? []).filter((v) => v.priceEUR != null);
    const min = priced.length ? Math.min(...priced.map((v) => v.priceEUR as number)) : defaultVitola.priceEUR;
    const max = priced.length ? Math.max(...priced.map((v) => v.priceEUR as number)) : defaultVitola.priceEUR;
    return {
      price: defaultVitola.priceEUR,
      fromMany: priced.length > 1 && max - min > 0.01,
    };
  }

  const priced = (c.vitolas ?? []).filter((v) => v.priceEUR != null);
  if (priced.length === 0) {
    return { price: c.priceEUR ?? null, fromMany: false };
  }
  const min = Math.min(...priced.map((v) => v.priceEUR as number));
  const max = Math.max(...priced.map((v) => v.priceEUR as number));
  return { price: min, fromMany: max - min > 0.01 };
}

/**
 * Cijena na gumbu "Kupnja" za konkretan shop link.
 * HR: cijena vitole na koju URL vodi (ne regionLinks.HR — često je to druga
 * vitola od one u opisu). EU/USA: regionLinks kad shop odgovara.
 */
export function cigarShopLinkPrice(
  c: Cigar,
  link: CigarShopLink,
): { price: number | null; approx?: boolean } {
  if (link.exact) {
    const vitola = (c.vitolas ?? []).find((v) => v.url === link.url);
    if (vitola?.priceEUR != null) return { price: vitola.priceEUR };
    if (c.priceUrl === link.url && c.priceEUR != null) return { price: c.priceEUR };
    if (link.region === "HR") {
      return { price: cigarPriceForMarket(c, "HR").price };
    }
  }
  // regionLinks.HR namjerno ignoriran — izvor istine za HR su vitolas/priceUrl
  if (link.region === "EU" || link.region === "USA") {
    const rl = c.regionLinks?.[link.region];
    if (rl && rl.shop === link.shop && rl.priceEUR != null) {
      return { price: rl.priceEUR, approx: rl.priceApprox };
    }
  }
  return { price: null };
}

export const formatPrice = (
  p: { min: number; max: number } | number | null | undefined,
): string => {
  if (p == null) return "—";
  if (typeof p === "number") return `${p.toFixed(0)} €`;
  if (Math.abs(p.min - p.max) < 0.01) return `${p.min.toFixed(2)} €`;
  return `${p.min.toFixed(0)}–${p.max.toFixed(0)} €`;
};
