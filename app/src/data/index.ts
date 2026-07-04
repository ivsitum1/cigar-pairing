import type { Cigar, Drink, DrinkCategory } from "../types";
import rums from "./rums.json";
import whiskies from "./whiskies.json";
import brandies from "./brandies.json";
import gins from "./gins.json";
import coffees from "./coffees.json";
import cigarsJson from "./cigars.json";
import shoppingJson from "./shopping.json";

export const DRINKS: Record<DrinkCategory, Drink[]> = {
  rum: rums as unknown as Drink[],
  whisky: whiskies as unknown as Drink[],
  brandy: brandies as unknown as Drink[],
  gin: gins as unknown as Drink[],
  coffee: coffees as unknown as Drink[],
};

export const ALL_DRINKS: Drink[] = [
  ...DRINKS.rum,
  ...DRINKS.whisky,
  ...DRINKS.brandy,
  ...DRINKS.gin,
  ...DRINKS.coffee,
];

export const CIGARS: Cigar[] = cigarsJson as Cigar[];

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

export const formatPrice = (
  p: { min: number; max: number } | number | null | undefined,
): string => {
  if (p == null) return "—";
  if (typeof p === "number") return `${p.toFixed(0)} €`;
  if (Math.abs(p.min - p.max) < 0.01) return `${p.min.toFixed(2)} €`;
  return `${p.min.toFixed(0)}–${p.max.toFixed(0)} €`;
};
