import type { Cigar, Drink, DrinkCategory } from "../types";
import rums from "./rums.json";
import whiskies from "./whiskies.json";
import brandies from "./brandies.json";
import gins from "./gins.json";
import wines from "./wines.json";
import coffees from "./coffees.json";
import cigarsJson from "./cigars.json";
import shoppingJson from "./shopping.json";
import brandsJson from "./brands.json";

export const DRINKS: Record<DrinkCategory, Drink[]> = {
  rum: rums as unknown as Drink[],
  whisky: whiskies as unknown as Drink[],
  brandy: brandies as unknown as Drink[],
  gin: gins as unknown as Drink[],
  wine: wines as unknown as Drink[],
  coffee: coffees as unknown as Drink[],
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
  ...DRINKS.gin,
  ...DRINKS.wine,
  ...DRINKS.coffee,
];

export const CIGARS: Cigar[] = dedupeCigars(cigarsJson as Cigar[]);

export interface ShoppingTier {
  tier: string;
  owned: boolean;
  styleTarget: string;
  bottleTarget: string;
  profile: string;
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

// linkovi za kupnju po tržištu — HR izravno (humidor/havana), EU cigarworld.de,
// USA/Svijet pouzdana pretraga (trgovine blokiraju izravne bot-provjere URL-ova)
export function cigarMarketLinks(c: Cigar): { market: string; url: string }[] {
  const q = encodeURIComponent(`${c.brand} ${c.line}`);
  const links: { market: string; url: string }[] = [];
  if (c.markets.includes("HR") && c.priceUrl) {
    links.push({ market: "HR", url: c.priceUrl });
  }
  if (c.markets.includes("EU")) {
    links.push({ market: "EU", url: `https://www.cigarworld.de/search?q=${q}` });
  }
  if (c.markets.includes("USA")) {
    links.push({
      market: "USA",
      url: `https://www.google.com/search?q=site%3Acigarsinternational.com+${q}`,
    });
  }
  links.push({
    market: "WW",
    url: `https://www.google.com/search?q=${q}+cigar+buy+online`,
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
