// Zajednicki tipovi podataka — odgovaraju JSON shemama u src/data/

export type Lang = "hr" | "en";

export type DrinkCategory = "rum" | "whisky" | "brandy" | "gin" | "coffee";

export type Market = "HR" | "EU" | "USA" | "WW";

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
  additiveDetail?: string;
  additiveSource?: string;
  qualityScore: number | null;
  priceEUR: PriceRange | null;
  priceApprox?: boolean;
  shopHR: string;
  status?: string | null; // META / IMAS / PROBAO iz Excela
  pairable: boolean;
  serving: Serving;
  cigarHint?: string | null;
  priceUrl?: string | null; // izvor cijene / gdje kupiti
  notes: LocalizedText;
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
  smokeTimeMin: number;
  priceEUR: number | null;
  priceApprox?: boolean;
  priceUrl?: string | null; // izvor cijene / gdje kupiti
  vitolas: Vitola[];
  markets: Market[]; // gdje se moze kupiti
  availabilityHR: string[];
  notes: LocalizedText;
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
