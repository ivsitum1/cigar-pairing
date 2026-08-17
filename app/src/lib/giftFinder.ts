// Poklon u pet pitanja — odgovori postaju filteri nad postojećim katalogom i
// pairing engineom. Bez novog modela bodovanja; cijena i blizina trgovine su
// tvrdi uvjeti (poklon bez cijene nije poklon).
import type { Cigar, Drink, DrinkCategory, LocalizedText, Region, RegionFilter } from "../types";
import { cigarLinePrice } from "./cigarPrice";
import { pairDrinksForCigar } from "../engine/pairing";
import { pairingBlurb } from "../engine/pairingExplain";
import { cigarShapes, type ShapeFamily } from "./vitolaShape";

export type GiftRecipient = "regular" | "beginner" | "drinks-only" | "unknown";
export type GiftBudget = "under20" | "20to40" | "40to60" | "60to100" | "unknown";
export type GiftDrinkPref = DrinkCategory | "unknown";
export type GiftIntensity = "mild" | "medium" | "bold" | "unknown";
export type GiftShape = "cigar" | "bottle" | "pairing" | "unknown";

export interface GiftAnswers {
  recipient: GiftRecipient;
  budget: GiftBudget;
  drink: GiftDrinkPref;
  intensity: GiftIntensity;
  shape: GiftShape;
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
};

const BUDGET_FALLBACK: Partial<Record<GiftBudget, GiftBudget>> = {
  "60to100": "40to60",
  "40to60": "20to40",
  "20to40": "under20",
};

const BEGINNER_SHAPES = new Set<ShapeFamily>(["corona", "robusto"]);

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
  if (region === "HR") return c.availabilityHR.length > 0;
  return c.markets.includes(region);
}

export function drinkGiftEligible(d: Drink, region: Region): boolean {
  if (!d.pairable || drinkMid(d) == null) return false;
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
): { items: T[]; fellBack: boolean } {
  let band = resolveBudget(budget);
  let fellBack = false;
  let currentBudget = budget;
  let filtered = items.filter((x) => {
    const p = priceOf(x);
    return p != null && inBudget(p, band);
  });
  while (filtered.length === 0 && currentBudget !== "unknown") {
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
    case "unknown":
    default:
      return { min: 2, max: 4 };
  }
}

function intensityBodyRange(intensity: GiftIntensity): { min: number; max: number } {
  switch (intensity) {
    case "mild":
      return { min: 1, max: 2 };
    case "bold":
      return { min: 4, max: 5 };
    case "medium":
    case "unknown":
    default:
      return { min: 2, max: 4 };
  }
}

function cigarMatchesIntensity(c: Cigar, intensity: GiftIntensity): boolean {
  const { min, max } = intensityStrengthRange(intensity);
  return c.strength >= min && c.strength <= max;
}

function drinkMatchesIntensity(d: Drink, intensity: GiftIntensity): boolean {
  const { min, max } = intensityBodyRange(intensity);
  return d.body >= min && d.body <= max;
}

function cigarMatchesRecipient(c: Cigar, recipient: GiftRecipient): boolean {
  const cap = recipientStrengthCap(recipient);
  if (cap != null && c.strength > cap) return false;
  if (recipient === "beginner" || recipient === "unknown") {
    const shapes = cigarShapes(c);
    if (shapes.size > 0 && ![...shapes].some((s) => BEGINNER_SHAPES.has(s))) return false;
  }
  return true;
}

function drinkPool(
  drinks: Drink[],
  pref: GiftDrinkPref,
  region: Region,
  intensity: GiftIntensity,
): Drink[] {
  let pool = drinks.filter((d) => drinkGiftEligible(d, region));
  if (pref !== "unknown") pool = pool.filter((d) => d.category === pref);
  pool = pool.filter((d) => drinkMatchesIntensity(d, intensity));
  return pool.sort(
    (a, b) =>
      (b.qualityScore ?? 0) - (a.qualityScore ?? 0) ||
      (drinkMid(a) ?? 9999) - (drinkMid(b) ?? 9999),
  );
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
        cigarMatchesIntensity(c, intensity),
    )
    .sort(
      (a, b) =>
        a.strength - b.strength ||
        (cigarPrice(a, region) ?? 9999) - (cigarPrice(b, region) ?? 9999),
    );
}

function pairingPick(
  cigars: Cigar[],
  drinks: Drink[],
  answers: GiftAnswers,
  region: Region,
  exclude: Set<string>,
): GiftPick | null {
  const cigarCandidates = cigarPool(cigars, region, answers.recipient, answers.intensity);
  const drinkCandidates = drinkPool(drinks, answers.drink, region, answers.intensity);

  let currentBudget = answers.budget;
  let fellBack = false;
  while (true) {
    const band = resolveBudget(currentBudget);
    const cigarsInBand = cigarCandidates
      .filter((c) => {
        const p = cigarPrice(c, region);
        return p != null && p <= (band.max ?? Infinity) + 0.01;
      })
      .sort(
        (a, b) => (cigarPrice(a, region) ?? 0) - (cigarPrice(b, region) ?? 0),
      );

    for (const cigar of cigarsInBand.slice(0, 16)) {
      if (exclude.has(`c:${cigar.id}`)) continue;
      const cp = cigarPrice(cigar, region)!;
      const drinksFit = drinkCandidates.filter((d) => {
        const dp = drinkMid(d);
        return dp != null && inBudget(cp + dp, band);
      });
      if (drinksFit.length === 0) continue;
      const ranked = pairDrinksForCigar(cigar, drinksFit);
      const top = ranked[0];
      if (!top) continue;
      const id = `pair:${cigar.id}:${top.item.id}`;
      if (exclude.has(id)) continue;
      const dp = drinkMid(top.item)!;
      return {
        id,
        kind: "pairing",
        cigar,
        drink: top.item,
        price: cp + dp,
        shop: cigarShopName(cigar, region) ?? top.item.shopHR ?? null,
        why: pairingBlurb(cigar, top.item, top.reasons, top.score),
        fellBackBudget: fellBack,
        region,
      };
    }

    const next = currentBudget === "unknown" ? undefined : BUDGET_FALLBACK[currentBudget];
    if (!next) break;
    currentBudget = next;
    fellBack = true;
  }
  return null;
}

function bottlePick(
  drinks: Drink[],
  answers: GiftAnswers,
  region: Region,
  exclude: Set<string>,
): GiftPick | null {
  const pool = drinkPool(drinks, answers.drink, region, answers.intensity);
  const { items, fellBack } = filterByBudget(pool, drinkMid, answers.budget);
  const drink = items.find((d) => !exclude.has(`d:${d.id}`));
  if (!drink) return null;
  return {
    id: `d:${drink.id}`,
    kind: "drink",
    drink,
    price: drinkMid(drink),
    shop: drink.shopHR ?? null,
    why: drink.notes,
    fellBackBudget: fellBack,
    region,
  };
}

function cigarPick(
  cigars: Cigar[],
  answers: GiftAnswers,
  region: Region,
  exclude: Set<string>,
): GiftPick | null {
  const pool = cigarPool(cigars, region, answers.recipient, answers.intensity);
  const { items, fellBack } = filterByBudget(pool, (c) => cigarPrice(c, region), answers.budget);
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

function takePicks(builders: (() => GiftPick | null)[]): GiftPick[] {
  const out: GiftPick[] = [];
  const used = new Set<string>();
  for (const build of builders) {
    const pick = build();
    if (!pick || used.has(pick.id)) continue;
    used.add(pick.id);
    out.push(pick);
    if (out.length >= 3) break;
  }
  return out;
}

function findGiftsOnce(
  answers: GiftAnswers,
  catalog: GiftCatalog,
  region: Region,
  exclude: Set<string>,
): GiftPick[] {
  const shape = resolveShape(answers.shape, answers.recipient);
  const cigar = () => cigarPick(catalog.cigars, answers, region, exclude);
  const bottle = () => bottlePick(catalog.drinks, answers, region, exclude);
  const pair = () => pairingPick(catalog.cigars, catalog.drinks, answers, region, exclude);

  if (answers.recipient === "drinks-only") {
    const first = bottle();
    const skip = new Set(exclude);
    if (first) skip.add(first.id);
    const second = bottlePick(catalog.drinks, answers, region, skip);
    return [first, second].filter(Boolean) as GiftPick[];
  }

  switch (shape) {
    case "cigar":
      return takePicks([cigar, pair, bottle]);
    case "bottle":
      return takePicks([bottle, pair, cigar]);
    case "pairing":
      return takePicks([pair, cigar, bottle]);
    default: {
      const _exhaustive: never = shape;
      return _exhaustive;
    }
  }
}

export function findGifts(
  answers: GiftAnswers,
  catalog: GiftCatalog,
  market: RegionFilter,
  opts?: { seed?: number; excludeIds?: string[] },
): GiftPick[] {
  const region = giftRegion(market);
  const exclude = new Set(opts?.excludeIds ?? []);

  const attempts: GiftAnswers[] = [answers];
  if (answers.intensity !== "unknown") {
    attempts.push({ ...answers, intensity: "unknown" });
  }
  if (answers.drink !== "unknown") {
    attempts.push({ ...answers, intensity: "unknown", drink: "unknown" });
  }
  if (answers.shape === "pairing") {
    attempts.push({ ...answers, intensity: "unknown", drink: "unknown", shape: "cigar" });
    attempts.push({ ...answers, intensity: "unknown", drink: "unknown", shape: "bottle" });
  }
  if (answers.shape === "cigar") {
    attempts.push({ ...answers, intensity: "unknown", shape: "bottle" });
  }

  for (const attempt of attempts) {
    const picks = findGiftsOnce(attempt, catalog, region, exclude);
    if (picks.length > 0) return picks;
  }

  return [];
}

export function allGiftAnswerCombos(): GiftAnswers[] {
  const recipients: GiftRecipient[] = ["regular", "beginner", "drinks-only", "unknown"];
  const budgets: GiftBudget[] = ["under20", "20to40", "40to60", "60to100", "unknown"];
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
