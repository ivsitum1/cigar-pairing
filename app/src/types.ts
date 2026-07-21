// Zajednicki tipovi podataka — odgovaraju JSON shemama u src/data/

export type Lang = "hr" | "en";

export type DrinkCategory =
  | "rum"
  | "whisky"
  | "brandy"
  | "wine"
  | "coffee"
  | "tequila"
  | "gin";

export type Market = "HR" | "EU" | "USA" | "WW";

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
}

export interface Cigar {
  id: string;
  brand: string;
  line: string;
  vitola: string; // default vitola
  format: string;
  country: string;
  wrapper: string;
  strength: number; // 1-5 (nikotin)
  body: number; // 1-5 (punoca dima)
  flavorTags: string[];
  profileEstimated?: boolean; // profil izveden heuristikom (profile-cigars.py), ne degustacijom
  smokeTimeMin: number;
  priceEUR: number | null;
  priceApprox?: boolean;
  priceUrl?: string | null; // izvor cijene / gdje kupiti
  vitolas: Vitola[];
  markets: Market[]; // gdje se moze kupiti
  // Izravan link na proizvod + cijena po regiji (iz stvarnog scrape-a trgovina).
  // HR/EU/USA gdje postoji; EU/USA cijena je "od" na razini linije, USD->EUR
  // konverzija nosi priceApprox. Embargo: kubanke nemaju USA.
  regionLinks?: Partial<Record<Region, { shop: string; url: string; priceEUR?: number; priceApprox?: boolean }>>;
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
  score: number;
  reasons: PairingReason[];
}
