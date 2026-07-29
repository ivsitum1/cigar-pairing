// Prilika (jutro / poslijepodne / večer).
//
// Dva sloja, oba čuvaju pravilo "par je važniji od doba dana":
//
//  1) SOFT NUDGE u scoreu (`occasionReasons`) — ukupni |delta| ostaje ispod
//     jednog koraka body-matcha (WEIGHTS.bodyPerStep), pa prilika nikad ne
//     pretvori loš par u dobar.
//  2) IZBOR UNUTAR IZJEDNAČENIH (`rankByOccasion`) — među kandidatima koji su
//     ionako u istom razredu kvalitete (score unutar `OCCASION_BAND_MARGIN` od
//     najboljeg) presuđuje doba dana. Ovdje nastaje stvarna razlika između
//     jutra i večeri: ne biramo lošiji par, biramo prikladniji od jednako
//     dobrih.
//
// Sam nudge iz (1) razliku gotovo ne pravi — audit je pokazao 3.8% cigara s
// drugačijim top-1 između jutra i večeri. Zato (2) postoji.

import type {
  Cigar,
  Drink,
  DrinkCategory,
  PairingReason,
  PairingResult,
} from "../types";
import { POWER_TAGS, WEIGHTS, normalizeTags } from "./rules";

export type OccasionFilter = "any" | "morning" | "afternoon" | "evening";
export type Occasion = Exclude<OccasionFilter, "any">;

/** Koliko bodova ispod najboljeg smije biti kandidat da ga prilika još smije pretaknuti. */
export const OCCASION_BAND_MARGIN = 6;

/**
 * Soft-only: ne isključuje pića. Raniji hard filter je blage cigare navečer
 * ostavljao bez laganih rumova (top ~41). Pool ostaje pun; rang pomiče score.
 */
export function occasionKeep(
  _occasion: OccasionFilter,
  _cigarBody = 3,
): (d: Drink) => boolean {
  return () => true;
}

/** @deprecated soft-only — svi prolaze */
export const OCCASION_KEEP: Record<OccasionFilter, (d: Drink) => boolean> = {
  any: () => true,
  morning: () => true,
  afternoon: () => true,
  evening: () => true,
};

type Clock = Record<Occasion, number>;

const clock = (morning: number, afternoon: number, evening: number): Clock => ({
  morning,
  afternoon,
  evening,
});

/**
 * Kategorija → doba dana. Kava je jutro, digestiv je večer po definiciji; sve
 * ostalo je nijansa, ne pravilo.
 */
const CATEGORY_CLOCK: Record<DrinkCategory, Clock> = {
  coffee: clock(2, 0.5, -1.25),
  gin: clock(-0.25, 1, 0),
  wine: clock(-0.75, 0.5, 0.5),
  tequila: clock(-0.5, 1, 0.25),
  rum: clock(-0.25, 0.5, 0.75),
  whisky: clock(-0.75, 0.25, 1),
  brandy: clock(-1, 0, 1.25),
  digestif: clock(-1.5, -0.25, 1.5),
};

/**
 * Stil → doba dana, povrh kategorije. Jutro: svijetlo, svježe, niskog stupnja.
 * Poslijepodne: aperitiv i srednje tijelo. Večer: staro, tamno, dimljeno,
 * slatko nakon jela.
 */
const STYLE_CLOCK: Record<string, Clock> = {
  // kava
  "filter-light": clock(1.25, 0.25, -0.75),
  "filter-medium": clock(1, 0.25, -0.5),
  "filter-dark": clock(0.5, 0.25, 0),
  "espresso-medium": clock(1, 0.5, -0.25),
  "espresso-dark": clock(0.5, 0.5, 0.25),
  milk: clock(1.5, 0, -1),
  cold: clock(1, 0.75, -0.5),
  turkish: clock(0.75, 0.5, 0),
  moka: clock(1, 0.25, -0.25),
  spiked: clock(-1, 0, 1.25), // kava s likerom — poslije večere, ne u osam ujutro

  // rum
  agricole: clock(1, 0.75, -0.25),
  cachaca: clock(0.75, 0.75, -0.25),
  cuba: clock(0.25, 0.75, 0.25),
  "puerto-rico": clock(0.5, 0.75, 0),
  spiced: clock(-0.25, 0.5, 0.5),
  jamaica: clock(-0.5, 0.25, 1),
  demerara: clock(-1, 0, 1.25),
  solera: clock(-0.75, 0, 1),
  navy: clock(-1.25, -0.25, 1.25),

  // whisky
  lowland: clock(0.75, 0.75, -0.25),
  "irish-blend": clock(0.5, 0.75, 0),
  "speyside-fruity": clock(0.5, 0.75, 0),
  "blended-scotch": clock(0, 0.75, 0.25),
  highland: clock(-0.25, 0.5, 0.5),
  bourbon: clock(-0.25, 0.5, 0.5),
  rye: clock(-0.5, 0.25, 0.75),
  "speyside-sherry": clock(-0.75, 0.25, 1),
  island: clock(-1, 0, 1.25),
  campbeltown: clock(-1, 0, 1.25),
  "islay-peated": clock(-1.5, -0.25, 1.5),

  // brandy
  grappa: clock(-0.5, 0.25, 1),
  calvados: clock(0, 0.5, 0.5),
  "cognac-vs": clock(-0.25, 0.75, 0.25),
  "cognac-vsop": clock(-0.5, 0.5, 0.75),
  "cognac-xo": clock(-1.25, -0.25, 1.5),
  armagnac: clock(-1.25, -0.25, 1.5),
  "brandy-de-jerez": clock(-1, 0, 1.25),
  vinjak: clock(-0.5, 0.5, 0.5),

  // vino
  "white-fresh": clock(0.5, 1.25, -0.25),
  sparkling: clock(0.5, 1.25, 0),
  "sherry-dry": clock(0.25, 1.25, 0), // fino/manzanilla — aperitiv
  "white-rich": clock(0, 1, 0.25),
  "red-medium": clock(-0.5, 0.75, 0.5),
  "red-full": clock(-1, 0.25, 1),
  "port-ruby": clock(-1.25, -0.25, 1.5),
  "port-tawny": clock(-1.25, -0.25, 1.5),
  madeira: clock(-1, 0, 1.25),
  "sherry-sweet": clock(-1.25, -0.25, 1.5),
  "dessert-wine": clock(-1.25, -0.25, 1.5),
  prosek: clock(-1, 0, 1.25),

  // tequila
  blanco: clock(0.5, 1.25, -0.25),
  reposado: clock(0, 1, 0.25),
  anejo: clock(-0.75, 0.25, 1),
  "extra-anejo": clock(-1.25, -0.25, 1.5),
  mezcal: clock(-1, 0, 1.25),

  // gin
  "london-dry": clock(0.25, 1.25, -0.25),
  plymouth: clock(0.25, 1.25, -0.25),
  contemporary: clock(0, 1.25, 0),
  "premium-dry": clock(-0.25, 1, 0.25),
  croatian: clock(0, 1, 0.25),

  // digestivi
  fernet: clock(-1.5, -0.25, 1.5),
  pelinkovac: clock(-1.25, 0, 1.5),
  "herbal-monastic": clock(-1.5, -0.25, 1.5),
  "herbal-bitter-italian": clock(-1, 0.5, 1.25),
  "herbal-bitter-central": clock(-1.25, 0, 1.5),
  "herbal-saffron-yellow": clock(-1, 0.25, 1.25),
  "specialty-botanical": clock(-1, 0.25, 1.25),
};

const clamp = (x: number, lo: number, hi: number) =>
  Math.max(lo, Math.min(hi, x));

export type OccasionInput = {
  cigar: Pick<Cigar, "strength" | "body">;
  drink: Pick<Drink, "body" | "category" | "style" | "flavorTags"> &
    Partial<Pick<Drink, "abv">>;
};

/**
 * Koliko piće (uz TU cigaru) pristaje dobu dana: −2 (strano) … +2 (kao
 * stvoreno). Zbraja kategoriju, stil, relativno tijelo prema cigari i žestinu.
 */
export function occasionAffinity(
  occasion: Occasion,
  { cigar, drink }: OccasionInput,
): number {
  let a = CATEGORY_CLOCK[drink.category][occasion];
  a += STYLE_CLOCK[drink.style]?.[occasion] ?? 0;

  // relativno prema cigari, ne apsolutni "body 4 uvečer"
  const lean = drink.body - cigar.body;
  if (occasion === "morning") a += clamp(-lean * 0.5, -1, 0.75);
  if (occasion === "afternoon") a += clamp(0.75 - Math.abs(lean) * 0.6, -1, 0.75);
  if (occasion === "evening") a += clamp(lean * 0.5, -1, 0.75);

  // žestina: overproof/vrlo jako je večernje, niski stupanj jutarnji
  const drinkTags = normalizeTags(drink.flavorTags);
  const power =
    drinkTags.some((t) => (POWER_TAGS as readonly string[]).includes(t)) ||
    (drink.abv ?? 0) >= 50;
  if (power) {
    a += occasion === "evening" ? 0.75 : occasion === "morning" ? -1 : -0.25;
  }
  if (occasion === "morning" && (drink.abv ?? 100) <= 20) a += 0.25;

  // snaga cigare vuče isti smjer kao piće
  if (occasion === "morning" && cigar.strength <= 2.5) a += 0.5;
  if (occasion === "evening" && cigar.strength >= 3.5) a += 0.5;

  return clamp(a, -2, 2);
}

const OCCASION_LABEL_HR: Record<Occasion, string> = {
  morning: "jutro",
  afternoon: "poslijepodne",
  evening: "večer",
};
const OCCASION_LABEL_EN: Record<Occasion, string> = {
  morning: "morning",
  afternoon: "afternoon",
  evening: "evening",
};

const FIT_TEXT_HR: Record<Occasion, string> = {
  morning: "Sjeda u jutarnji ritam — svježije i laganije, budi bez opterećenja.",
  afternoon:
    "Poslijepodnevni tempo — dovoljno tijela da drži cigaru, bez težine večeri.",
  evening: "Večernji ritam — punije, starije i tamnije, za sporo pijenje.",
};
const FIT_TEXT_EN: Record<Occasion, string> = {
  morning:
    "Sits in a morning rhythm — fresher and lighter, wakes you without weighing you down.",
  afternoon:
    "An afternoon pace — enough body to hold the cigar, none of the evening's weight.",
  evening: "An evening rhythm — fuller, older and darker, made for slow sipping.",
};

const CLASH_TEXT_HR: Record<Occasion, string> = {
  morning: "Za jutro pretamno i preteško — ovo traži kraj dana.",
  afternoon: "Krajnost u oba smjera manje pristaje poslijepodnevu.",
  evening: "Za večer prelagano — nestane ispod cigare.",
};
const CLASH_TEXT_EN: Record<Occasion, string> = {
  morning: "Too dark and heavy for the morning — this asks for the end of the day.",
  afternoon: "An extreme either way suits the afternoon less well.",
  evening: "Too light for the evening — it disappears under the cigar.",
};

/**
 * Soft nudge. Ukupni |delta| namjerno < WEIGHTS.bodyPerStep (12),
 * da dobar par ne izgubi od lošijeg samo zbog chipa prilike.
 */
export function occasionReasons(
  occasion: Occasion | undefined,
  eff: OccasionInput,
): PairingReason[] {
  if (!occasion) return [];

  const a = occasionAffinity(occasion, eff);
  if (Math.abs(a) < 0.5) return [];

  // |a| ≤ 2 → |score| ≤ occasionFit + occasionMild < bodyPerStep
  const unit = (WEIGHTS.occasionFit + WEIGHTS.occasionMild) / 2;
  const score = Math.round(a * unit);
  if (score === 0) return [];

  const hrLabel = OCCASION_LABEL_HR[occasion];
  const enLabel = OCCASION_LABEL_EN[occasion];

  return [
    score > 0
      ? {
          rule: "occasion-fit",
          score,
          text: {
            hr: `${FIT_TEXT_HR[occasion]} (prilika: ${hrLabel})`,
            en: `${FIT_TEXT_EN[occasion]} (occasion: ${enLabel})`,
          },
        }
      : {
          rule: "occasion-clash",
          score,
          text: {
            hr: `${CLASH_TEXT_HR[occasion]} (prilika: ${hrLabel})`,
            en: `${CLASH_TEXT_EN[occasion]} (occasion: ${enLabel})`,
          },
        },
  ];
}

/**
 * Presloži već rangiranu listu tako da unutar pojasa izjednačenih (score ≥
 * max − margin) presudi prikladnost dobu dana. Izvan pojasa ništa se ne miče —
 * slabiji par ne može preskočiti bolji samo zato što je "jutarnji".
 */
export function rankByOccasion<T extends Drink>(
  ranked: PairingResult<T>[],
  cigar: Pick<Cigar, "strength" | "body">,
  occasion: Occasion | undefined,
  margin: number = OCCASION_BAND_MARGIN,
): PairingResult<T>[] {
  if (!occasion || ranked.length < 2) return ranked;

  const cutoff = ranked[0].score - margin;
  const bandSize = ranked.findIndex((r) => r.score < cutoff);
  const end = bandSize === -1 ? ranked.length : bandSize;
  if (end < 2) return ranked;

  const band = ranked.slice(0, end);
  const affinity = new Map<string, number>();
  for (const r of band) {
    affinity.set(r.item.id, occasionAffinity(occasion, { cigar, drink: r.item }));
  }

  const reordered = [...band].sort(
    (a, b) =>
      (affinity.get(b.item.id) ?? 0) - (affinity.get(a.item.id) ?? 0) ||
      b.score - a.score ||
      (b.item.qualityScore ?? 0) - (a.item.qualityScore ?? 0) ||
      a.item.name.localeCompare(b.item.name),
  );

  return [...reordered, ...ranked.slice(end)];
}
