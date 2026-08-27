import type { Cigar, Region, RegionFilter, Vitola } from "../types";
import { shopsForRegion } from "../data/shops";
import { urlFitsVitola } from "./vitolaLinkMatch";

const norm = (s: string) => s.trim().toLowerCase();

const ALL_REGIONS: Region[] = ["HR", "EU", "USA"];

/**
 * Je li ova vitola dostupna u odabranoj regiji (ne linija kao cjelina).
 * ALL = da; inače regionLinks[regija] ili product URL na hostu te regije.
 */
export function vitolaInRegion(v: Vitola, f: RegionFilter): boolean {
  if (f === "ALL") return true;
  const region = f as Region;
  if (v.regionLinks?.[region]?.url) return true;
  if (v.url) {
    for (const shop of shopsForRegion(region)) {
      if (shop.productHost && v.url.includes(shop.productHost)) return true;
    }
  }
  return false;
}

/**
 * EU/USA linkovi (i cijene) za odabranu vitolu.
 *
 * Vitolin vlastiti `regionLinks` uvijek pobjeđuje — scrapan je za nju.
 * Linijski link se nasljeđuje samo kad slug proizvoda odgovara imenu vitole:
 * inače je to stranica druge vitole iste linije (CigarWorld/Holt's zna imati
 * samo jednu), pa bi svaka vitola vodila na isti krivi proizvod i pokazivala
 * njegovu cijenu.
 */
function regionLinksForVitola(
  cigar: Cigar,
  vitola: Vitola,
): Cigar["regionLinks"] | undefined {
  const out: NonNullable<Cigar["regionLinks"]> = {};
  const context = `${cigar.brand} ${cigar.line}`;
  for (const region of ALL_REGIONS) {
    const own = vitola.regionLinks?.[region];
    if (own) {
      out[region] = own;
      continue;
    }
    const line = cigar.regionLinks?.[region];
    if (line?.url && urlFitsVitola(line.url, vitola.name, context)) out[region] = line;
  }
  return Object.keys(out).length > 0 ? out : undefined;
}

// Locale-normalizirani ključ proizvoda: /en/ i /hr/ stranice iste cigare vode
// na isti proizvod. Koristi se kao sigurnosna mreža protiv locale-blizanaca
// (glavni dedup je u scripts/normalize-vitolas.py nad podacima).
const productKey = (url: string | null | undefined): string | null => {
  if (!url) return null;
  let u = url.split("?")[0].split("#")[0];
  u = u.replace(
    /(humidor\.hr|havana-cigar-shop\.com)\/(?:hr|en)\/proizvod\//,
    "$1/proizvod/",
  );
  u = u.replace(/cigarworld\.de\/(?:en|de)\//, "cigarworld.de/");
  u = u.replace(/\/+$/, "");
  return u.includes("/proizvod/") ? u : null;
};

const isProductUrl = (url: string | null | undefined): url is string =>
  Boolean(
    url &&
      !url.includes("?s=") &&
      !/holts\.com\/cigars\/all-cigar-brands\/[^/?#]+\.html/i.test(url),
  );

const preferHrUrl = (a: Vitola, b: Vitola): Vitola => {
  const aHumidor = a.url?.includes("humidor.hr") ?? false;
  const bHumidor = b.url?.includes("humidor.hr") ?? false;
  if (aHumidor && !bHumidor) return a;
  if (bHumidor && !aHumidor) return b;
  return a;
};

export function uniqueVitolas(cigar: Cigar): Vitola[] {
  const seenNames = new Set<string>();
  const seenUrls = new Set<string>();
  const out: Vitola[] = [];
  for (const v of cigar.vitolas ?? []) {
    const key = v.name.trim().toLowerCase();
    if (!key || seenNames.has(key)) continue;
    // sigurnosna mreža: isti proizvod (locale-blizanac) pod drugim imenom
    const pk =
      productKey(v.url) ??
      productKey(v.regionLinks?.HR?.url) ??
      null;
    if (pk && seenUrls.has(pk)) continue;
    seenNames.add(key);
    if (pk) seenUrls.add(pk);
    out.push(v);
  }
  return out;
}

export function needsVitolaPick(cigar: Cigar): boolean {
  return uniqueVitolas(cigar).length > 1;
}

/** Što otvoriti kad korisnik klikne cigaru: linija (izbor vitole) ili kartica vitole. */
export type CigarSheetOpen =
  | { mode: "line"; cigar: Cigar }
  | { mode: "detail"; cigar: Cigar };

/**
 * Multi-vitola linija → LineSheet (klikabilan popis).
 * Jedna vitola ili već primijenjen `applyVitola` → DetailSheet s tom veličinom.
 * Ništa se ne briše iz podataka — sibling vitole ostaju na liniji.
 */
export function resolveCigarSheetOpen(cigar: Cigar): CigarSheetOpen {
  if (needsVitolaPick(cigar)) {
    return { mode: "line", cigar };
  }
  return { mode: "detail", cigar };
}

/** Zadana vitola za cijenu/link — ne najjeftinija u listi. */
export function resolveDefaultVitola(cigar: Cigar): Vitola | undefined {
  const vitolas = uniqueVitolas(cigar);
  if (vitolas.length === 0) return undefined;
  if (vitolas.length === 1) return vitolas[0];

  const line = norm(cigar.line);
  const byLineExact = vitolas.find((v) => norm(v.name) === line);
  if (byLineExact) return byLineExact;

  const byField = vitolas.find((v) => norm(v.name) === norm(cigar.vitola));
  if (byField) return byField;

  const byLine = vitolas.find(
    (v) => line.includes(norm(v.name)) || norm(v.name).includes(line),
  );
  if (byLine) return byLine;

  const productVitolas = vitolas.filter((v) => isProductUrl(v.url));
  const priced = productVitolas.filter((v) => v.priceEUR != null);
  if (priced.length === 1) return priced[0];
  if (priced.length > 1) {
    return priced.reduce(preferHrUrl);
  }
  if (productVitolas.length === 1) return productVitolas[0];
  if (productVitolas.length > 1) {
    return productVitolas.reduce(preferHrUrl);
  }

  return vitolas[0];
}

/** Primijeni odabranu vitolu na prikaz / pairing (cijena, format, link). */
export function applyVitola(cigar: Cigar, vitola: Vitola): Cigar {
  const inheritedPriceUrl = cigar.priceUrl ?? null;

  // Ako vitola nema vlastiti product URL, ranije je fallbackao na
  // `cigar.priceUrl` (što može biti pogrešan proizvod kad dimenzije/format
  // ne odgovaraju).
  // Novi guard: naslijedi URL samo ako izgleda kao da pripada istoj vitoli
  // (usporedba format/ring/length kad postoje).
  const resolvedPriceUrl = (() => {
    if (vitola.url) return vitola.url;
    if (!inheritedPriceUrl) return null;

    const anchor = (cigar.vitolas ?? []).find((v) => v.url === inheritedPriceUrl);
    if (!anchor) return null;

    const anchorFormat = anchor.format ?? null;
    const vitolaFormat = vitola.format ?? null;
    const anchorRing = anchor.ring ?? null;
    const vitolaRing = vitola.ring ?? null;
    const anchorLen = anchor.lengthMM ?? null;
    const vitolaLen = vitola.lengthMM ?? null;

    const anyComparable =
      (anchorFormat && vitolaFormat) ||
      (anchorRing != null && vitolaRing != null) ||
      (anchorLen != null && vitolaLen != null);

    if (!anyComparable) return inheritedPriceUrl; // nema čime dokazati mismatch

    const formatOk = anchorFormat && vitolaFormat ? anchorFormat === vitolaFormat : true;
    const ringOk = anchorRing != null && vitolaRing != null ? anchorRing === vitolaRing : true;
    const lenOk = anchorLen != null && vitolaLen != null ? anchorLen === vitolaLen : true;

    return formatOk && ringOk && lenOk ? inheritedPriceUrl : null;
  })();

  // Linija s više formata: zapamti izbor da stanje kolekcije/dnevnika ide po
  // vitoli (vidi lib/cigarItemId). Linija s jednim formatom nema što razdvajati.
  const selectedVitola =
    uniqueVitolas(cigar).length > 1 ? vitola.name : cigar.selectedVitola;

  return {
    ...cigar,
    selectedVitola,
    vitola: vitola.name,
    format: vitola.format && vitola.format !== "—" ? vitola.format : cigar.format,
    smokeTimeMin: vitola.smokeTimeMin ?? cigar.smokeTimeMin,
    priceEUR: vitola.priceEUR ?? cigar.priceEUR,
    priceUrl: resolvedPriceUrl,
    // odabir vitole → kupnja/cijena po regiji vode na TU vitolu (market katalog)
    regionLinks: regionLinksForVitola(cigar, vitola),
    // prikaži SAMO odabranu vitolu (ne cijeli popis) — kad tražiš Robusto,
    // Churchill i Half Corona te ne zanimaju
    vitolas: [vitola],
  };
}
