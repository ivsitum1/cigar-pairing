// Zajednicki tipovi podataka — odgovaraju JSON shemama u src/data/

export type Lang = "hr" | "en";

export type DrinkCategory =
  | "rum"
  | "whisky"
  | "brandy"
  | "wine"
  | "coffee"
  | "tequila"
  | "gin"
  | "digestif";

export type Market = "HR" | "EU" | "USA" | "WW";

// Kako se piće servira — mijenja aromu/žestinu spoja (vidi engine/serve.ts).
export type ServeStyle = "neat" | "water" | "rocks" | "highball" | "cola";

// Regija za kupnju cigara (bez WW — WW je "dostupno globalno" u podacima).
export type Region = "HR" | "EU" | "USA";
// Filter u UI-u: "ALL" = bez filtera (prikaži sve), inače konkretna regija.
export type RegionFilter = "ALL" | Region;

export interface LocalizedText {
  hr: string;
  en: string;
}

export interface PriceRange {
  min: number;
  max: number;
}

export interface Serving {
  neat?: number; // 0-3 (x, ~, +, ++)
  water?: number;
  rocks?: number;
  highball?: number;
  cola?: number;
  best: string;
}

export interface Drink {
  id: string;
  category: DrinkCategory;
  name: string;
  // Prikazno ime po jeziku. Kada opisno ime sadrži hrvatske riječi
  // ("Turska kava", "ledena", "tamna mješavina"), ovdje živi prijevod;
  // vlastiti pojmovi (džezva, cà phê sữa đá) ostaju nepromijenjeni.
  // Ako izostane, koristi se `name` u oba jezika.
  nameLoc?: LocalizedText;
  style: string;
  region: string;
  country?: string;
  abv?: number | null;
  body: number; // 1-5
  sweetness: number; // 1-5
  flavorTags: string[];
  additiveStatus?: string;
  additiveDetail?: LocalizedText;
  additiveSource?: string;
  qualityScore: number | null;
  priceEUR: PriceRange | null;
  priceApprox?: boolean;
  shopHR: string;
  status?: string | null; // META / IMAS / PROBAO iz Excela
  pairable: boolean;
  serving: Serving;
  cigarHint?: LocalizedText | null;
  priceUrl?: string | null; // izvor cijene / gdje kupiti
  notes: LocalizedText;
  // Za unose koji predstavljaju seriju/raspon (npr. Foursquare ECS), a ne
  // jednu bocu: popis izdanja koji se prikaze kad se detalj otvori.
  lineup?: string[];
}

export interface Vitola {
  name: string;
  format: string | null; // "50 x 127mm"
  smokeTimeMin: number | null;
  priceEUR: number | null;
  url: string | null; // link na proizvod (humidor.hr)
  // Generic family (Robusto, Toro, …). When the maker uses the generic name, name === shape.
  shape?: string;
  ring?: number;
  lengthMM?: number;
  // ISO datum (YYYY-MM-DD) kad je priceEUR preuzet iz HR trgovine.
  fetchedAt?: string;
  // Linkovi na proizvod te KONKRETNE vitole po regiji (market katalog) — kad
  // korisnik izabere vitolu, kupnja/cijena vode na tu vitolu, ne na liniju.
  regionLinks?: Partial<Record<Region, { shop: string; url: string; priceEUR?: number; priceApprox?: boolean; fetchedAt?: string }>>;
}

export interface Cigar {
  id: string;
  brand: string;
  line: string;
  vitola: string; // default vitola
  format: string;
  country: string;
  wrapper: string;
  /** Display label for binder (variety / shop string), when known. */
  binder?: string;
  /** Display label for filler (variety / shop string), when known. */
  filler?: string;
  /** Country of wrapper leaf (HR name, aligned with `country`). */
  wrapperOrigin?: string;
  /** Country of binder leaf. */
  binderOrigin?: string;
  /** Country of filler leaf (single-country only; multi-origin left unset for puro). */
  fillerOrigin?: string;
  /**
   * true = all three origins known and equal;
   * false = all three known and not equal;
   * null/absent = incomplete leaf origins.
   */
  isPuro?: boolean | null;
  strength: number; // 1-5 (nikotin)
  body: number; // 1-5 (punoca dima)
  flavorTags: string[];
  profileEstimated?: boolean; // profil izveden heuristikom (profile-cigars.py), ne degustacijom
  smokeTimeMin: number;
  priceEUR: number | null;
  priceApprox?: boolean;
  priceUrl?: string | null; // izvor cijene / gdje kupiti
  vitolas: Vitola[];
  /**
   * Runtime oznaka (NIJE u JSON-u): ime vitole koju je korisnik izabrao iz
   * linije s više formata — postavlja `applyVitola`. Ključ stanja kolekcije i
   * dnevnika gradi se iz nje (`lib/cigarItemId`) da Churchill i Corona iste
   * linije ne dijele "Imam / Probao / ocjenu".
   */
  selectedVitola?: string;
  markets: Market[]; // gdje se moze kupiti
  // Izravan link na proizvod + cijena po regiji (iz stvarnog scrape-a trgovina).
  // HR/EU/USA gdje postoji; EU/USA cijena je "od" na razini linije, USD->EUR
  // konverzija nosi priceApprox. Embargo: kubanke nemaju USA.
  regionLinks?: Partial<Record<Region, { shop: string; url: string; priceEUR?: number; priceApprox?: boolean; fetchedAt?: string }>>;
  // "market" = generirano iz scrape-a trgovina (build-market-cigars.py), za razliku
  // od kuriranih unosa; idempotentno regenerirano. Vidi Faza B/C playbook.
  catalogSource?: "market";
  formatEstimated?: boolean; // duljina procijenjena iz vitole (shop bez dimenzije)
  strengthFromShop?: boolean; // snaga iz stvarnog shop-ocjenjivanja, ne heuristike
  flavoured?: boolean; // aromatizirana/infuzirana (shop oznaka)
  sourceUrls?: string[];
  availabilityHR: string[];
  notes: LocalizedText;
  // Za samplere/gift-packove: popis linija cigara koje pakiranje sadrzi.
  lineup?: string[];
}

export interface PairingReason {
  rule: string;
  text: LocalizedText;
  score: number;
}

export interface PairingResult<T> {
  item: T;
  /** Prikazni rezultat: zaokružen i stisnut na 0–100. */
  score: number;
  /**
   * Rezultat prije zaokruživanja i stiskanja — jedini koji smije rangirati.
   * Zbroj pravila zna prijeći 100 (base + body + note + kontrast + wrapper…),
   * pa je prikazni rezultat zasićen: desetak pića završi na istih 100 i onda o
   * pobjedniku odlučuje razrješenje neriješenog (kvaliteta), ne slaganje s
   * cigarom. Zato se sortira i "soft band" računa po ovome.
   */
  rawScore: number;
  reasons: PairingReason[];
}
