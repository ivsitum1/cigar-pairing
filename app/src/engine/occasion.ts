// Prilika (jutro / poslijepodne / večer): soft-only nudge.
// Par (body/tagovi) je važniji od doba dana — prilika ne reže pool i ne smije
// nadjačati ni jedan korak body-mismatcha (vidi WEIGHTS.occasion* ≪ bodyPerStep).

import type { Cigar, Drink, PairingReason } from "../types";
import { POWER_TAGS, WEIGHTS, normalizeTags } from "./rules";

export type OccasionFilter = "any" | "morning" | "afternoon" | "evening";
export type Occasion = Exclude<OccasionFilter, "any">;

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

type EffPair = {
  cigar: Pick<Cigar, "strength" | "body">;
  drink: Pick<Drink, "body" | "category" | "flavorTags">;
};

/**
 * Soft nudge. Ukupni |delta| namjerno < WEIGHTS.bodyPerStep (12),
 * da dobar par ne izgubi od lošijeg samo zbog chipa prilike.
 */
export function occasionReasons(
  occasion: Occasion | undefined,
  eff: EffPair,
): PairingReason[] {
  if (!occasion) return [];

  const { cigar, drink } = eff;
  const reasons: PairingReason[] = [];
  const drinkTags = normalizeTags(drink.flavorTags);
  const powerDrink = drinkTags.some((t) =>
    (POWER_TAGS as readonly string[]).includes(t),
  );

  // relativno prema cigari: favoriziraj piće blizu tijela cigare, uz blagi
  // nagib jutro→laganije / večer→punije (ne apsolutni body 4 „uvečer”)
  const lean = drink.body - cigar.body;

  const pushFit = (pts: number, hr: string, en: string) => {
    reasons.push({
      rule: "occasion-fit",
      score: pts,
      text: { hr, en },
    });
  };
  const pushClash = (pts: number, hr: string, en: string) => {
    reasons.push({
      rule: "occasion-clash",
      score: -pts,
      text: { hr, en },
    });
  };

  switch (occasion) {
    case "morning": {
      if (drink.category === "coffee" || lean <= 0.25) {
        pushFit(
          WEIGHTS.occasionFit,
          "Prikladnije za jutro — laganije ili usklađeno tijelo.",
          "Better suited to morning — lighter or matched body.",
        );
      }
      if (cigar.strength <= 2.5) {
        pushFit(
          WEIGHTS.occasionMild,
          "Blaža cigara dobro sjeda u jutarnji ritam.",
          "A milder cigar sits well with a morning pace.",
        );
      }
      if (lean >= 1.5) {
        pushClash(
          WEIGHTS.occasionClash,
          "Piće je znatno punije od cigare za jutarnji ritam.",
          "The drink is much fuller than the cigar for a morning pace.",
        );
      }
      break;
    }
    case "afternoon": {
      if (Math.abs(lean) <= 0.75) {
        pushFit(
          WEIGHTS.occasionFit,
          "Prikladnije za poslijepodne — tijela blizu.",
          "Better suited to afternoon — bodies close together.",
        );
      }
      if (Math.abs(lean) >= 2) {
        pushClash(
          WEIGHTS.occasionMild,
          "Veliki raskorak tijela manje pristaje poslijepodnevu.",
          "A large body gap fits afternoon less well.",
        );
      }
      break;
    }
    case "evening": {
      if (lean >= -0.25 || powerDrink) {
        pushFit(
          WEIGHTS.occasionFit,
          "Prikladnije za večer — punije ili usklađeno tijelo.",
          "Better suited to evening — fuller or matched body.",
        );
      }
      if (cigar.strength >= 3.5) {
        pushFit(
          WEIGHTS.occasionMild,
          "Jača cigara prirodno ide uz večernji ritam.",
          "A stronger cigar naturally suits an evening pace.",
        );
      }
      if (lean <= -1.5 && drink.category !== "coffee") {
        pushClash(
          WEIGHTS.occasionClash,
          "Piće je znatno laganije od cigare za večernji ritam.",
          "The drink is much lighter than the cigar for an evening pace.",
        );
      }
      break;
    }
    default: {
      const _exhaustive: never = occasion;
      return _exhaustive;
    }
  }

  return reasons;
}
