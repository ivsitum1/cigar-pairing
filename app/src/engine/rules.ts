// Kalibracija pairing enginea — tezine i tablice komplementarnih okusa.
// Mijenjaj ovdje ako zelis drugacije ponasanje prijedloga.

import type { Lang, LocalizedText } from "../types";

export const WEIGHTS = {
  base: 36,
  bodyPerStep: 12, // kazna po koraku razlike tijela (0 razlike = pun bonus)
  bodyBonus: 18, // bonus za savrseni body match
  overwhelmPenalty: 12, // jaka cigara (4+) uz lagano pice (<=2)
  tagOverlap: 7, // po zajednickom tagu (cap 3)
  tagComplement: 5, // po komplementarnom paru (cap 3)
  contrastSweetMaduro: 14,
  wrapperMatch: 10,
  strengthPowerMatch: 8, // overproof/dim pice + jaka cigara
  strengthPowerMismatch: 10, // overproof pice + blaga cigara (kazna)
  qualityNudge: 2, // * (qualityScore - 7)
  curatedHintMinScore: 80,
  curatedWarnMaxScore: 45, // ispod ovoga kurirana poruka smije biti negativna
  personal: 5, // max nudge iz dnevnika (stil pica / brend cigare), po smjeru
  formatComplexityBonus: 0, // B2 (eksperimentalno, default 0=iskljuceno): duga cigara + kompleksno pice
};

// sinonimi/varijante iz scrape podataka -> kanonski tag koji engine boduje
// (podaci se regeneriraju iz Excela pa se normalizacija radi ovdje, ne u JSON-u)
export const TAG_ALIASES: Record<string, string> = {
  "začini": "zacini",
  cokolada: "kakao",
  jod: "dim",
  iodin: "dim",
  medicinski: "dim",
  slane: "mineralno",
  sol: "mineralno",
  juniper: "travnato",
  koriander: "zacini",
  cimet: "zacini-slatki",
  maple: "karamela",
  orah: "orasasti",
  naranca: "citrus",
  grozdje: "voce",
  menta: "travnato",
  mediterran: "travnato",
  mesnato: "zemljano",
  mizunara: "hrast",
  prune: "suho-voce",
  borovnica: "tamno-voce",
  ribiz: "voce",
  gladak: "kremasto",
  viski: "hrast",
};

export const normalizeTag = (t: string): string => TAG_ALIASES[t] ?? t;

export const normalizeTags = (tags: string[]): string[] => [
  ...new Set(tags.map(normalizeTag)),
];

// cigar tag -> komplementarni tagovi u picu
export const COMPLEMENTS: Record<string, string[]> = {
  kakao: ["kava", "karamela", "melasa", "tamno-voce", "slatko", "gorko", "kakao"],
  kava: ["kakao", "karamela", "zemljano", "gorko", "kava", "melasa"],
  kremasto: ["vanilija", "med", "karamela", "kokos", "mlijeko", "kremasto"],
  zemljano: ["hrast", "koza", "dim", "zemljano", "duhan", "gorko"],
  papar: ["overproof", "zacini", "ester-funk", "dim", "papar"],
  zacini: ["zacini", "suho-voce", "hrast", "vanilija", "zacini-slatki"],
  "zacini-slatki": ["karamela", "vanilija", "med", "kakao", "zacini"],
  cedar: ["hrast", "drvo", "vanilija", "citrus", "cedar"],
  drvo: ["hrast", "drvo", "vanilija"],
  med: ["med", "karamela", "cvjetno", "voce", "caj"],
  citrus: ["citrus", "travnato", "trava-slatka", "voce", "cvjetno"],
  "trava-slatka": ["travnato", "vegetalno", "citrus", "caj", "cvjetno"],
  cvjetno: ["cvjetno", "caj", "citrus", "med", "voce"],
  koza: ["koza", "dim", "tamno-voce", "duhan", "zemljano"],
  duhan: ["duhan", "koza", "zemljano", "kava", "melasa"],
  "tamno-voce": ["suho-voce", "tamno-voce", "melasa", "vino", "kakao"],
  orasasti: ["orasasti", "karamela", "med", "psenica", "kremasto"],
  slatko: ["melasa", "karamela", "slatko", "med", "vanilija"],
  dim: ["dim", "overproof", "zemljano", "ester-funk"],
  karamela: ["karamela", "melasa", "med", "vanilija", "slatko"],
  voce: ["voce", "suho-voce", "citrus", "tropsko-voce"],
  mineralno: ["mineralno", "citrus", "dim"],
  jabuka: ["jabuka", "voce", "med"],
  agava: ["agava", "citrus", "papar", "biljno", "zemljano", "vanilija"],
  biljno: ["biljno", "agava", "travnato", "citrus", "vegetalno"],
  mlijeko: ["mlijeko", "kremasto", "vanilija", "kakao", "slatko"],
};

// wrapper (regex) -> drink stilovi/tagovi koji mu prirodno pasu
export const WRAPPER_AFFINITY: {
  wrapper: RegExp;
  styles: string[];
  tags: string[];
  labelHr: string;
  labelEn: string;
}[] = [
  {
    wrapper: /connecticut|claro/i,
    styles: ["agricole", "filter-light", "cognac-vs", "cognac-vsop", "irish-blend", "milk", "vinjak", "speyside-fruity", "japanese", "contemporary", "london-dry", "premium-dry", "plymouth", "sparkling", "white-fresh", "white-rich"],
    tags: ["travnato", "cvjetno", "kremasto", "med", "citrus"],
    labelHr: "Connecticut wrapper voli lagana, svježa i kremasta pića",
    labelEn: "Connecticut wrappers love light, fresh and creamy drinks",
  },
  {
    wrapper: /maduro|oscuro|san andr|broadleaf|brazil/i,
    styles: ["demerara", "solera", "espresso-dark", "espresso-medium", "filter-dark", "brandy-de-jerez", "turkish", "moka", "bourbon", "navy-strength", "port-ruby", "sherry-sweet", "madeira", "prosek", "red-full", "dessert-wine"],
    tags: ["melasa", "kakao", "kava", "karamela", "tamno-voce", "slatko"],
    labelHr: "Maduro/oscuro wrapper (kakao, kava) traži tamna i bogata pića",
    labelEn: "Maduro/oscuro wrappers (cocoa, coffee) call for dark, rich drinks",
  },
  {
    wrapper: /habano|corojo|sumatra|cameroon/i,
    styles: ["jamaica", "islay-peated", "speyside-sherry", "espresso-dark", "cognac-xo", "armagnac", "rye", "campbeltown", "croatian", "red-full", "red-medium", "port-tawny", "sherry-dry"],
    tags: ["zacini", "dim", "suho-voce", "hrast", "ester-funk"],
    labelHr: "Habano/corojo wrapper podnosi začinska i dimna pića",
    labelEn: "Habano/corojo wrappers stand up to spicy and smoky drinks",
  },
];

// tagovi koje engine posebno boduje u pravilu snage (pairing.ts, pravilo 5)
export const POWER_TAGS = ["overproof", "dim", "ester-funk"] as const;

// puni vokabular tagova koje engine boduje — integrity test provjerava da
// svaki tag u podacima (nakon normalizacije) pripada ovom skupu
export const KNOWN_TAGS: Set<string> = new Set([
  ...Object.keys(COMPLEMENTS),
  ...Object.values(COMPLEMENTS).flat(),
  ...WRAPPER_AFFINITY.flatMap((w) => w.tags),
  ...POWER_TAGS,
]);

// Prikazni nazivi kanonskih tagova (chipovi + reason tekstovi).
// Ključ = kanonski ID; integrity test traži unos za svaki član KNOWN_TAGS.
export const TAG_LABELS: Record<string, LocalizedText> = {
  agava: { hr: "agava", en: "agave" },
  biljno: { hr: "biljno", en: "herbal" },
  caj: { hr: "čaj", en: "tea" },
  cedar: { hr: "cedar", en: "cedar" },
  citrus: { hr: "citrus", en: "citrus" },
  cvjetno: { hr: "cvjetno", en: "floral" },
  dim: { hr: "dim", en: "smoke" },
  drvo: { hr: "drvo", en: "wood" },
  duhan: { hr: "duhan", en: "tobacco" },
  "ester-funk": { hr: "ester-funk", en: "ester funk" },
  gorko: { hr: "gorko", en: "bitter" },
  hrast: { hr: "hrast", en: "oak" },
  jabuka: { hr: "jabuka", en: "apple" },
  kakao: { hr: "kakao", en: "cocoa" },
  karamela: { hr: "karamela", en: "caramel" },
  kava: { hr: "kava", en: "coffee" },
  kokos: { hr: "kokos", en: "coconut" },
  koza: { hr: "koža", en: "leather" },
  kremasto: { hr: "kremasto", en: "creamy" },
  med: { hr: "med", en: "honey" },
  melasa: { hr: "melasa", en: "molasses" },
  mineralno: { hr: "mineralno", en: "mineral" },
  mlijeko: { hr: "mlijeko", en: "milk" },
  orasasti: { hr: "orašasti", en: "nutty" },
  overproof: { hr: "overproof", en: "overproof" },
  papar: { hr: "papar", en: "pepper" },
  psenica: { hr: "pšenica", en: "wheat" },
  slatko: { hr: "slatko", en: "sweet" },
  "suho-voce": { hr: "suho voće", en: "dried fruit" },
  "tamno-voce": { hr: "tamno voće", en: "dark fruit" },
  "trava-slatka": { hr: "slatka trava", en: "sweet grass" },
  travnato: { hr: "travnato", en: "grassy" },
  "tropsko-voce": { hr: "tropsko voće", en: "tropical fruit" },
  vanilija: { hr: "vanilija", en: "vanilla" },
  vegetalno: { hr: "vegetalno", en: "vegetal" },
  vino: { hr: "vino", en: "wine" },
  voce: { hr: "voće", en: "fruit" },
  zacini: { hr: "začini", en: "spices" },
  "zacini-slatki": { hr: "slatki začini", en: "sweet spices" },
  zemljano: { hr: "zemljano", en: "earthy" },
};

/** Lokalizirani prikaz flavor taga (nakon aliasa → kanonski ID). */
export function flavorLabel(tag: string, lang: Lang): string {
  const canonical = normalizeTag(tag);
  const entry = TAG_LABELS[canonical];
  if (!entry) return tag;
  return entry[lang] || entry.hr || tag;
}
