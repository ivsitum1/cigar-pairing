import type { Cigar, Drink, DrinkCategory, Region, RegionFilter, Vitola } from "../types";
import { shopsForRegion, REGIONS, isLineListingUrl } from "./shops";
import { cigarAvailableInRegion, cigarCatalogProof } from "../lib/cigarAvailability";

export { isLineListingUrl } from "./shops";
export {
  cigarAvailableInRegion,
  cigarCatalogProof,
  cigarShelfStatus,
} from "../lib/cigarAvailability";
export type { CatalogProof, ShelfStatus } from "../lib/cigarAvailability";
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
import { bestVitolaUrl, urlFitsVitola } from "../lib/vitolaLinkMatch";
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

const hostOfUrl = (url: string): string => {
  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return "";
  }
};

/**
 * Scrape zna vitoli pripisati proizvod SESTRINSKE vitole (Robusto → Toro,
 * Lancero → Torpedo — 331 od 4884 linkova u katalogu). Takav link je i kriva
 * cijena, jer `priceEUR` pripada tom drugom proizvodu.
 *
 * Ovdje se to čisti jednom, na ulazu u app, pa svi prikazi (popis vitola,
 * cijena, gumbi kupnje) vide isto: ako linija ima product URL te vitole na
 * istom hostu (`sourceUrls`), link se zamijeni njime i cijena otpada; inače
 * link otpada i ostaje pretraga po nazivu.
 */
function sanitizeVitolaLinks(c: Cigar): Cigar {
  const vitolas = c.vitolas ?? [];
  if (vitolas.length === 0) return c;
  const context = `${c.brand} ${c.line}`;
  let touched = false;

  const next = vitolas.map((v) => {
    const links = v.regionLinks;
    if (!links) return v;
    const kept: NonNullable<Vitola["regionLinks"]> = {};
    let changed = false;
    for (const region of REGIONS) {
      const link = links[region];
      if (!link?.url) continue;
      if (urlFitsVitola(link.url, v.name, context)) {
        kept[region] = link;
        continue;
      }
      changed = true;
      const host = hostOfUrl(link.url);
      const better = host
        ? bestVitolaUrl(
            (c.sourceUrls ?? []).filter((u) => hostOfUrl(u) === host),
            v.name,
            context,
          )
        : null;
      // cijena je pripadala krivom proizvodu — ne seli se na novi URL
      if (better) kept[region] = { shop: link.shop, url: better };
    }
    if (!changed) return v;
    touched = true;
    return { ...v, regionLinks: Object.keys(kept).length > 0 ? kept : undefined };
  });

  return touched ? { ...c, vitolas: next } : c;
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

export const CIGARS: Cigar[] = dedupeCigars(cigarsJson as Cigar[]).map(sanitizeVitolaLinks);

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
  /** Jedna rečenica: u čemu je ta kuća naj. Postoji samo gdje je stvarno znamo. */
  signature?: { hr: string; en: string };
  /** Priča o kući — kako je nastala i što je oblikovalo njezin stil. */
  story?: { hr: string; en: string };
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

// Je li cigara dostupna u odabranoj regiji — dokaz u trgovini, ne samo markets.
// "ALL" = bez filtera (sve).
export const cigarInRegion = (c: Cigar, f: RegionFilter): boolean =>
  cigarAvailableInRegion(c, f);

// Broj cigara s dokazom po regiji — za detaljan popis trgovina.
export const cigarCountByRegion: Record<Region, number> = {
  HR: CIGARS.filter((c) => cigarAvailableInRegion(c, "HR")).length,
  EU: CIGARS.filter((c) => cigarAvailableInRegion(c, "EU")).length,
  USA: CIGARS.filter((c) => cigarAvailableInRegion(c, "USA")).length,
};

// Izravan link na proizvod za dani host — samo URL koji odgovara prikazanoj
// cijeni (zadana vitola / priceUrl / vitola iste cijene). Ne padati na
// proizvoljnu vitolu istog hosta (npr. Cubanitos umjesto Gran Reserva).
function exactProductUrl(c: Cigar, host: string, region: Region): string | null {
  const shown = uniqueVitolas(c);
  // Prikaz jedne vitole: kandidati s tog hosta biraju se po imenu vitole, ne
  // "prvi koji nađem" — inače Maduro Robusto otvori Robusto ili Short Churchill.
  const only = shown.length === 1 ? shown[0] : null;
  const context = `${c.brand} ${c.line}`;
  const pick = (urls: string[]): string | null => {
    const usable = urls.filter((u) => u.includes(host) && !isLineListingUrl(u));
    if (usable.length === 0) return null;
    if (!only) return usable[0];
    return bestVitolaUrl(usable, only.name, context);
  };
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
  const fromVitolaLinks = pick(
    (c.vitolas ?? []).flatMap((v) =>
      Object.values(v.regionLinks ?? {})
        .map((link) => link?.url)
        .filter((u): u is string => Boolean(u)),
    ),
  );
  if (fromVitolaLinks) return fromVitolaLinks;
  // sourceUrls zna imati po jedan proizvod za SVAKU vitolu linije
  return pick([...(c.sourceUrls ?? [])]);
}

export interface CigarShopLink {
  region: Region;
  shop: string;
  url: string;
  exact: boolean; // true = izravan link na proizvod; false = listing / walk-in home
  /**
   * Što se zapravo otvara: stranica proizvoda, stranica cijele LINIJE (Holt's
   * i sl.), naslovnica walk-in dućana, ili (rijetko) pretraga.
   */
  kind: "product" | "line" | "walkin" | "search";
}

/**
 * Linijski EU/USA link kad je u prikazu jedna vitola: prihvati ga samo ako je
 * to link TE vitole (vitolin vlastiti scrape) ili slug odgovara njenom imenu.
 * Inače je to stranica druge vitole iste linije — vidi lib/vitolaLinkMatch.
 */
function regionLinkForShownVitola(c: Cigar, region: Region) {
  const rl = c.regionLinks?.[region];
  if (!rl?.url) return undefined;
  const vitolas = uniqueVitolas(c);
  if (vitolas.length !== 1) return rl; // cijela linija — link je linijski
  const v = vitolas[0];
  if (v.regionLinks?.[region]?.url === rl.url) return rl;
  // stranica cijele linije (Holt's listing) nije tvrdnja o vitoli, ali ni
  // kriva — pusti je; guard cilja krive PROIZVODE
  if (isLineListingUrl(rl.url)) return rl;
  return urlFitsVitola(rl.url, v.name, `${c.brand} ${c.line}`) ? rl : undefined;
}

/**
 * Linkovi na trgovine gdje imamo dokaz da cigara postoji u katalogu.
 * Ne izmišlja search gumbe za shopove bez product/line URL-a.
 */
export function cigarShopLinks(c: Cigar): CigarShopLink[] {
  const out: CigarShopLink[] = [];
  for (const region of REGIONS) {
    if (cigarCatalogProof(c, region) === "none") continue;

    const usedShops = new Set<string>();
    const push = (link: CigarShopLink) => {
      if (usedShops.has(link.shop)) return;
      usedShops.add(link.shop);
      out.push(link);
    };

    // EU/USA: scrapani regionLinks (product ili line listing)
    if (region !== "HR") {
      const rl = regionLinkForShownVitola(c, region);
      if (rl?.url) {
        const listing = isLineListingUrl(rl.url);
        push({
          region,
          shop: rl.shop,
          url: rl.url,
          exact: !listing,
          kind: listing ? "line" : "product",
        });
      }
    }

    for (const shop of shopsForRegion(region)) {
      if (usedShops.has(shop.name)) continue;

      if (region === "HR") {
        const named = (c.availabilityHR ?? []).includes(shop.name);
        if (shop.walkIn) {
          if (named) {
            push({
              region,
              shop: shop.name,
              url: shop.home,
              exact: false,
              kind: "walkin",
            });
          }
          continue;
        }
        const exact = shop.productHost
          ? exactProductUrl(c, shop.productHost, region)
          : null;
        if (exact) {
          const listing = isLineListingUrl(exact);
          push({
            region,
            shop: shop.name,
            url: exact,
            exact: !listing,
            kind: listing ? "line" : "product",
          });
        }
        // Online u availabilityHR bez product URL-a: bez gumba (dokaz ostaje za filter;
        // ime trgovine je već u DetailSheet retku availabilityHR). Ne izmišljamo search.
        continue;
      }

      // EU/USA: samo product/line URL — nikad search fallback
      const host = shop.productHost;
      const exact = host ? exactProductUrl(c, host, region) : null;
      // Holt's: regionLinks URL na holts.com (nema productHost)
      if (!exact && /holt/i.test(shop.name)) {
        const rl = regionLinkForShownVitola(c, region);
        if (rl?.url && /holts\.com/i.test(rl.url) && rl.shop === shop.name) {
          // already pushed above
          continue;
        }
        // vitola regionLinks may still match
        for (const v of c.vitolas ?? []) {
          const vrl = v.regionLinks?.[region];
          if (vrl?.url && /holts\.com/i.test(vrl.url)) {
            const listing = isLineListingUrl(vrl.url);
            push({
              region,
              shop: vrl.shop || shop.name,
              url: vrl.url,
              exact: !listing,
              kind: listing ? "line" : "product",
            });
            break;
          }
        }
        continue;
      }
      if (!exact) continue;
      const listing = isLineListingUrl(exact);
      push({
        region,
        shop: shop.name,
        url: exact,
        exact: !listing,
        kind: listing ? "line" : "product",
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
  // Stranica cijele linije (Holt's listing) nosi "od" cijenu linije — uz gumb
  // odabrane vitole to izgleda kao njena cijena, pa se ne prikazuje; gumb tada
  // nosi oznaku "stranica linije".
  if ((link.region === "EU" || link.region === "USA") && link.kind !== "line") {
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
