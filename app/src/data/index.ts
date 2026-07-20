import type { Cigar, Drink, DrinkCategory } from "../types";
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

export interface BrandInfo {
  country: string;
  founded: string;
  blurb: { hr: string; en: string };
}

const BRANDS = brandsJson as Record<string, BrandInfo>;

export const brandInfo = (brand: string): BrandInfo | undefined => BRANDS[brand];

export const cigarsByBrand = (brand: string): Cigar[] =>
  CIGARS.filter((c) => c.brand === brand);

// sve marke koje imaju barem jednu cigaru, sortirano
export const ALL_BRANDS: string[] = [
  ...new Set(CIGARS.map((c) => c.brand)),
].sort((a, b) => a.localeCompare(b));

/** Indeks brenda za katalog / Brand Index (derivacija iz cigars + brands.json). */
export interface BrandCatalogStats {
  brand: string;
  info?: BrandInfo;
  lineCount: number;
  vitolaCount: number;
  hasAdditionalVitolas: boolean;
  minPriceEUR: number | null;
}

export function brandCatalogStats(brand: string): BrandCatalogStats {
  const lines = cigarsByBrand(brand);
  let vitolaCount = 0;
  let minPrice: number | null = null;
  let hasAdditional = false;
  for (const c of lines) {
    if (c.line === "Additional Vitolas") hasAdditional = true;
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
    lineCount: lines.filter((c) => c.line !== "Additional Vitolas").length,
    vitolaCount,
    hasAdditionalVitolas: hasAdditional,
    minPriceEUR: minPrice,
  };
}

export const BRAND_CATALOG: BrandCatalogStats[] = ALL_BRANDS.map(brandCatalogStats);

// linkovi za kupnju po tržištu — HR izravno (humidor/havana), EU cigarworld.de,
// USA izravna pretraga US trgovine (Google site:ci… često 0 pogodaka),
// WW otvorena Google pretraga bez site: ograničenja
export function cigarMarketLinks(c: Cigar): { market: string; url: string }[] {
  const label = `${c.brand} ${c.line}`.trim();
  const q = encodeURIComponent(label);
  const links: { market: string; url: string }[] = [];
  const defaultVitola = resolveDefaultVitola(c);
  const hrUrl = defaultVitola?.url ?? c.priceUrl;
  if (c.markets.includes("HR") && hrUrl) {
    links.push({ market: "HR", url: hrUrl });
  }
  if (c.markets.includes("EU")) {
    links.push({ market: "EU", url: `https://www.cigarworld.de/search?q=${q}` });
  }
  if (c.markets.includes("USA")) {
    // Famous Smoke prihvaća search URL iz EU; CI često blokira / GDPR redirect
    links.push({
      market: "USA",
      url: `https://www.famous-smoke.com/search?q=${q}`,
    });
  }
  links.push({
    market: "WW",
    url: `https://www.google.com/search?q=${encodeURIComponent(`${label} cigar buy online`)}`,
  });
  return links;
}

// URL trgovine za odabrano tržište (za taj market, ne bilo koji)
export function cigarLinkForMarket(c: Cigar, market: string): string {
  const links = cigarMarketLinks(c);
  return (links.find((l) => l.market === market) ?? links[links.length - 1]).url;
}

// Cijena SAMO kad je pouzdana za odabrano tržište (HR = humidor po vitoli).
// Za EU/USA/WW nemamo scrape cijenu -> vraćamo null (ne izmišljamo broj).
// "fromMany" = ima više vitola s cijenama pa je ovo najniža ("od X €").
export function cigarPriceForMarket(
  c: Cigar,
  market: string,
): { price: number | null; fromMany: boolean } {
  if (market !== "HR") return { price: null, fromMany: false };

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

export const formatPrice = (
  p: { min: number; max: number } | number | null | undefined,
): string => {
  if (p == null) return "—";
  if (typeof p === "number") return `${p.toFixed(0)} €`;
  if (Math.abs(p.min - p.max) < 0.01) return `${p.min.toFixed(2)} €`;
  return `${p.min.toFixed(0)}–${p.max.toFixed(0)} €`;
};
