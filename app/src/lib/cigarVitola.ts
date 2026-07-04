import type { Cigar, Vitola } from "../types";

export function uniqueVitolas(cigar: Cigar): Vitola[] {
  const seen = new Set<string>();
  const out: Vitola[] = [];
  for (const v of cigar.vitolas ?? []) {
    const key = v.name.trim().toLowerCase();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(v);
  }
  return out;
}

export function needsVitolaPick(cigar: Cigar): boolean {
  return uniqueVitolas(cigar).length > 1;
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
  };
}
