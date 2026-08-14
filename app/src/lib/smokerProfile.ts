// Profil pušača — brojke umjesto popisa.
//
// „Probano” je bio popis koji se samo gomilao: dugačak, bez redoslijeda i bez
// poruke. Isti podaci kao zbroj kažu nešto o tebi — koliko si cigara prošao,
// kako ih ocjenjuješ i kakav format i profil te zapravo drži.
//
// Čista funkcija nad već pripremljenim recima (stranica zna razriješiti ključ u
// cigaru), pa je izračun lako testirati bez Reacta i bez kataloga.
import type { ShapeFamily } from "./vitolaShape";

export interface TriedCigar {
  itemId: string;
  /** 1–5 */
  strength: number;
  /** 1–5 */
  body: number;
  country: string;
  wrapper: string;
  flavorTags: string[];
  /** null kad linija ima više formata pa se ne zna koji je pušen. */
  shape: ShapeFamily | null;
  rating: number | null;
}

export interface JournalRow {
  cigarId: string;
  drinkId: string | null;
  rating: number | null;
}

export interface TopCount<T> {
  value: T;
  count: number;
}

export type SmokerStyle = "novice" | "mild" | "balanced" | "full" | "strong";

export interface SmokerProfile {
  tried: number;
  triedDrinks: number;
  rated: number;
  avgRating: number | null;
  evenings: number;
  avgStrength: number | null;
  avgBody: number | null;
  topShape: TopCount<ShapeFamily> | null;
  topCountry: TopCount<string> | null;
  topWrapper: TopCount<string> | null;
  topFlavors: TopCount<string>[];
  topDrink: TopCount<string> | null;
  /** Najbolje ocijenjena cigara — ključ i ocjena. */
  best: { itemId: string; rating: number } | null;
  style: SmokerStyle;
}

const mean = (values: number[]): number | null =>
  values.length === 0 ? null : values.reduce((s, v) => s + v, 0) / values.length;

/** Najčešća vrijednost; neriješeno rješava abecedno da izlaz bude stabilan. */
function topOf<T extends string>(values: T[]): TopCount<T> | null {
  const list = rankOf(values, 1);
  return list[0] ?? null;
}

function rankOf<T extends string>(values: T[], limit: number): TopCount<T>[] {
  const counts = new Map<T, number>();
  for (const v of values) {
    if (!v) continue;
    counts.set(v, (counts.get(v) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => b.count - a.count || String(a.value).localeCompare(String(b.value)))
    .slice(0, limit);
}

/**
 * Stil se čita iz prosjeka jačine i tijela probanih cigara. Ispod tri probane
 * cigare ne tvrdimo ništa — dvije cigare nisu stil nego slučaj.
 */
export function smokerStyle(
  tried: number,
  avgStrength: number | null,
  avgBody: number | null,
): SmokerStyle {
  if (tried < 3 || avgStrength == null || avgBody == null) return "novice";
  if (avgStrength >= 3.75) return "strong";
  if (avgStrength < 2.5 && avgBody < 2.75) return "mild";
  if (avgBody >= 3.5) return "full";
  return "balanced";
}

export function smokerProfile(
  cigars: TriedCigar[],
  triedDrinks: number,
  journal: JournalRow[],
): SmokerProfile {
  const ratings = cigars
    .map((c) => c.rating)
    .filter((r): r is number => r != null);
  const avgStrength = mean(cigars.map((c) => c.strength));
  const avgBody = mean(cigars.map((c) => c.body));

  const best = cigars.reduce<{ itemId: string; rating: number } | null>((acc, c) => {
    if (c.rating == null) return acc;
    if (!acc || c.rating > acc.rating) return { itemId: c.itemId, rating: c.rating };
    return acc;
  }, null);

  return {
    tried: cigars.length,
    triedDrinks,
    rated: ratings.length,
    avgRating: mean(ratings),
    evenings: journal.length,
    avgStrength,
    avgBody,
    topShape: topOf(
      cigars.map((c) => c.shape).filter((s): s is ShapeFamily => s != null),
    ),
    topCountry: topOf(cigars.map((c) => c.country)),
    topWrapper: topOf(cigars.map((c) => c.wrapper)),
    topFlavors: rankOf(cigars.flatMap((c) => c.flavorTags), 3),
    topDrink: topOf(
      journal.map((j) => j.drinkId).filter((d): d is string => d != null),
    ),
    best,
    style: smokerStyle(cigars.length, avgStrength, avgBody),
  };
}
