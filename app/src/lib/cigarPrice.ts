// Jedan izvor istine za cijenu cigare — SVA mjesta u appu (popis, linija,
// izbor vitole, kartica, gumb kupnje) moraju pokazati isti broj za istu
// vitolu i isto tržište.
//
// Prije je svaki prikaz imao vlastito pravilo: popis je uzimao HR cijenu
// zadane vitole, kartica je za vitolu bez HR cijene tiho posegnula za prvom
// regijom koja ima broj (najčešće njemački CigarWorld), a linija/izbor vitole
// gledali su samo `v.priceEUR` pa su za istu vitolu pisali "provjeri cijenu".
// Zato je korisnik na jednoj cigari vidio tri različite cijene.
//
// Model: cijena UVIJEK pripada paru (vitola, regija). Regija se bira iz
// odabranog tržišta; "ALL" ide redom HR → EU → USA i vraća `region` da prikaz
// može reći odakle broj dolazi.
import type { Cigar, Region, RegionFilter, Vitola } from "../types";
import { uniqueVitolas } from "./cigarVitola";

export interface ResolvedPrice {
  price: number | null;
  /** Konverzija iz druge valute / cijena "od" na razini linije. */
  approx: boolean;
  /** Link na proizvod koji nosi TU cijenu (null = nemamo izravan link). */
  url: string | null;
  shop: string | null;
  /** Iz koje regije broj dolazi — prikaz to označi kad nije odabrano tržište. */
  region: Region | null;
}

const NONE: ResolvedPrice = {
  price: null,
  approx: false,
  url: null,
  shop: null,
  region: null,
};

/** Redoslijed traženja cijene za odabrani filter tržišta. */
export function regionOrder(market: RegionFilter): Region[] {
  return market === "ALL" ? ["HR", "EU", "USA"] : [market];
}

/**
 * `v.priceEUR` / `v.url` su HR podaci (humidor.hr, havana-cigar-shop.com) —
 * vidi `Vitola` u types.ts. `regionLinks.HR` je scrapan zasebno i zna pokazati
 * na drugu vitolu, pa je tek zamjena kad vlastite cijene nema.
 */
function vitolaPriceInRegion(v: Vitola, region: Region): ResolvedPrice {
  if (region === "HR" && v.priceEUR != null) {
    return {
      price: v.priceEUR,
      approx: false,
      url: v.url ?? v.regionLinks?.HR?.url ?? null,
      shop: v.regionLinks?.HR?.shop ?? null,
      region: "HR",
    };
  }
  const rl = v.regionLinks?.[region];
  if (rl?.priceEUR != null) {
    return {
      price: rl.priceEUR,
      approx: rl.priceApprox === true,
      url: rl.url ?? null,
      shop: rl.shop ?? null,
      region,
    };
  }
  return NONE;
}

/** Cijena jedne vitole za odabrano tržište. */
export function vitolaPriceForMarket(
  v: Vitola,
  market: RegionFilter,
): ResolvedPrice {
  for (const region of regionOrder(market)) {
    const hit = vitolaPriceInRegion(v, region);
    if (hit.price != null) return hit;
  }
  return NONE;
}

/**
 * Cijena linije u popisu = NAJNIŽA cijena njenih vitola u tom tržištu, uz
 * `from` kad ostale vitole koštaju više.
 *
 * Ranije se prikazivala cijena zadane vitole, a "od" se palio čim je raspon
 * postojao — pa je uz Opus X pisalo "od 51 €" iako je najjeftinija vitola u
 * liniji 12,30 €. Sada "od X" znači točno to: X je najniža cijena u liniji, a
 * link vodi na tu vitolu.
 */
export interface LinePrice extends ResolvedPrice {
  /** Prikaži "od X €" — ostale vitole u liniji koštaju više. */
  from: boolean;
  min: number | null;
  max: number | null;
}

export function cigarLinePrice(c: Cigar, market: RegionFilter): LinePrice {
  const resolved = uniqueVitolas(c)
    .map((v) => vitolaPriceForMarket(v, market))
    .filter((r) => r.price != null);

  if (resolved.length > 0) {
    const prices = resolved.map((r) => r.price!);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const cheapest = resolved.find((r) => r.price === min)!;
    return { ...cheapest, from: max - min > 0.01, min, max };
  }

  // Linija bez ijedne vitole s cijenom: HR pada na cijenu zapisanu na liniji,
  // EU/USA na scrapanu "od" cijenu linije.
  for (const region of regionOrder(market)) {
    if (region === "HR" && c.priceEUR != null) {
      const base: ResolvedPrice = {
        price: c.priceEUR,
        approx: c.priceApprox === true,
        url: c.priceUrl ?? null,
        shop: null,
        region: "HR",
      };
      return { ...base, from: false, min: c.priceEUR, max: c.priceEUR };
    }
    const rl = c.regionLinks?.[region];
    if (rl?.priceEUR != null) {
      const base: ResolvedPrice = {
        price: rl.priceEUR,
        approx: rl.priceApprox === true,
        url: rl.url ?? null,
        shop: rl.shop ?? null,
        region,
      };
      return { ...base, from: false, min: rl.priceEUR, max: rl.priceEUR };
    }
  }

  return { ...NONE, from: false, min: null, max: null };
}

/** "12,50 €" / "13 €" — dvije decimale samo kad ih cijena stvarno ima. */
export function formatEur(price: number): string {
  return `${price.toFixed(price % 1 ? 2 : 0)} €`;
}
