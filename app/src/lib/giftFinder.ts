// Poklon u nekoliko pitanja — odgovori postaju filteri nad postojećim katalogom
// i pairing engineom. Bez novog modela bodovanja; cijena i blizina trgovine su
// tvrdi uvjeti (poklon bez cijene nije poklon).
// Polica i način odabira boce (rupa / vrh / omjer) dolaze iz pitanja, ne iz
// tuđe kolekcije — isti bucketi i ranking kao na Kupnji.
//
// Tri pravila drže kvalitetu prijedloga:
//  1. Kombinacija cigare i pića ide van samo ako slaganje prijeđe MIN_PAIRING_SCORE.
//  2. Kad u traženoj kategoriji pića nema ni jednog pogotka, spušta se na
//     SUSJEDNU kategoriju (whisky → brandy → rum → vino), pa tek onda mijenja
//     oblik poklona.
//  3. Kad su svih pet odgovora „ne znam”, ne radi se presjek praznih filtera
//     nego se bira namjerno siguran profil (SAFE_DEFAULT_ANSWERS).
import type { Cigar, Drink, DrinkCategory, LocalizedText, Region, RegionFilter } from "../types";
import { cigarLinePrice } from "./cigarPrice";
import { cigarAvailableInRegion } from "./cigarAvailability";
import { pairDrinksForCigar } from "../engine/pairing";
import { pairingBlurb } from "../engine/pairingExplain";
import { cigarShapes, type ShapeFamily } from "./vitolaShape";
import {
  BUCKETS,
  drinkByQuality,
  drinkValueScore,
  type StyleBucket,
} from "./shoppingPicks";

export type GiftRecipient = "regular" | "beginner" | "drinks-only" | "unknown";
export type GiftBudget = "under20" | "20to40" | "40to60" | "60to100" | "over100" | "unknown";
export type GiftDrinkPref = DrinkCategory | "unknown";
export type GiftIntensity = "mild" | "medium" | "bold" | "unknown";
export type GiftShape = "cigar" | "bottle" | "pairing" | "unknown";
export type GiftDrinkPick = "gap" | "top" | "value" | "unknown";

/** Q6 „ništa od toga” — svi segmenti su rupe, nije isto što i „ne znam”. */
export const OWNED_STYLES_NONE = "none";

export interface GiftAnswers {
  recipient: GiftRecipient;
  budget: GiftBudget;
  drink: GiftDrinkPref;
  intensity: GiftIntensity;
  shape: GiftShape;
  /** Bucket id-evi s police; prazno = ne znam; `OWNED_STYLES_NONE` = ništa od toga. */
  ownedStyles?: string[];
  drinkPick?: GiftDrinkPick;
}

export type GiftPickKind = "cigar" | "drink" | "pairing";

export interface GiftAccessoryLink {
  label: LocalizedText;
  url: string;
}

export interface GiftPick {
  id: string;
  kind: GiftPickKind;
  cigar?: Cigar;
  cigars?: Cigar[];
  drink?: Drink;
  accessories?: GiftAccessoryLink[];
  price: number | null;
  shop: string | null;
  why: LocalizedText;
  fellBackBudget?: boolean;
  /** Postotak slaganja para (samo kind === "pairing"); uvijek ≥ MIN_PAIRING_SCORE. */
  matchScore?: number;
  /** Kategorija pića koju je korisnik tražio, kad u njoj nije bilo pogotka. */
  swappedFromCategory?: DrinkCategory;
  /** Tražena je kombinacija, ali nijedna nije prešla prag — ide zasebno. */
  droppedPairing?: boolean;
  /** Svih pet odgovora „ne znam” — vrijedi siguran profil. */
  safeDefault?: boolean;
  /** Tražena je rupa, ali svi navedeni stilovi već su na polici. */
  noGapLeft?: boolean;
  /** Segment iz kojeg dolazi boca (rupa / objašnjenje na kartici). */
  styleBucket?: StyleBucket;
  region: Region;
}

export interface GiftCatalog {
  cigars: Cigar[];
  drinks: Drink[];
}

interface BudgetBand {
  min: number;
  max: number | null;
}

const BUDGET_BANDS: Record<Exclude<GiftBudget, "unknown">, BudgetBand> = {
  under20: { min: 0, max: 20 },
  "20to40": { min: 20, max: 40 },
  "40to60": { min: 40, max: 60 },
  "60to100": { min: 60, max: 100 },
  over100: { min: 100, max: null },
};

const BUDGET_FALLBACK: Partial<Record<GiftBudget, GiftBudget>> = {
  over100: "60to100",
  "60to100": "40to60",
  "40to60": "20to40",
  "20to40": "under20",
};

const BEGINNER_SHAPES = new Set<ShapeFamily>(["corona", "robusto"]);

/** Poklon nije svakodnevni bundle. Pića imaju 1–10; cigare taj broj nemaju,
 *  pa uz cijenu i trgovinu ispadaju bundle/value linije i aromatizirane. */
export const MIN_GIFT_QUALITY = 7;

/** Kombinacija koja „ne ide” gori je poklon od dvije zasebne stvari koje idu.
 *  Prag je na prikaznoj skali sparivanja (ista brojka koju korisnik vidi kao
 *  postotak), pa ono što piše na kartici i ono što filtrira jest isti broj. */
export const MIN_PAIRING_SCORE = 80;

/** Koliko se cigara i pića boduje po budžetnom pojasu. Prag od 80 % traži da se
 *  pretraži više od prvog pogotka, ali ne cijeli katalog (≈220 000 parova).
 *  Mjereno na HR poolu: ove brojke daju jednak broj parova kao neograničeno
 *  skeniranje, uz najgori slučaj od ~24 000 bodovanja (≈0,2 s) po pojasu. */
const PAIR_CIGAR_SCAN = 120;
const PAIR_DRINK_SCAN = 200;

/** Kad korisnik ne zna što osoba pije, ne nudimo gin ni kavu — poklon-boca bez
 *  informacije o ukusu ostaje u klasičnim kategorijama. */
const CLASSIC_GIFT_CATEGORIES: DrinkCategory[] = ["whisky", "rum", "brandy", "wine"];

/** Susjedstvo kategorija: bačvom zrele žestice su međusobno najbliže, vino i
 *  porto sjede uz brandy. Redoslijed je „sljedeći najbliži”, ne abecedni. */
const CATEGORY_NEIGHBOURS: Record<DrinkCategory, DrinkCategory[]> = {
  whisky: ["brandy", "rum", "wine"],
  rum: ["brandy", "whisky", "wine"],
  brandy: ["whisky", "rum", "wine"],
  wine: ["brandy", "rum", "whisky"],
  tequila: ["rum", "whisky", "brandy"],
  gin: ["tequila", "whisky", "rum"],
  digestif: ["brandy", "wine", "rum"],
  coffee: ["rum", "brandy", "whisky"],
};

export function neighbourCategories(cat: DrinkCategory): DrinkCategory[] {
  return CATEGORY_NEIGHBOURS[cat] ?? [];
}

/** Polica i način odabira boce imaju smisla samo kad znamo kategoriju i
 *  poklon nije sama cigara. */
export function giftShelfApplies(answers: GiftAnswers): boolean {
  return answers.drink !== "unknown" && answers.shape !== "cigar";
}

export type GiftWizardStep =
  | "recipient"
  | "budget"
  | "intensity"
  | "drink"
  | "shape"
  | "ownedStyles"
  | "drinkPick";

const CORE_WIZARD_STEPS: GiftWizardStep[] = [
  "recipient",
  "budget",
  "intensity",
  "drink",
  "shape",
];

export function visibleGiftSteps(answers: GiftAnswers): GiftWizardStep[] {
  if (giftShelfApplies(answers)) return [...CORE_WIZARD_STEPS, "ownedStyles", "drinkPick"];
  return CORE_WIZARD_STEPS;
}

export function ownedStyleIds(answers: GiftAnswers): string[] {
  return answers.ownedStyles ?? [];
}

/** `unknown` + označena polica ponaša se kao rupa. */
export function resolveDrinkPick(answers: GiftAnswers): GiftDrinkPick {
  const pick = answers.drinkPick ?? "unknown";
  if (pick !== "unknown") return pick;
  return ownedStyleIds(answers).length > 0 ? "gap" : "unknown";
}

export function bucketForDrink(d: Drink): StyleBucket | undefined {
  return (BUCKETS[d.category] ?? []).find((b) => b.styles.includes(d.style));
}

/**
 * Segmenti iz kojih smije doći boca-rupa.
 * Prazna polica („ne znam”) preskače prvi, najčešći bucket.
 * `OWNED_STYLES_NONE` otvara sve buckete.
 */
export function uncoveredStyleBuckets(
  category: DrinkCategory,
  ownedStyles: string[],
): StyleBucket[] {
  const buckets = BUCKETS[category] ?? [];
  if (ownedStyles.includes(OWNED_STYLES_NONE)) return buckets;
  if (ownedStyles.length === 0) return buckets.slice(1);
  return buckets.filter((b) => !ownedStyles.includes(b.id));
}

function drinkInBuckets(d: Drink, buckets: StyleBucket[]): boolean {
  return buckets.some((b) => b.styles.includes(d.style));
}

function sortDrinksForPick(pool: Drink[], pick: GiftDrinkPick): Drink[] {
  if (pick === "value" || pick === "gap") {
    return [...pool].sort(
      (a, b) => drinkValueScore(b) - drinkValueScore(a) || drinkByQuality(a, b),
    );
  }
  return [...pool].sort(drinkByQuality);
}

function gapWhy(bucket: StyleBucket): LocalizedText {
  return {
    hr: `Na polici još nema segmenta „${bucket.label.hr}” — ovo ga pokriva.`,
    en: `The “${bucket.label.en}” segment is still open — this covers it.`,
  };
}

function topWhy(): LocalizedText {
  return {
    hr: "Vrh kategorije u ovom rasponu.",
    en: "Top of the category in this band.",
  };
}

function valueWhy(): LocalizedText {
  return {
    hr: "Najbolji omjer cijene i kvalitete u ovom rasponu.",
    en: "Best value for money in this band.",
  };
}

function drinkWhy(
  drink: Drink,
  pick: GiftDrinkPick,
  noGapLeft: boolean,
): { why: LocalizedText; styleBucket?: StyleBucket; noGapLeft?: boolean } {
  const bucket = bucketForDrink(drink);
  if (pick === "gap" && !noGapLeft && bucket) {
    return { why: gapWhy(bucket), styleBucket: bucket };
  }
  if (pick === "top" || noGapLeft) {
    return { why: topWhy(), styleBucket: bucket, ...(noGapLeft ? { noGapLeft: true } : null) };
  }
  if (pick === "value") {
    return { why: valueWhy(), styleBucket: bucket };
  }
  return { why: drink.notes, styleBucket: bucket };
}

/** Svih pet „ne znam”. Prazan presjek filtera dao bi nasumičan rezultat, pa se
 *  taj slučaj rješava jednim namjerno odabranim profilom (vidi
 *  SAFE_DEFAULT_ANSWERS), a prijedlozi nose oznaku safeDefault. */
export function isBlankGiftAnswers(a: GiftAnswers): boolean {
  return (
    a.recipient === "unknown" &&
    a.budget === "unknown" &&
    a.drink === "unknown" &&
    a.intensity === "unknown" &&
    a.shape === "unknown"
  );
}

/** Siguran poklon za osobu o kojoj ne znamo ništa:
 *  - recipient „unknown” → snaga do 3 i klasičan format (corona/robusto),
 *  - intensity „medium” → sredina ljestvice, ondje je najviše parova iznad praga,
 *  - budget „unknown” → 20–40 € (isti default kao i inače),
 *  - drink „unknown” → samo klasične kategorije,
 *  - redoslijed prijedloga: kombinacija (ako prijeđe prag) → boca → cigara,
 *    jer ne znamo ni puši li osoba, a boca radi u oba slučaja. */
const SAFE_DEFAULT_ANSWERS: GiftAnswers = {
  recipient: "unknown",
  budget: "unknown",
  drink: "unknown",
  intensity: "medium",
  shape: "unknown",
};

const BARGAIN_LINE = /\bbundle\b|\bvalue\b|closeout|\bseconds\b|\bbudget\b/i;

/** Za „u blizini”: ALL tretiramo kao HR (domaće trgovine). */
export function giftRegion(market: RegionFilter): Region {
  return market === "ALL" || market === "HR" ? "HR" : market;
}

function drinkMid(d: Drink): number | null {
  if (!d.priceEUR) return null;
  return (d.priceEUR.min + d.priceEUR.max) / 2;
}

function cigarPrice(c: Cigar, region: Region): number | null {
  return cigarLinePrice(c, region).price;
}

function cigarShopName(c: Cigar, region: Region): string | null {
  if (region === "HR") return c.availabilityHR[0] ?? null;
  return c.regionLinks?.[region]?.shop ?? null;
}

export function cigarGiftEligible(c: Cigar, region: Region): boolean {
  // Samo cigare s poznatom cijenom (~10 % kataloga). Neprijedložena cigara
  // nije poklon — praznina se rješava scrapom, ne mekšim filterom.
  if (cigarPrice(c, region) == null) return false;
  if (c.flavoured) return false;
  if (BARGAIN_LINE.test(`${c.brand} ${c.line}`)) return false;
  const scored = c.qualityScore;
  if (scored != null && scored < MIN_GIFT_QUALITY) return false;
  if (region === "HR") return c.availabilityHR.length > 0;
  return cigarAvailableInRegion(c, region);
}

export function drinkGiftEligible(d: Drink, region: Region): boolean {
  if (!d.pairable || drinkMid(d) == null) return false;
  if (d.qualityScore == null || d.qualityScore < MIN_GIFT_QUALITY) return false;
  if (region === "HR") return Boolean(d.shopHR?.trim());
  return d.priceEUR != null;
}

function inBudget(price: number, band: BudgetBand): boolean {
  if (price < band.min - 0.01) return false;
  if (band.max != null && price > band.max + 0.01) return false;
  return true;
}

function resolveBudget(budget: GiftBudget): BudgetBand {
  if (budget === "unknown") return BUDGET_BANDS["20to40"];
  return BUDGET_BANDS[budget];
}

function filterByBudget<T>(
  items: T[],
  priceOf: (t: T) => number | null,
  budget: GiftBudget,
  allowCheaper: boolean,
): { items: T[]; fellBack: boolean } {
  let band = resolveBudget(budget);
  let fellBack = false;
  let currentBudget = budget;
  let filtered = items.filter((x) => {
    const p = priceOf(x);
    return p != null && inBudget(p, band);
  });
  while (allowCheaper && filtered.length === 0 && currentBudget !== "unknown") {
    const next = BUDGET_FALLBACK[currentBudget];
    if (!next) break;
    currentBudget = next;
    band = resolveBudget(currentBudget);
    fellBack = true;
    filtered = items.filter((x) => {
      const p = priceOf(x);
      return p != null && inBudget(p, band);
    });
  }
  return { items: filtered, fellBack };
}

function recipientStrengthCap(recipient: GiftRecipient): number | null {
  if (recipient === "beginner" || recipient === "unknown") return 3;
  return null;
}

function intensityStrengthRange(intensity: GiftIntensity): { min: number; max: number } {
  switch (intensity) {
    case "mild":
      return { min: 1, max: 2 };
    case "bold":
      return { min: 4, max: 5 };
    case "medium":
      return { min: 3, max: 3 };
    case "unknown":
      return { min: 2, max: 4 };
    default: {
      const _exhaustive: never = intensity;
      return _exhaustive;
    }
  }
}

function intensityBodyRange(intensity: GiftIntensity): { min: number; max: number } {
  return intensityStrengthRange(intensity);
}

/** Jačina cigare mora poštovati i odgovor „kakav je navečer” i strop primatelja.
 *  Kad se ne sijeku („tek je na početku” + „voli jače stvari”), strop pobjeđuje,
 *  ali se traži najjače što je unutar njega — inače bi presjek bio prazan i
 *  proturječan par odgovora ne bi dao ništa. */
function cigarStrengthRange(
  recipient: GiftRecipient,
  intensity: GiftIntensity,
): { min: number; max: number } {
  const { min, max } = intensityStrengthRange(intensity);
  const cap = recipientStrengthCap(recipient);
  if (cap == null) return { min, max };
  if (min > cap) return { min: cap, max: cap };
  return { min, max: Math.min(max, cap) };
}

function cigarMatchesIntensity(c: Cigar, recipient: GiftRecipient, intensity: GiftIntensity): boolean {
  const { min, max } = cigarStrengthRange(recipient, intensity);
  return c.strength >= min && c.strength <= max;
}

function drinkMatchesIntensity(d: Drink, intensity: GiftIntensity): boolean {
  const { min, max } = intensityBodyRange(intensity);
  return d.body >= min && d.body <= max;
}

function cigarMatchesRecipient(c: Cigar, recipient: GiftRecipient): boolean {
  if (recipient === "beginner" || recipient === "unknown") {
    const shapes = cigarShapes(c);
    if (shapes.size > 0 && ![...shapes].some((s) => BEGINNER_SHAPES.has(s))) return false;
  }
  return true;
}

interface DrinkPoolOpts {
  ignoreIntensity?: boolean;
  ownedStyles?: string[];
  drinkPick?: GiftDrinkPick;
}

function gapBucketsForPref(
  pref: GiftDrinkPref,
  ownedStyles: string[],
): { buckets: StyleBucket[]; noGapLeft: boolean } {
  if (pref === "unknown") return { buckets: [], noGapLeft: false };
  const all = BUCKETS[pref] ?? [];
  const uncovered = uncoveredStyleBuckets(pref, ownedStyles);
  if (all.length > 0 && uncovered.length === 0) {
    return { buckets: [], noGapLeft: true };
  }
  return { buckets: uncovered, noGapLeft: false };
}

function drinkPool(
  drinks: Drink[],
  pref: GiftDrinkPref,
  region: Region,
  intensity: GiftIntensity,
  opts?: DrinkPoolOpts,
): Drink[] {
  let pool = drinks.filter((d) => drinkGiftEligible(d, region));
  if (pref !== "unknown") pool = pool.filter((d) => d.category === pref);
  else pool = pool.filter((d) => CLASSIC_GIFT_CATEGORIES.includes(d.category));
  if (!opts?.ignoreIntensity) pool = pool.filter((d) => drinkMatchesIntensity(d, intensity));

  const pick = resolveDrinkPick({
    recipient: "unknown",
    budget: "unknown",
    drink: pref,
    intensity,
    shape: "bottle",
    ownedStyles: opts?.ownedStyles,
    drinkPick: opts?.drinkPick,
  });
  let effectivePick = pick;
  if (pick === "gap") {
    const gap = gapBucketsForPref(pref, opts?.ownedStyles ?? []);
    if (gap.noGapLeft) effectivePick = "top";
    else if (gap.buckets.length > 0) {
      const narrowed = pool.filter((d) => drinkInBuckets(d, gap.buckets));
      if (narrowed.length > 0) pool = narrowed;
    }
  }
  return sortDrinksForPick(pool, effectivePick);
}

function cigarPool(
  cigars: Cigar[],
  region: Region,
  recipient: GiftRecipient,
  intensity: GiftIntensity,
): Cigar[] {
  return cigars
    .filter(
      (c) =>
        cigarGiftEligible(c, region) &&
        cigarMatchesRecipient(c, recipient) &&
        cigarMatchesIntensity(c, recipient, intensity),
    )
    .sort(
      (a, b) =>
        intensityCenterDist(a.strength, recipient, intensity) -
          intensityCenterDist(b.strength, recipient, intensity) ||
        (cigarPrice(b, region) ?? 0) - (cigarPrice(a, region) ?? 0),
    );
}

function intensityCenterDist(
  value: number,
  recipient: GiftRecipient,
  intensity: GiftIntensity,
): number {
  const { min, max } = cigarStrengthRange(recipient, intensity);
  const center = (min + max) / 2;
  return Math.abs(value - center);
}

/** Kombinacije iznad praga slaganja, najviše `limit` komada.
 *
 *  Jačinu nosi CIGARA (odgovor „kakav je navečer”), a piće bira pairing engine:
 *  dvostruki filter po jačini izbacivao bi upravo parove koje pravilo body-match
 *  najbolje ocjenjuje (npr. srednja cigara + puno piće). Prag od 80 % ionako
 *  jamči da se tijela slažu. */
function pairingPicks(
  cigars: Cigar[],
  drinks: Drink[],
  answers: GiftAnswers,
  region: Region,
  exclude: Set<string>,
  limit: number,
  allowCheaper: boolean,
): GiftPick[] {
  const cigarCandidates = cigarPool(cigars, region, answers.recipient, answers.intensity);
  const drinkCandidates = drinkPool(drinks, answers.drink, region, answers.intensity, {
    ignoreIntensity: true,
    ownedStyles: ownedStyleIds(answers),
    drinkPick: answers.drinkPick,
  }).filter((d) => !exclude.has(`d:${d.id}`));
  if (cigarCandidates.length === 0 || drinkCandidates.length === 0) return [];
  const drinkRank = new Map(drinkCandidates.map((d, i) => [d.id, i]));
  const pickMode = resolveDrinkPick(answers);
  const gap = gapBucketsForPref(answers.drink, ownedStyleIds(answers));
  const noGapLeft = pickMode === "gap" && gap.noGapLeft;

  const cheapestDrink = Math.min(...drinkCandidates.map((d) => drinkMid(d) ?? Infinity));
  const out: GiftPick[] = [];
  const usedDrinks = new Set<string>();

  let currentBudget = answers.budget;
  let fellBack = false;
  while (out.length < limit) {
    const band = resolveBudget(currentBudget);
    const ceiling = (band.max ?? Infinity) - cheapestDrink + 0.01;
    // Cigare koje same pojedu cijeli pojas preskačemo odmah — uz njih nijedno
    // piće ne stane u budžet, a trošile bi mjesta u skeniranju.
    const cigarsInBand = cigarCandidates
      .filter((c) => {
        if (exclude.has(`c:${c.id}`)) return false;
        const p = cigarPrice(c, region);
        return p != null && p <= ceiling;
      })
      .slice(0, PAIR_CIGAR_SCAN);

    for (const cigar of cigarsInBand) {
      if (out.length >= limit) break;
      const cp = cigarPrice(cigar, region)!;
      const drinksFit = drinkCandidates
        .filter((d) => {
          if (usedDrinks.has(d.id)) return false;
          const dp = drinkMid(d);
          return dp != null && inBudget(cp + dp, band);
        })
        // Tijelo pića je najjače pravilo u bodovanju, pa se prvo boduju pića
        // blizu tijela cigare — inače bi rezanje na PAIR_DRINK_SCAN odsjeklo
        // baš one koje prelaze prag.
        .sort(
          (a, b) =>
            Math.abs(a.body - cigar.body) - Math.abs(b.body - cigar.body) ||
            (drinkRank.get(a.id) ?? 9999) - (drinkRank.get(b.id) ?? 9999) ||
            (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
        )
        .slice(0, PAIR_DRINK_SCAN);
      if (drinksFit.length === 0) continue;

      const top = pairDrinksForCigar(cigar, drinksFit).find(
        (r) => r.score >= MIN_PAIRING_SCORE && !exclude.has(`pair:${cigar.id}:${r.item.id}`),
      );
      if (!top) continue;

      const dp = drinkMid(top.item)!;
      usedDrinks.add(top.item.id);
      const bucket = bucketForDrink(top.item);
      out.push({
        id: `pair:${cigar.id}:${top.item.id}`,
        kind: "pairing",
        cigar,
        drink: top.item,
        price: cp + dp,
        shop: cigarShopName(cigar, region) ?? top.item.shopHR ?? null,
        why: pairingBlurb(cigar, top.item, top.reasons, top.score),
        matchScore: top.score,
        fellBackBudget: fellBack,
        ...(noGapLeft ? { noGapLeft: true } : null),
        ...(bucket ? { styleBucket: bucket } : null),
        region,
      });
    }

    if (out.length > 0 || !allowCheaper) break;
    const next = currentBudget === "unknown" ? undefined : BUDGET_FALLBACK[currentBudget];
    if (!next) break;
    currentBudget = next;
    fellBack = true;
  }
  return out;
}

function bottlePick(
  drinks: Drink[],
  answers: GiftAnswers,
  region: Region,
  exclude: Set<string>,
  allowCheaper: boolean,
): GiftPick | null {
  const pool = drinkPool(drinks, answers.drink, region, answers.intensity, {
    ownedStyles: ownedStyleIds(answers),
    drinkPick: answers.drinkPick,
  });
  const { items, fellBack } = filterByBudget(pool, drinkMid, answers.budget, allowCheaper);
  const free = items.filter((d) => !exclude.has(`d:${d.id}`));
  // Tri prijedloga iz iste kategorije nisu izbor. Kad korisnik nije rekao što
  // osoba pije, boca radije dolazi iz kategorije koja još nije upotrijebljena.
  const drink =
    free.find((d) => !exclude.has(`cat:${d.category}`)) ?? free[0];
  if (!drink) return null;
  const pickMode = resolveDrinkPick(answers);
  const gap = gapBucketsForPref(answers.drink, ownedStyleIds(answers));
  const noGapLeft = pickMode === "gap" && gap.noGapLeft;
  const explained = drinkWhy(drink, noGapLeft ? "top" : pickMode, noGapLeft);
  return {
    id: `d:${drink.id}`,
    kind: "drink",
    drink,
    price: drinkMid(drink),
    shop: drink.shopHR ?? null,
    why: explained.why,
    fellBackBudget: fellBack,
    ...(explained.noGapLeft ? { noGapLeft: true } : null),
    ...(explained.styleBucket ? { styleBucket: explained.styleBucket } : null),
    region,
  };
}

function cigarPick(
  cigars: Cigar[],
  answers: GiftAnswers,
  region: Region,
  exclude: Set<string>,
  allowCheaper: boolean,
): GiftPick | null {
  const pool = cigarPool(cigars, region, answers.recipient, answers.intensity);
  const { items, fellBack } = filterByBudget(
    pool,
    (c) => cigarPrice(c, region),
    answers.budget,
    allowCheaper,
  );
  const cigar = items.find((c) => !exclude.has(`c:${c.id}`));
  if (!cigar) return null;
  return {
    id: `c:${cigar.id}`,
    kind: "cigar",
    cigar,
    price: cigarPrice(cigar, region),
    shop: cigarShopName(cigar, region),
    why: cigar.notes,
    fellBackBudget: fellBack,
    region,
  };
}

function resolveShape(shape: GiftShape, recipient: GiftRecipient): Exclude<GiftShape, "unknown"> {
  if (recipient === "drinks-only") return "bottle";
  if (shape !== "unknown") return shape;
  return "pairing";
}

type PickBuilder = (exclude: Set<string>) => GiftPick | GiftPick[] | null;

/** Gradi do tri prijedloga redom, s rastućim skupom već potrošenih artikala —
 *  ista cigara ne smije biti i u kombinaciji i kao samostalan prijedlog. */
function takePicks(exclude: Set<string>, builders: PickBuilder[]): GiftPick[] {
  const out: GiftPick[] = [];
  const used = new Set(exclude);
  const seenIds = new Set<string>();
  for (const build of builders) {
    if (out.length >= 3) break;
    const res = build(used);
    const list = res == null ? [] : Array.isArray(res) ? res : [res];
    for (const pick of list) {
      if (out.length >= 3) break;
      if (seenIds.has(pick.id)) continue;
      seenIds.add(pick.id);
      used.add(pick.id);
      if (pick.cigar) used.add(`c:${pick.cigar.id}`);
      if (pick.drink) {
        used.add(`d:${pick.drink.id}`);
        used.add(`cat:${pick.drink.category}`);
      }
      out.push(pick);
    }
  }
  return out;
}

const PRIMARY_KIND: Record<Exclude<GiftShape, "unknown">, GiftPickKind> = {
  cigar: "cigar",
  bottle: "drink",
  pairing: "pairing",
};

function findGiftsOnce(
  answers: GiftAnswers,
  catalog: GiftCatalog,
  region: Region,
  exclude: Set<string>,
  opts: { safeDefault: boolean; requirePrimary: boolean; allowCheaper: boolean },
): GiftPick[] {
  const shape = resolveShape(answers.shape, answers.recipient);
  const cheap = opts.allowCheaper;
  const cigar: PickBuilder = (ex) => cigarPick(catalog.cigars, answers, region, ex, cheap);
  const bottle: PickBuilder = (ex) => bottlePick(catalog.drinks, answers, region, ex, cheap);
  const pairs =
    (limit: number): PickBuilder =>
    (ex) =>
      pairingPicks(catalog.cigars, catalog.drinks, answers, region, ex, limit, cheap);

  const picks = (() => {
    if (answers.recipient === "drinks-only") return takePicks(exclude, [bottle, bottle]);
    switch (shape) {
      case "cigar":
        return takePicks(exclude, [cigar, pairs(1), bottle]);
      case "bottle":
        return takePicks(exclude, [bottle, pairs(1), cigar]);
      case "pairing":
        // Tražena je kombinacija → nudimo do tri kombinacije, a ne jednu pa
        // dvije samostalne stvari.
        //
        // Kod svih pet „ne znam” radimo obrnuto: jedna kombinacija, pa boca, pa
        // cigara. Ne znamo ni puši li osoba, pa je bolje pokriti tri različita
        // scenarija nego tri varijante istoga; boca ide ispred cigare jer radi
        // u oba slučaja.
        return takePicks(
          exclude,
          opts.safeDefault ? [pairs(1), bottle, cigar] : [pairs(3), cigar, bottle],
        );
      default: {
        const _exhaustive: never = shape;
        return _exhaustive;
      }
    }
  })();

  // Dok ljestvica popuštanja još ima koraka, pokušaj se broji kao neuspješan
  // ako nema traženog oblika: inače bi cigara „za popunu” pojela korak u kojem
  // bi susjedna kategorija dala pravu kombinaciju.
  if (opts.requirePrimary) {
    const wanted =
      answers.recipient === "drinks-only" ? "drink" : PRIMARY_KIND[shape];
    if (!picks.some((p) => p.kind === wanted)) return [];
  }
  return picks;
}

interface GiftAttempt {
  answers: GiftAnswers;
  /** Tražena kategorija pića, kad se odstupilo od nje. */
  swappedFromCategory?: DrinkCategory;
  /** Kombinacija je pala ispod praga, pa se cigara i piće nude zasebno. */
  droppedPairing?: boolean;
  /** Smije se sići u niži cjenovni pojas (nikad u viši). */
  allowCheaper?: boolean;
  /** Zadnji koraci uzimaju što god ima — bolje išta nego prazan ekran. */
  lenient?: boolean;
}

/** Ljestvica popuštanja. Redoslijed nije slučajan — ide od najmanjeg ustupka
 *  prema najvećem:
 *
 *    1. sve točno kako je rečeno,
 *    2. SUSJEDNA kategorija pića (pa bilo koja klasična) — isti budžet, ista jačina,
 *    3. isto to, ali s niže police (nikad skuplje od odgovora),
 *    4. drugi OBLIK poklona (kombinacija → cigara i boca zasebno).
 *
 *  Zamjena kategorije ide PRIJE spuštanja cijene: budžet je korisnikovo tvrdo
 *  ograničenje, a kategorija je pretpostavka o tuđem ukusu. */
function buildAttempts(answers: GiftAnswers): GiftAttempt[] {
  const out: GiftAttempt[] = [];
  const requested = answers.drink;
  const shape = resolveShape(answers.shape, answers.recipient);
  // Kod „samo cigara” kategorija pića ne mijenja glavni prijedlog, pa se
  // ljestvica kategorija preskače.
  const categoryLadder: GiftDrinkPref[] =
    shape === "cigar" || requested === "unknown"
      ? []
      : [...neighbourCategories(requested), "unknown"];

  for (const allowCheaper of [false, true]) {
    out.push({ answers, allowCheaper });
    for (const cat of categoryLadder) {
      out.push({
        answers: { ...answers, drink: cat, ownedStyles: [], drinkPick: "unknown" },
        swappedFromCategory: requested === "unknown" ? undefined : requested,
        allowCheaper,
      });
    }
  }

  if (shape === "pairing") {
    // Nijedna kategorija nije dala par iznad praga: radije cigara i boca
    // zasebno nego kombinacija koja ne ide.
    out.push({
      answers: { ...answers, shape: "cigar" },
      droppedPairing: true,
      allowCheaper: true,
      lenient: true,
    });
    out.push({
      answers: { ...answers, drink: "unknown", shape: "cigar", ownedStyles: [], drinkPick: "unknown" },
      droppedPairing: true,
      swappedFromCategory: requested === "unknown" ? undefined : requested,
      allowCheaper: true,
      lenient: true,
    });
  }
  if (shape === "cigar") {
    out.push({ answers: { ...answers, shape: "bottle" }, allowCheaper: true, lenient: true });
  }
  if (shape === "bottle") {
    out.push({ answers: { ...answers, shape: "cigar" }, allowCheaper: true, lenient: true });
  }
  // Posljednji korak nikad ne inzistira na obliku — ako u katalogu uopće ima
  // nečega za ovo tržište, prijedlog izlazi.
  out.push({ answers, allowCheaper: true, lenient: true });

  return out;
}

export function findGifts(
  answers: GiftAnswers,
  catalog: GiftCatalog,
  market: RegionFilter,
  opts?: { seed?: number; excludeIds?: string[] },
): GiftPick[] {
  const region = giftRegion(market);
  const exclude = new Set(opts?.excludeIds ?? []);
  const safeDefault = isBlankGiftAnswers(answers);
  const effective = safeDefault ? SAFE_DEFAULT_ANSWERS : answers;

  const annotate = (picks: GiftPick[], attempt: GiftAttempt): GiftPick[] =>
    picks.map((pick) => ({
      ...pick,
      ...(safeDefault ? { safeDefault: true } : null),
      ...(attempt.droppedPairing ? { droppedPairing: true } : null),
      ...(attempt.swappedFromCategory != null &&
      pick.drink != null &&
      pick.drink.category !== attempt.swappedFromCategory
        ? { swappedFromCategory: attempt.swappedFromCategory }
        : null),
    }));

  // Prvi korak koji zadovolji traženi oblik pobjeđuje. Kad se siđe na popustljive
  // korake, jedan usamljen prijedlog nije dobar ishod — zapamti ga, ali nastavi
  // tražiti korak koji nudi barem dvije stvari (npr. cigaru i bocu zasebno).
  let best: GiftPick[] = [];
  for (const attempt of buildAttempts(effective)) {
    const picks = findGiftsOnce(attempt.answers, catalog, region, exclude, {
      safeDefault,
      requirePrimary: !attempt.lenient,
      allowCheaper: Boolean(attempt.allowCheaper),
    });
    if (picks.length === 0) continue;
    if (!attempt.lenient || picks.length >= 2) return annotate(picks, attempt);
    if (best.length === 0) best = annotate(picks, attempt);
  }

  return best;
}

export function allGiftAnswerCombos(): GiftAnswers[] {
  const recipients: GiftRecipient[] = ["regular", "beginner", "drinks-only", "unknown"];
  const budgets: GiftBudget[] = ["under20", "20to40", "40to60", "60to100", "over100", "unknown"];
  const drinks: GiftDrinkPref[] = ["whisky", "rum", "brandy", "wine", "unknown"];
  const intensities: GiftIntensity[] = ["mild", "medium", "bold", "unknown"];
  const shapes: GiftShape[] = ["cigar", "bottle", "pairing", "unknown"];
  const out: GiftAnswers[] = [];
  for (const recipient of recipients) {
    for (const budget of budgets) {
      for (const drink of drinks) {
        for (const intensity of intensities) {
          for (const shape of shapes) {
            out.push({ recipient, budget, drink, intensity, shape });
          }
        }
      }
    }
  }
  return out;
}
