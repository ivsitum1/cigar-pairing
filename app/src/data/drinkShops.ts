// Registar trgovina PICEM — jedini izvor istine za "Gdje kupiti" kod boca.
// (Cigare imaju vlastiti registar u `shops.ts`; pravila su druga jer se duhan
// u HR ne prodaje online.)
//
// Zasto postoji: katalog ima izravan link na proizvod za manjinu boca
// (allez/ecuga scrape). Za ostale je do sada pisalo samo `shopHR` ("allez.hr")
// i gumb je vodio na Google — tvrdnja o dostupnosti bez pokrica. Ovdje se
// razdvaja sto app zna:
//   product — potvrdena stranica te boce (slug se poklapa s imenom),
//   search  — trgovina ima pretragu po nazivu (WordPress `?s=`), pa link
//             stvarno trazi tu bocu, ali pogodak nije zajamcen,
//   browse  — trgovinu znamo, ali ne i njen endpoint pretrage: link vodi na
//             katalog kategorije (nikad na izmisljeni URL),
//   ref     — svjetski cjenik (wine-searcher) za orijentir kad boce nema u HR.
import type { DrinkCategory, LocalizedText } from "../types";

/**
 * Regija police. HR/EU/USA prate isti raspored kao trgovine cigarama
 * (`shops.ts` — UK i CH žive pod "EU"), REF je svjetski cjenik.
 */
export type DrinkShopScope = "HR" | "EU" | "USA" | "REF";

export interface DrinkShop {
  id: string;
  name: string;
  scope: DrinkShopScope;
  home: string;
  /** Host izravnih product URL-ova u katalogu (`priceUrl`). */
  productHost?: string;
  categories: DrinkCategory[];
  /**
   * Pretraga po nazivu boce. Za razliku od `shops.ts` (cigare), ovdje stize
   * SIROVO ocisceno ime — svaka trgovina kodira kako njen URL trazi
   * (`?s=` query vs. wine-searcher `/find/ime+s+plusevima`).
   */
  search?: (name: string) => string;
  /** Katalog po kategoriji — koristi se kad trgovina nema poznatu pretragu. */
  browse?: Partial<Record<DrinkCategory, string>>;
  note: LocalizedText;
}

const SPIRITS: DrinkCategory[] = ["rum", "whisky", "gin", "brandy", "tequila", "digestif"];

// Redoslijed u nizu je samo registar; prikaz slaze `drinkShopLinks`
// (potvrdena boca prva, pa trgovine s pretragom, pa katalozi).
export const DRINK_SHOPS: DrinkShop[] = [
  {
    id: "allez",
    name: "allez.hr",
    scope: "HR",
    home: "https://allez.hr/",
    productHost: "allez.hr",
    categories: SPIRITS,
    browse: {
      rum: "https://allez.hr/shop/rum4",
      whisky: "https://allez.hr/shop/whiskey",
      gin: "https://allez.hr/shop/gin1",
      brandy: "https://allez.hr/shop/cognac-calvados-armagnac",
      tequila: "https://allez.hr/shop/tequila-mezcal",
      digestif: "https://allez.hr/shop/absinthe-brandy-grappa-sake",
    },
    note: {
      hr: "Najširi online izbor žestice u HR; izravan link kad je boca u katalogu",
      en: "Widest online spirits range in Croatia; direct link when the bottle is in the catalogue",
    },
  },
  {
    id: "ecuga",
    name: "ecuga.com",
    scope: "HR",
    home: "https://ecuga.com/",
    productHost: "ecuga.com",
    categories: SPIRITS,
    browse: {
      whisky: "https://ecuga.com/katalog/whisky",
      rum: "https://ecuga.com/katalog/rum",
      gin: "https://ecuga.com/katalog/spirits-and-liqueurs",
      brandy: "https://ecuga.com/katalog/spirits-and-liqueurs",
      tequila: "https://ecuga.com/katalog/spirits-and-liqueurs",
      digestif: "https://ecuga.com/katalog/spirits-and-liqueurs",
    },
    note: {
      hr: "Specijalist za viski i rum; katalog po potkategorijama",
      en: "Whisky and rum specialist; catalogue by sub-category",
    },
  },
  {
    id: "tipsy",
    name: "Tipsy",
    scope: "HR",
    home: "https://tipsy.hr/",
    productHost: "tipsy.hr",
    categories: [...SPIRITS, "wine"],
    // WordPress/WooCommerce trgovina — pretraga po nazivu radi za cijeli katalog
    search: (name) => `https://tipsy.hr/?s=${encodeURIComponent(name)}&post_type=product`,
    browse: {
      rum: "https://tipsy.hr/zestice/rum-zestice/",
      whisky: "https://tipsy.hr/zestice/whiskey-zestice/",
    },
    note: {
      hr: "Zagreb — dostava; pretraga po nazivu boce",
      en: "Zagreb — delivery; search by bottle name",
    },
  },
  {
    id: "cugaklik",
    name: "Cugaklik",
    scope: "HR",
    home: "https://www.cugaklik.hr/",
    productHost: "cugaklik.hr",
    categories: [...SPIRITS, "wine"],
    search: (name) =>
      `https://www.cugaklik.hr/?s=${encodeURIComponent(name)}&post_type=product`,
    browse: {
      rum: "https://www.cugaklik.hr/kategorija/zestoka-cuga/rum/",
    },
    note: {
      hr: "Žestica i vino uz dostavu po RH; pretraga po nazivu boce",
      en: "Spirits and wine delivered across Croatia; search by bottle name",
    },
  },
  {
    id: "roto",
    name: "Roto",
    scope: "HR",
    home: "https://webshop.rotodinamic.hr/",
    productHost: "webshop.rotodinamic.hr",
    categories: SPIRITS,
    browse: {
      rum: "https://webshop.rotodinamic.hr/en/spirits",
      whisky: "https://webshop.rotodinamic.hr/en/spirits",
      gin: "https://webshop.rotodinamic.hr/en/spirits",
      brandy: "https://webshop.rotodinamic.hr/en/spirits",
      tequila: "https://webshop.rotodinamic.hr/en/spirits",
      digestif: "https://webshop.rotodinamic.hr/en/spirits",
    },
    note: {
      hr: "Veleprodajni webshop — širok katalog žestice",
      en: "Wholesaler webshop — wide spirits catalogue",
    },
  },
  {
    id: "vrutak",
    name: "Vrutak",
    scope: "HR",
    home: "https://www.vrutak.hr/",
    // Vino drže, ali nemamo provjeren URL tog odjela — bez izmišljanja puta.
    categories: SPIRITS,
    browse: {
      rum: "https://www.vrutak.hr/zestoka-pica",
      whisky: "https://www.vrutak.hr/zestoka-pica",
      gin: "https://www.vrutak.hr/zestoka-pica",
      brandy: "https://www.vrutak.hr/zestoka-pica",
      tequila: "https://www.vrutak.hr/zestoka-pica",
      digestif: "https://www.vrutak.hr/zestoka-pica",
    },
    note: {
      hr: "Zagreb — velik odjel žestice i vina u trgovini",
      en: "Zagreb — large in-store spirits and wine section",
    },
  },
  {
    id: "vivat",
    name: "Vivat fina vina",
    scope: "HR",
    home: "https://www.vivat-finavina.hr/",
    productHost: "vivat-finavina.hr",
    categories: ["wine"],
    browse: {
      wine: "https://www.vivat-finavina.hr/",
    },
    note: {
      hr: "Vinoteka s webshopom — hrvatska i uvozna vina",
      en: "Wine shop with a webshop — Croatian and imported wines",
    },
  },
  // EU / USA: samo trgovine kojima znamo endpoint pretrage po nazivu. Ostale
  // (Drinks&Co, Conalco, Wine.com…) namjerno nisu ovdje — URL se ne izmišlja,
  // a nepotvrđen upit vodi na praznu stranicu, što je gore od Google pretrage.
  {
    id: "whisky-exchange",
    name: "The Whisky Exchange",
    scope: "EU",
    home: "https://www.thewhiskyexchange.com/",
    productHost: "thewhiskyexchange.com",
    categories: SPIRITS,
    search: (name) =>
      `https://www.thewhiskyexchange.com/search?q=${encodeURIComponent(name)}`,
    note: {
      hr: "London — najveći europski specijalist za žesticu, dostava po EU",
      en: "London — largest European spirits specialist, ships across the EU",
    },
  },
  {
    id: "total-wine",
    name: "Total Wine & More",
    scope: "USA",
    home: "https://www.totalwine.com/",
    productHost: "totalwine.com",
    categories: [...SPIRITS, "wine"],
    search: (name) =>
      `https://www.totalwine.com/search/all?text=${encodeURIComponent(name)}`,
    note: {
      hr: "SAD — velik lanac; zaliha i dostava ovise o saveznoj državi",
      en: "USA — large chain; stock and delivery depend on the state",
    },
  },
  {
    id: "wine-searcher",
    name: "Wine-Searcher",
    scope: "REF",
    home: "https://www.wine-searcher.com/",
    categories: [...SPIRITS, "wine"],
    // Svjetski cjenik: /find/<ime s "+"> vraca ponude i raspon cijena.
    search: (name) =>
      `https://www.wine-searcher.com/find/${name
        .split(/\s+/)
        .filter(Boolean)
        .map(encodeURIComponent)
        .join("+")}`,
    note: {
      hr: "Svjetski cjenik — provjera cijene i tko bocu uopće drži",
      en: "Global price index — check the price and who stocks the bottle at all",
    },
  },
];

export const drinkShopById = (id: string): DrinkShop | undefined =>
  DRINK_SHOPS.find((s) => s.id === id);

export const drinkShopsForCategory = (c: DrinkCategory): DrinkShop[] =>
  DRINK_SHOPS.filter((s) => s.categories.includes(c));
