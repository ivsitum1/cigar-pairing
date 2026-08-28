import images from "../data/productImages.json";
import local from "../data/productImagesLocal.json";
import cigarAliasFile from "../data/cigarIdAliases.json";
import drinkAliasFile from "../data/drinkIdAliases.json";
import type { Cigar } from "../types";
import { cigarItemId } from "./cigarItemId";

/**
 * Fotografije proizvoda — dva sloja, jedan odgovor.
 *
 * SLOJ 1 (`productImages.json`): adresa slike kod dućana. Nastaje scrapeom,
 * pokriva gotovo cijeli katalog i prikazuje se izravno s tudjeg posluzitelja.
 * Te su fotografije snimljene na cemu je koji ducan htio — bijelo, crno, drvo.
 *
 * SLOJ 2 (`productImagesLocal.json`): ista slika, ali preuzeta i obradjena
 * (`scripts/normalize-product-images.py`) — podloga maknuta u prozirno, izrez
 * na proizvod, poravnata svjetlina. Lezi u `public/img/products/`.
 *
 * Obradjena pobjedjuje kad postoji. Sloj 1 ostaje kao zastita: dok obrada nije
 * pokrenuta, ili za stavke koje kroz nju nisu prosle, kartica i dalje ima
 * sliku — samo neujednacenu. Nikad se ne gubi ono sto je vec radilo.
 */

/** Kako je slika obradjena. */
export type ImageTreatment =
  /** Podloga je maknuta — slika sjeda izravno na karticu, bez plohe iza. */
  | "cutout"
  /** Podloga se nije dala odvojiti (ambijentalna fotografija) — ide u okvir. */
  | "framed"
  /** Neobradjena slika s dućanskog poslužitelja — podloga je kakva jest. */
  | "remote";

export type ProductPhoto = {
  src: string;
  treatment: ImageTreatment;
  /** Izvorne dimenzije obradjene slike; kod udaljenih se ne znaju. */
  width?: number;
  height?: number;
};

type UrlMaps = { cigars: Record<string, string>; drinks: Record<string, string> };
type LocalUnos = { w: number; h: number; t: string };
type LocalMaps = { cigars?: Record<string, LocalUnos>; drinks?: Record<string, LocalUnos> };

const MAPS = images as UrlMaps;
const LOCAL = local as LocalMaps;
const CIGAR_ALIASES: Record<string, string> =
  (cigarAliasFile as { aliases?: Record<string, string> }).aliases ?? {};
const DRINK_ALIASES: Record<string, string> =
  (drinkAliasFile as { aliases?: Record<string, string> }).aliases ?? {};

function followAlias(kind: "cigar" | "drink", id: string): string {
  const map = kind === "cigar" ? CIGAR_ALIASES : DRINK_ALIASES;
  let cur = id;
  const seen = new Set<string>();
  while (map[cur] && !seen.has(cur)) {
    seen.add(cur);
    cur = map[cur];
  }
  return cur;
}

/** Živi ključ slike: kanonski ID ako ima fotografiju, inače original. */
function photoId(kind: "cigar" | "drink", id: string): string {
  const canon = followAlias(kind, id);
  const map = kind === "cigar" ? MAPS.cigars : MAPS.drinks;
  if (map[canon]) return canon;
  if (map[id]) return id;
  return canon;
}

/**
 * Vite servira aplikaciju pod `/cigar-pairing/`, ne pod korijenom. Tvrdo
 * upisan `/img/...` radio bi u dev serveru samo slucajno, a na GitHub Pagesu
 * bi dao 404.
 */
function base(): string {
  const b = import.meta.env.BASE_URL || "/";
  return b.endsWith("/") ? b : `${b}/`;
}

/**
 * Adresa slike kod dućana, bez obzira postoji li obradjena inacica.
 * Zadrzano kao zaseban izvor istine — po njemu radi i skripta koja preuzima.
 */
export function productImageUrl(kind: "cigar" | "drink", id: string): string | null {
  const map = kind === "cigar" ? MAPS.cigars : MAPS.drinks;
  const url = map[photoId(kind, id)];
  return typeof url === "string" && url.startsWith("http") ? url : null;
}

/**
 * Slika za prikaz: obradjena ako je ima, inace dućanska.
 *
 * Ključevi u manifestu: `cig-x` (linija) ili `cig-x@vitola-slug` kad dućan
 * ima zaseban product URL po veličini. Lookup ide alias → kanonski id.
 */
export function productPhoto(kind: "cigar" | "drink", id: string | undefined): ProductPhoto | null {
  if (!id) return null;
  const vrsta = kind === "cigar" ? "cigars" : "drinks";
  const lookup = photoId(kind, id);
  const localKey = LOCAL[vrsta]?.[lookup] ? lookup : id;

  const obradjena = LOCAL[vrsta]?.[localKey];
  if (obradjena) {
    return {
      src: `${base()}img/products/${vrsta}/${encodeURIComponent(localKey)}.webp`,
      // Okvir je vidljiv zahvat; kad popis kaže nešto nepoznato, tiši je izbor.
      treatment: obradjena.t === "framed" ? "framed" : "cutout",
      width: obradjena.w,
      height: obradjena.h,
    };
  }

  const url = productImageUrl(kind, id);
  return url ? { src: url, treatment: "remote" } : null;
}

/**
 * Slika cigare uz odabranu vitolu: prvo `cig-x@vitola`, pa linija `cig-x`.
 * Linija s jednom vitolom koristi isti ključ kao prije.
 */
export function productPhotoForCigar(cigar: Cigar): ProductPhoto | null {
  const scoped = cigarItemId(cigar);
  if (scoped !== cigar.id) {
    const hit = productPhoto("cigar", scoped);
    if (hit) return hit;
  }
  return productPhoto("cigar", cigar.id);
}

/** Koliko je slika prošlo obradu — za izvještaj skripte i provjere. */
export function processedCount(): number {
  return Object.keys(LOCAL.cigars ?? {}).length + Object.keys(LOCAL.drinks ?? {}).length;
}
