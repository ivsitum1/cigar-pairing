import type { Cigar, Drink, DrinkCategory, Region, RegionFilter, Vitola } from "../types";
import { shopsForRegion, REGIONS } from "./shops";
import rums from "./rums.json";
import whiskies from "./whiskies.json";
import brandies from "./brandies.json";
import gins from "./gins.json";
import wines from "./wines.json";
import coffees from "./coffees.json";
import tequilas from "./tequilas.json";
import digestifs from "./digestifs.json";
import cigarsJson from "./cigars.json";
import shoppingJson from "./shopping.json";
import brandsJson from "./brands.json";
import cigarIdAliasesJson from "./cigarIdAliases.json";
import drinkIdAliasesJson from "./drinkIdAliases.json";
import drinkBrandsJson from "./drinkBrands.json";
import { applyVitola, resolveDefaultVitola, uniqueVitolas } from "../lib/cigarVitola";
import { cigarLinePrice, vitolaPriceForMarket } from "../lib/cigarPrice";
import {
  cigarItemId,
  parseCigarItemId,
  vitolaFromItemId,
  VITOLA_ID_SEP,
} from "../lib/cigarItemId";

export const DRINKS: Record<DrinkCategory, Drink[]> = {
  rum: rums as unknown as Drink[],
  whisky: whiskies as unknown as Drink[],
  brandy: brandies as unknown as Drink[],
  wine: wines as unknown as Drink[],
  coffee: coffees as unknown as Drink[],
  tequila: tequilas as unknown as Drink[],
  gin: gins as unknown as Drink[],
  digestif: digestifs as unknown as Drink[],
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
  ...DRINKS.digestif,
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

const DRINK_ID_ALIASES: Record<string, string> =
  (drinkIdAliasesJson as { aliases?: Record<string, string> }).aliases ?? {};

const drinkByExactId = (id: string): Drink | undefined =>
  ALL_DRINKS.find((d) => d.id === id);

/**
 * Piće iza ID-a, uz praćenje `drinkIdAliases.json` do kanonskog zapisa.
 * Kad se kombinirani unos razdvoji ili preimenuje, stari ID i dalje razriješi —
 * inače korisnikova oznaka Imam/ocjena/bilješka i zapis u dnevniku ostanu
 * sirotčad (nevidljivi u Kolekciji, goli ID u dnevniku).
 */
export const drinkById = (id: string | null | undefined): Drink | undefined => {
  if (id == null || id === "") return undefined;
  let cur = id;
  const seen = new Set<string>();
  for (;;) {
    const hit = drinkByExactId(cur);
    if (hit) return hit;
    if (seen.has(cur)) return undefined; // ciklus u aliasima
    seen.add(cur);
    const next = DRINK_ID_ALIASES[cur];
    if (!next) return undefined;
    cur = next;
  }
};

/**
 * Marka pića. Pića nemaju `brand` polje — marka živi unutar `name`, pa je
 * izvedena skriptom (`scripts/derive-drink-brands.py`) u `drinkBrands.json`.
 * Kava je namjerno izostavljena: „Ristretto" i „Cold brew" nisu marke.
 */
const DRINK_BRANDS: Record<string, string> =
  (drinkBrandsJson as { brands?: Record<string, string> }).brands ?? {};

export const drinkBrand = (id: string): string | undefined => DRINK_BRANDS[id];

/** Sve marke pića, abecedno — za filter i pregled po marki. */
export const ALL_DRINK_BRANDS: string[] = [
  ...new Set(Object.values(DRINK_BRANDS)),
].sort((a, b) => a.localeCompare(b));

// Indeks marka → boce. Pregled po marki iscrta stotine kartica odjednom, a
// linearno pretraživanje po svakoj marki bilo bi 390 × 930 usporedbi po renderu.
const DRINKS_BY_BRAND: Map<string, Drink[]> = (() => {
  const m = new Map<string, Drink[]>();
  for (const d of ALL_DRINKS) {
    const brand = DRINK_BRANDS[d.id];
    if (!brand) continue;
    const list = m.get(brand);
    if (list) list.push(d);
    else m.set(brand, [d]);
  }
  for (const list of m.values()) {
    list.sort(
      (a, b) =>
        (b.qualityScore ?? 0) - (a.qualityScore ?? 0) || a.name.localeCompare(b.name),
    );
  }
  return m;
})();

/** Boce jedne marke, najbolje ocijenjene prvo pa abecedno. Kopija — pozivatelji sortiraju. */
export function drinksByBrand(brand: string): Drink[] {
  const list = DRINKS_BY_BRAND.get(brand);
  return list ? [...list] : [];
}

export const cigarById = (id: string): Cigar | undefined =>
  CIGARS.find((c) => c.id === id);

/**
 * Cigara iza ključa kolekcije/dnevnika. Ključ smije nositi vitolu
 * (`cig-x@churchill`) — tada se vraća linija s primijenjenom tom vitolom, pa
 * prikaz (format, cijena, vrijeme) odgovara baš onome što je korisnik označio.
 */
export function cigarForItemId(itemId: string): Cigar | undefined {
  const direct = resolveCigarId(itemId);
  if (direct) return direct;
  const { cigarId } = parseCigarItemId(itemId);
  if (cigarId === itemId) return undefined;
  const line = resolveCigarId(cigarId);
  if (!line) return undefined;
  const vitola = vitolaFromItemId(line, itemId);
  return vitola ? applyVitola(line, vitola) : line;
}

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

/**
 * Prati alias lanac do kanonskog string id-a (i kad zapis još nije u katalogu).
 * Pića i nepoznati ključevi ostaju netaknuti.
 */
export function resolveCigarIdAlias(id: string): string {
  let cur = id;
  const seen = new Set<string>();
  while (CIGAR_ID_ALIASES[cur] && !seen.has(cur)) {
    seen.add(cur);
    cur = CIGAR_ID_ALIASES[cur];
  }
  return cur;
}

/**
 * Kanonski ključ stavke kolekcije/humidora: alias linije → live id,
 * vitola-sufiks se zadržava (`alias@torpedo` → `canon@torpedo`).
 */
export function canonicalCigarItemId(itemId: string): string {
  const { cigarId, vitolaSlug } = parseCigarItemId(itemId);
  const canon = resolveCigarIdAlias(cigarId);
  return vitolaSlug ? `${canon}${VITOLA_ID_SEP}${vitolaSlug}` : canon;
}

/**
 * Ključ stanja kolekcije/humidora koji sučelje stvarno može pročitati i
 * prepisati. Kartica cigare radi po `cigarItemId(cigarForItemId(key))`, pa
 * svaki ključ koji ne preživi taj krug postaje sirotan zapis: vidi se na
 * popisu Kolekcije, ali nijedan gumb ga ne dira (npr. `cig-x@torpedo` nakon
 * što je Torpedo izbačen iz linije, ili `cig-x@robusto` kad je liniji ostala
 * samo jedna vitola). Ovdje se takav ključ vraća na ono što kartica piše.
 *
 * Nepoznata cigara ostaje netaknuta — migracija ne briše ono što ne razumije.
 */
export function canonicalCigarStateKey(itemId: string): string {
  const canon = canonicalCigarItemId(itemId);
  const cigar = cigarForItemId(canon);
  return cigar ? cigarItemId(cigar) : canon;
}

/**
 * Kanonski ID pića: prati `drinkIdAliases.json` do živog zapisa.
 * Nepoznat ID vraća se nepromijenjen — migracija ne smije brisati ono što
 * ne razumije (možda je piće privremeno izvan kataloga).
 */
export function canonicalDrinkId(id: string): string {
  let cur = id;
  const seen = new Set<string>();
  while (!drinkByExactId(cur)) {
    if (seen.has(cur)) return id; // ciklus — ostavi kako je bilo
    seen.add(cur);
    const next = DRINK_ID_ALIASES[cur];
    if (!next) return id;
    cur = next;
  }
  return cur;
}

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
  /** Market-specific display name (e.g. La Aroma de Cuba → del Caribe in HR/EU). */
  displayNames?: Partial<Record<"HR" | "EU" | "USA", string>>;
}

const BRANDS = brandsJson as Record<string, BrandInfo>;

export const brandInfo = (brand: string): BrandInfo | undefined => BRANDS[brand];

/** Canonical brand key stays in data; UI may show a market alias. */
export function brandDisplayName(
  brand: string,
  market: RegionFilter,
): string {
  if (market === "ALL") return brand;
  const alias = brandInfo(brand)?.displayNames?.[market];
  return alias ?? brand;
}

/** Haystack for catalog/pairing search: canonical name + all display aliases. */
export function brandSearchHaystack(brand: string): string {
  const info = brandInfo(brand);
  const aliases = info?.displayNames
    ? Object.values(info.displayNames).filter(Boolean)
    : [];
  return [brand, ...aliases].join(" ");
}

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

/**
 * Indeks marke pića — isti obrazac kao BRAND_CATALOG za cigare, samo izveden
 * iz imena (pića nemaju `brand` polje). Kuće s više kategorija (Nikka: whisky
 * + gin) namjerno su jedna marka, pa `categories` zna imati više članova.
 */
export interface DrinkBrandStats {
  brand: string;
  slug: string;
  count: number;
  categories: DrinkCategory[];
  countries: string[];
  minPriceEUR: number | null;
  bestQuality: number | null;
}

export function drinkBrandStats(brand: string): DrinkBrandStats {
  const bottles = drinksByBrand(brand);
  const categories: DrinkCategory[] = [];
  const countries: string[] = [];
  let minPrice: number | null = null;
  let best: number | null = null;
  for (const d of bottles) {
    if (!categories.includes(d.category)) categories.push(d.category);
    const origin = d.country ?? d.region;
    if (origin && !countries.includes(origin)) countries.push(origin);
    if (d.priceEUR && (minPrice == null || d.priceEUR.min < minPrice)) {
      minPrice = d.priceEUR.min;
    }
    if (d.qualityScore != null && (best == null || d.qualityScore > best)) {
      best = d.qualityScore;
    }
  }
  return {
    brand,
    slug: slugifyLabel(brand),
    count: bottles.length,
    categories,
    countries,
    minPriceEUR: minPrice,
    bestQuality: best,
  };
}

export const DRINK_BRAND_CATALOG: DrinkBrandStats[] =
  ALL_DRINK_BRANDS.map(drinkBrandStats);

// Slug je izveden iz imena, pa se dvije marke mogu preslikati u isti slug
// ("Bowmore" i "Bowmoré" hipotetski). Prva pobjeđuje i to je stabilno jer je
// ALL_DRINK_BRANDS abecedan; test čuva da kolizija ne prođe nezapaženo.
const DRINK_BRAND_BY_SLUG = new Map<string, string>();
for (const b of DRINK_BRAND_CATALOG) {
  if (!DRINK_BRAND_BY_SLUG.has(b.slug)) DRINK_BRAND_BY_SLUG.set(b.slug, b.brand);
}

export const drinkBrandSlug = (brand: string): string => slugifyLabel(brand);

export function drinkBrandFromSlug(slug: string): string | undefined {
  return DRINK_BRAND_BY_SLUG.get(slug);
}

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
function exactProductUrl(c: Cigar, host: string, region: Region): string | null {
  const dv = resolveDefaultVitola(c);
  if (dv?.url && dv.url.includes(host) && !isLineListingUrl(dv.url)) return dv.url;
  if (c.priceUrl?.includes(host) && !isLineListingUrl(c.priceUrl)) return c.priceUrl;
  const display = cigarLinePrice(c, region).price;
  if (display != null) {
    const samePrice = (c.vitolas ?? []).find((v) => {
      if (!v.url?.includes(host) || isLineListingUrl(v.url)) return false;
      const p = vitolaPriceForMarket(v, region).price;
      return p != null && Math.abs(p - display) < 0.05;
    });
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

/**
 * Listing / brand pages — not a single product SKU.
 * Holt's /all-cigar-brands/*.html, Havana /product-brand/*, Famous /brand(s|group)/,
 * Neptune /cigar/ (line index; products live under /cigars/).
 */
export function isLineListingUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  return (
    /holts\.com\/cigars\/all-cigar-brands\/[^/?#]+\.html/i.test(url) ||
    /\/(?:en\/)?product-brand\//i.test(url) ||
    /famous-smoke\.com\/brands?\//i.test(url) ||
    /famous-smoke\.com\/brandgroup\//i.test(url) ||
    /neptunecigar\.com\/cigar\//i.test(url)
  );
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
      // fizicki ducan bez kataloga: nema smisla nuditi "pretragu" po proizvodu —
      // dostupnost se deklarira preko `availabilityHR`
      if (shop.walkIn) continue;
      const exact = shop.productHost ? exactProductUrl(c, shop.productHost, region) : null;
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

export interface ResolvedPrice {
  price: number | null;
  fromMany: boolean;
  approx?: boolean;
  /** ISO YYYY-MM-DD date when this price was scraped. Absent when unknown. */
  fetchedAt?: string;
}

/**
 * Cijena linije za odabrano tržište — tanki omotač oko `cigarLinePrice`
 * (lib/cigarPrice.ts). "fromMany" = prikazani broj je najniži u liniji.
 * `fetchedAt` dolazi s najjeftinije vitole / regionLinka koji nosi taj broj.
 */
export function cigarPriceForMarket(c: Cigar, region: RegionFilter): ResolvedPrice {
  const p = cigarLinePrice(c, region);
  if (p.price == null) return { price: null, fromMany: false };

  let fetchedAt: string | undefined;
  if (p.region === "HR" || region === "HR" || region === "ALL") {
    const priced = uniqueVitolas(c)
      .map((v) => ({ v, r: vitolaPriceForMarket(v, region) }))
      .filter((x) => x.r.price === p.price);
    const hit = priced[0]?.v;
    if (hit?.fetchedAt) fetchedAt = hit.fetchedAt;
    else if (hit?.regionLinks?.HR?.fetchedAt) fetchedAt = hit.regionLinks.HR.fetchedAt;
  }
  if (!fetchedAt && p.region && (p.region === "EU" || p.region === "USA")) {
    fetchedAt = c.regionLinks?.[p.region]?.fetchedAt;
  }
  return { price: p.price, fromMany: p.from, approx: p.approx, fetchedAt };
}

/**
 * Najnoviji `fetchedAt` datum koji postoji u cijenama cigare (vitole i regionLinks).
 * Koristi se za prikaz oznake svježine u UI-u.
 */
export function cigarLatestFetchedAt(c: Cigar): string | undefined {
  const dates: string[] = [];
  for (const region of ["HR", "EU", "USA"] as const) {
    const rl = c.regionLinks?.[region];
    if (rl?.priceEUR != null && rl.fetchedAt) dates.push(rl.fetchedAt);
  }
  for (const v of c.vitolas ?? []) {
    if (v.priceEUR != null && v.fetchedAt) dates.push(v.fetchedAt);
    for (const region of ["HR", "EU", "USA"] as const) {
      const rl = v.regionLinks?.[region];
      if (rl?.priceEUR != null && rl.fetchedAt) dates.push(rl.fetchedAt);
    }
  }
  if (!dates.length) return undefined;
  return [...dates].sort().at(-1);
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
    const byUrl = (c.vitolas ?? []).find(
      (v) => v.url === link.url || v.regionLinks?.[link.region]?.url === link.url,
    );
    if (byUrl) {
      const p = vitolaPriceForMarket(byUrl, link.region);
      if (p.price != null) return { price: p.price, approx: p.approx };
    }
    if (c.priceUrl === link.url && c.priceEUR != null) return { price: c.priceEUR };
  }
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
