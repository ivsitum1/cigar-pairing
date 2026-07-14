// Preporuke za kupovinu — racunaju se iz indeksa, ne iz staticnog Excela.
// Segmenti (bucketi stilova) po kategoriji + tri vrste preporuka po kategoriji
// + "buffet petorka": 5 boca koje pokrivaju cijeli spektar kategorije
// + rupe u kolekciji: segmenti u kojima korisnik jos nema nijednu bocu.

import type { Drink, DrinkCategory, LocalizedText } from "../types";

export interface StyleBucket {
  id: string;
  label: LocalizedText;
  styles: string[];
}

export const BUCKETS: Partial<Record<DrinkCategory, StyleBucket[]>> = {
  rum: [
    { id: "clean", label: { hr: "Čisti klasik", en: "Clean classic" }, styles: ["barbados", "blend", "trinidad", "puerto-rico", "dominican", "st-lucia", "cuba", "nicaragua-dry", "colombia", "mixing"] },
    { id: "jamaica", label: { hr: "Jamajka / esteri", en: "Jamaica / esters" }, styles: ["jamaica"] },
    { id: "agricole", label: { hr: "Agricole", en: "Agricole" }, styles: ["agricole"] },
    { id: "rich", label: { hr: "Bogati / tamni", en: "Rich / dark" }, styles: ["demerara", "solera", "venezuela", "panama", "navy", "other"] },
    { id: "dessert", label: { hr: "Desertni / spiced", en: "Dessert / spiced" }, styles: ["spiced", "liqueur"] },
  ],
  whisky: [
    { id: "scotch", label: { hr: "Scotch (sherry / voćni)", en: "Scotch (sherry / fruity)" }, styles: ["speyside-sherry", "speyside-fruity", "highland", "lowland", "blended-scotch"] },
    { id: "peat", label: { hr: "Treset / otoci", en: "Peat / islands" }, styles: ["islay-peated", "island", "campbeltown"] },
    { id: "america", label: { hr: "Bourbon / rye", en: "Bourbon / rye" }, styles: ["bourbon", "tennessee", "rye"] },
    { id: "irish", label: { hr: "Irska", en: "Ireland" }, styles: ["irish-pot-still", "irish-blend", "irish-single-malt"] },
    { id: "world", label: { hr: "Japan / svijet", en: "Japan / world" }, styles: ["japanese", "world", "liqueur"] },
  ],
  brandy: [
    { id: "cognac", label: { hr: "Cognac", en: "Cognac" }, styles: ["cognac-vs", "cognac-vsop", "cognac-xo"] },
    { id: "armagnac", label: { hr: "Armagnac / Calvados", en: "Armagnac / Calvados" }, styles: ["armagnac", "calvados"] },
    { id: "spain", label: { hr: "Španjolska", en: "Spain" }, styles: ["brandy-de-jerez", "brandy-spanish"] },
    { id: "mediteran", label: { hr: "Grappa / mediteran", en: "Grappa / Mediterranean" }, styles: ["grappa", "brandy-italian", "brandy-greek", "vinjak", "brandy-armenian", "brandy-german"] },
    { id: "liqueur", label: { hr: "Liker", en: "Liqueur" }, styles: ["liqueur"] },
  ],
  gin: [
    { id: "london", label: { hr: "London Dry", en: "London Dry" }, styles: ["london-dry"] },
    { id: "premium", label: { hr: "Premium dry", en: "Premium dry" }, styles: ["premium-dry"] },
    { id: "plymouth", label: { hr: "Plymouth / meki stil", en: "Plymouth / soft style" }, styles: ["plymouth", "navy-strength", "old-tom", "genever"] },
    { id: "contemporary", label: { hr: "Contemporary", en: "Contemporary" }, styles: ["contemporary"] },
    { id: "croatian", label: { hr: "HR craft", en: "Croatian craft" }, styles: ["croatian"] },
  ],
  wine: [
    { id: "port", label: { hr: "Porto / fortificirano", en: "Port / fortified" }, styles: ["port-ruby", "port-tawny", "madeira", "prosek"] },
    { id: "sherry", label: { hr: "Sherry", en: "Sherry" }, styles: ["sherry-dry", "sherry-sweet"] },
    { id: "red", label: { hr: "Crno", en: "Red" }, styles: ["red-full", "red-medium"] },
    { id: "white", label: { hr: "Bijelo / pjenušavo", en: "White / sparkling" }, styles: ["white-fresh", "white-rich", "sparkling"] },
    { id: "dessert", label: { hr: "Desertno", en: "Dessert" }, styles: ["dessert-wine"] },
  ],
};

const price = (d: Drink): number | null => d.priceEUR?.min ?? null;

const byQuality = (a: Drink, b: Drink) =>
  (b.qualityScore ?? 0) - (a.qualityScore ?? 0) ||
  (price(a) ?? 9999) - (price(b) ?? 9999);

/** Vrijednost = kvaliteta uz blagu kaznu za cijenu (25 EUR ~ 0.5 boda). */
const valueScore = (d: Drink) =>
  (d.qualityScore ?? 0) - (price(d) ?? 100) * 0.02;

export interface SegmentPicks {
  top: Drink | null;
  value: Drink | null;
  budget: Drink | null;
}

/** Tri preporuke za kategoriju: vrh ponude, najbolji omjer, pristupacno (<=30 EUR). */
export function segmentPicks(drinks: Drink[], isOwned: (id: string) => boolean): SegmentPicks {
  const pool = drinks.filter((d) => d.pairable && !isOwned(d.id));
  const top = [...pool].sort(byQuality)[0] ?? null;
  const priced = pool.filter((d) => price(d) != null);
  const value =
    [...priced].sort((a, b) => valueScore(b) - valueScore(a)).find((d) => d.id !== top?.id) ?? null;
  const budget =
    [...priced]
      .filter((d) => (price(d) as number) <= 30)
      .sort(byQuality)
      .find((d) => d.id !== top?.id && d.id !== value?.id) ?? null;
  return { top, value, budget };
}

/** Buffet petorka: iz svakog segmenta kategorije po jedna boca (najbolji omjer). */
export function buffetFive(
  category: DrinkCategory,
  drinks: Drink[],
  isOwned: (id: string) => boolean,
): { bucket: StyleBucket; drink: Drink }[] {
  const buckets = BUCKETS[category] ?? [];
  const used = new Set<string>();
  const out: { bucket: StyleBucket; drink: Drink }[] = [];
  for (const bucket of buckets) {
    const pick = drinks
      .filter(
        (d) =>
          d.pairable &&
          bucket.styles.includes(d.style) &&
          !isOwned(d.id) &&
          !used.has(d.id),
      )
      .sort((a, b) => valueScore(b) - valueScore(a))[0];
    if (pick) {
      used.add(pick.id);
      out.push({ bucket, drink: pick });
    }
  }
  return out;
}

export const buffetTotal = (picks: { drink: Drink }[]): number =>
  picks.reduce((s, p) => s + (price(p.drink) ?? 0), 0);

/**
 * Rupe u kolekciji: segmenti kategorije u kojima korisnik NEMA nijednu bocu,
 * s po jednom preporukom (najbolji omjer) za popuniti rupu. Zivi "moj plan".
 */
export function collectionGaps(
  category: DrinkCategory,
  drinks: Drink[],
  isOwned: (id: string) => boolean,
): { bucket: StyleBucket; suggestion: Drink | null }[] {
  const buckets = BUCKETS[category] ?? [];
  return buckets
    .filter((b) => !drinks.some((d) => b.styles.includes(d.style) && isOwned(d.id)))
    .map((bucket) => ({
      bucket,
      suggestion:
        drinks
          .filter((d) => d.pairable && bucket.styles.includes(d.style) && !isOwned(d.id))
          .sort((a, b) => valueScore(b) - valueScore(a))[0] ?? null,
    }));
}

/** Tekst liste zelja za kopiranje/share — ponijeti u ducan. */
export function wishlistText(
  items: { name: string; price: number | null; shop?: string }[],
): string {
  const lines = items.map(
    (it) =>
      `• ${it.name}${it.price != null ? ` — ~${it.price.toFixed(0)} €` : ""}${it.shop ? ` (${it.shop})` : ""}`,
  );
  const total = items.reduce((s, it) => s + (it.price ?? 0), 0);
  return [...lines, `Ukupno: ~${total.toFixed(0)} €`].join("\n");
}
