import type { Cigar, Vitola } from "../types";

const norm = (s: string) => s.trim().toLowerCase();

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
  Boolean(url && !url.includes("?s="));

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
  return {
    ...cigar,
    vitola: vitola.name,
    format: vitola.format && vitola.format !== "—" ? vitola.format : cigar.format,
    smokeTimeMin: vitola.smokeTimeMin ?? cigar.smokeTimeMin,
    priceEUR: vitola.priceEUR ?? cigar.priceEUR,
    priceUrl: vitola.url ?? cigar.priceUrl,
    // odabir vitole → kupnja/cijena po regiji vode na TU vitolu (market katalog)
    regionLinks: vitola.regionLinks ?? cigar.regionLinks,
  };
}
