// Registar trgovina cigarama po regiji — jedini izvor istine za "gdje kupiti"
// linkove i za detaljan popis trgovina (Katalog → Trgovine).
//
// HR trgovine imaju `productHost` pa app prepoznaje izravne linkove na proizvod
// iz kataloga (humidor.hr / havana-cigar-shop.com). EU/USA: `regionLinks` ili
// `productHost` kad postoji scrapani product URL; inače pretraga po nazivu.
import type { Region } from "../types";

export interface Shop {
  id: string;
  name: string;
  region: Region;
  home: string; // naslovnica trgovine
  productHost?: string; // host izravnih product URL-ova u katalogu
  search: (query: string) => string; // pretraga po nazivu (query je vec encodeURIComponent)
  note: { hr: string; en: string };
  /**
   * Trgovina bez web kataloga (fizicki ducan). Prikazuje se u popisu trgovina
   * i u `availabilityHR`, ali NE dobiva link po proizvodu — pretraga po nazivu
   * na stranici koja nema katalog vodi u prazno.
   */
  walkIn?: boolean;
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
    id: "tobacco-petica-branimir",
    name: "Tobacco Petica (Branimir)",
    region: "HR",
    home: "https://www.branimir.hr/minglanje/trgovine/tobacco-petica",
    // fizicki ducan bez web kataloga — search vodi na stranicu ducana
    search: () => "https://www.branimir.hr/minglanje/trgovine/tobacco-petica",
    walkIn: true,
    note: {
      hr: "Zagreb, Branimir centar — dobavlja od Havana Cigar Shopa, djelomična Havana ponuda. Dućan bez web kataloga, kupnja na mjestu.",
      en: "Zagreb, Branimir Center — stocks a subset of Havana Cigar Shop. Walk-in, no online catalogue.",
    },
  },
  {
    id: "aficionado-zg",
    name: "Aficionado",
    region: "HR",
    home: "https://www.aficionado.hr/",
    // fizicki ducan bez web kataloga — search vodi na naslovnicu
    search: () => "https://www.aficionado.hr/",
    walkIn: true,
    note: {
      hr: "Zagreb — dućan bez web kataloga, kupnja na mjestu",
      en: "Zagreb — walk-in shop, no online catalogue",
    },
  },
  {
    id: "cigarworld",
    name: "CigarWorld",
    region: "EU",
    home: "https://www.cigarworld.de/en",
    productHost: "cigarworld.de",
    search: (q) => `https://www.cigarworld.de/en/search?q=${q}`,
    note: { hr: "Njemačka — dostava po Europi", en: "Germany — ships across Europe" },
  },
  {
    id: "cgars-uk",
    name: "C.Gars Ltd",
    region: "EU",
    home: "https://www.cgarsltd.co.uk/",
    productHost: "cgarsltd.co.uk",
    search: (q) => `https://www.cgarsltd.co.uk/advanced_search_result.php?keywords=${q}`,
    note: {
      hr: "UK — najveći online specijalist (Havana EMS, New World)",
      en: "UK — largest online specialist (Havana EMS, New World)",
    },
  },
  {
    id: "la-couronne-ch",
    name: "La Couronne",
    region: "EU",
    home: "https://cigarpassion.ch/en/",
    productHost: "cigarpassion.ch",
    search: (q) => `https://cigarpassion.ch/en/?s=${q}`,
    note: {
      hr: "Švicarska — ekskluzivni Habanos uvoznik (Intertabak), širok premium katalog",
      en: "Switzerland — exclusive Habanos importer (Intertabak), wide premium catalogue",
    },
  },
  {
    id: "holts",
    name: "Holt's",
    region: "USA",
    home: "https://www.holts.com/",
    search: (q) => `https://www.holts.com/catalogsearch/result/?q=${q}`,
    note: { hr: "Philadelphia — klasična američka kuća", en: "Philadelphia — classic US house" },
  },
  {
    id: "cigarsdaily",
    name: "Cigars Daily",
    region: "USA",
    home: "https://cigarsdaily.com/",
    productHost: "cigarsdaily.com",
    search: (q) => `https://cigarsdaily.com/?s=${q}`,
    note: { hr: "Američke ponude i recenzije", en: "US deals and reviews" },
  },
  {
    id: "famous-smoke",
    name: "Famous Smoke",
    region: "USA",
    home: "https://www.famous-smoke.com/",
    productHost: "famous-smoke.com",
    search: (q) => `https://www.famous-smoke.com/cigars?search=${q}`,
    note: {
      hr: "Pennsylvania — velik US katalog, value linije",
      en: "Pennsylvania — large US catalogue, value lines",
    },
  },
  {
    id: "neptune",
    name: "Neptune Cigar",
    region: "USA",
    home: "https://www.neptunecigar.com/",
    productHost: "neptunecigar.com",
    search: (q) => `https://www.neptunecigar.com/search?q=${q}`,
    note: {
      hr: "Florida — online + trgovine, česte value ponude",
      en: "Florida — online + retail stores, frequent value deals",
    },
  },
];

// Sve regije redom kako se prikazuju.
export const REGIONS: Region[] = ["HR", "EU", "USA"];

export const shopsForRegion = (r: Region): Shop[] =>
  SHOPS.filter((s) => s.region === r);
