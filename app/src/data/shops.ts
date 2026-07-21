// Registar trgovina cigarama po regiji — jedini izvor istine za "gdje kupiti"
// linkove i za detaljan popis trgovina (Katalog → Trgovine).
//
// HR trgovine imaju `productHost` pa app prepoznaje izravne linkove na proizvod
// iz kataloga (humidor.hr / havana-cigar-shop.com). EU/USA trgovine nemaju
// scrapane linkove po proizvodu — koriste pretragu po nazivu (referentno).
import type { Region } from "../types";

export interface Shop {
  id: string;
  name: string;
  region: Region;
  home: string; // naslovnica trgovine
  productHost?: string; // host izravnih product URL-ova u katalogu
  search: (query: string) => string; // pretraga po nazivu (query je vec encodeURIComponent)
  note: { hr: string; en: string };
}

// Redoslijed u nizu = redoslijed prikaza unutar regije (prva = primarna).
export const SHOPS: Shop[] = [
  {
    id: "humidor",
    name: "The Humidor",
    region: "HR",
    home: "https://humidor.hr/hr/",
    productHost: "humidor.hr",
    search: (q) => `https://humidor.hr/?s=${q}&post_type=product`,
    note: { hr: "Zagreb — cijene po vitoli", en: "Zagreb — prices per vitola" },
  },
  {
    id: "havana-hr",
    name: "Havana Cigar Shop",
    region: "HR",
    home: "https://havana-cigar-shop.com/",
    productHost: "havana-cigar-shop.com",
    search: (q) => `https://havana-cigar-shop.com/?s=${q}`,
    note: { hr: "provjera dobi na ulazu", en: "age-gate at entry" },
  },
  {
    id: "cigarworld",
    name: "CigarWorld",
    region: "EU",
    home: "https://www.cigarworld.de/en",
    search: (q) => `https://www.cigarworld.de/en/search?q=${q}`,
    note: { hr: "Njemacka — dostava po EU", en: "Germany — ships across the EU" },
  },
  {
    id: "holts",
    name: "Holt's",
    region: "USA",
    home: "https://www.holts.com/",
    search: (q) => `https://www.holts.com/catalogsearch/result/?q=${q}`,
    note: { hr: "Philadelphia — klasicna US kuca", en: "Philadelphia — classic US house" },
  },
  {
    id: "cigarsdaily",
    name: "Cigars Daily",
    region: "USA",
    home: "https://cigarsdaily.com/",
    search: (q) => `https://cigarsdaily.com/?s=${q}`,
    note: { hr: "US ponude i recenzije", en: "US deals and reviews" },
  },
];

// Sve regije redom kako se prikazuju.
export const REGIONS: Region[] = ["HR", "EU", "USA"];

export const shopsForRegion = (r: Region): Shop[] =>
  SHOPS.filter((s) => s.region === r);
