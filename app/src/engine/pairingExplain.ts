// Lokalna objašnjenja para — blurb (uvijek) i narrative (proširenje).
// Deterministički iz reasons + dijeljenih tagova; bez LLM/API.

import type { Cigar, Drink, LocalizedText, PairingReason } from "../types";
import { flavorLabel, normalizeTags } from "./rules";

const BODY_HR = ["", "vrlo lagano", "lagano", "srednje", "puno", "vrlo puno"];
const BODY_EN = ["", "very light", "light", "medium", "full", "very full"];

function stripDot(s: string): string {
  return s.replace(/\.+$/, "").trim();
}

function sharedTags(cigar: Cigar, drink: Drink): string[] {
  const drinkTags = normalizeTags(drink.flavorTags);
  return normalizeTags(cigar.flavorTags).filter((t) => drinkTags.includes(t));
}

function sortedPos(reasons: PairingReason[]): PairingReason[] {
  return reasons.filter((r) => r.score > 0).sort((a, b) => b.score - a.score);
}

function sortedNeg(reasons: PairingReason[]): PairingReason[] {
  return reasons.filter((r) => r.score < 0).sort((a, b) => a.score - b.score);
}

function fallback(cigar: Cigar, drink: Drink, score: number): LocalizedText {
  return {
    hr: `${BODY_HR[cigar.body] || "srednje"} tijelo cigare uz ${drink.category} (${drink.style}): ${score}% slaganja.`,
    en: `${BODY_EN[cigar.body] || "medium"} cigar body with ${drink.category} (${drink.style}): ${score}% match.`,
  };
}

/** One-line explanation for every scored pair. */
export function pairingBlurb(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): LocalizedText {
  const topPos = sortedPos(reasons)[0];
  if (topPos) {
    return { hr: `${stripDot(topPos.text.hr)}.`, en: `${stripDot(topPos.text.en)}.` };
  }
  const topNeg = sortedNeg(reasons)[0];
  if (topNeg) {
    return { hr: `${stripDot(topNeg.text.hr)}.`, en: `${stripDot(topNeg.text.en)}.` };
  }
  return fallback(cigar, drink, score);
}

/** 2–3 sentence paragraph for expand / detail view. */
export function pairingNarrative(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): LocalizedText {
  const blurb = pairingBlurb(cigar, drink, reasons, score);
  const pos = sortedPos(reasons);
  const neg = sortedNeg(reasons);
  const shared = sharedTags(cigar, drink).slice(0, 3);

  const extraHr: string[] = [];
  const extraEn: string[] = [];

  const second = pos[1];
  if (second) {
    extraHr.push(stripDot(second.text.hr));
    extraEn.push(stripDot(second.text.en));
  } else if (neg[0]) {
    extraHr.push(stripDot(neg[0].text.hr));
    extraEn.push(stripDot(neg[0].text.en));
  }

  if (shared.length > 0) {
    extraHr.push(`Zajedničke note: ${shared.map((t) => flavorLabel(t, "hr")).join(", ")}`);
    extraEn.push(`Shared notes: ${shared.map((t) => flavorLabel(t, "en")).join(", ")}`);
  }

  if (extraHr.length === 0) {
    return {
      hr: `${stripDot(blurb.hr)}. Slaganje ${score}%.`,
      en: `${stripDot(blurb.en)}. Match ${score}%.`,
    };
  }

  return {
    hr: `${stripDot(blurb.hr)}. ${extraHr.join(". ")}.`,
    en: `${stripDot(blurb.en)}. ${extraEn.join(". ")}.`,
  };
}
