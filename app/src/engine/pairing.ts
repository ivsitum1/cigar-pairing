// Deterministicki rule-based pairing engine.
// Svako pravilo koje pridonese rezultatu generira dvojezicno objasnjenje.

import type { Cigar, Drink, PairingReason, PairingResult } from "../types";
import { COMPLEMENTS, POWER_TAGS, WEIGHTS, WRAPPER_AFFINITY, normalizeTags } from "./rules";
import { personalBrandReason, personalStyleReason, type PersonalPrefs } from "./personal";
import { applyGeometry } from "./vitolaGeometry";

const clamp = (v: number, lo: number, hi: number) =>
  Math.max(lo, Math.min(hi, v));

const BODY_LABEL_HR = ["", "vrlo lagano", "lagano", "srednje", "puno", "vrlo puno"];
const BODY_LABEL_EN = ["", "very light", "light", "medium", "full", "very full"];

export function scorePairing(
  cigar: Cigar,
  drink: Drink,
  prefs?: PersonalPrefs,
): { score: number; reasons: PairingReason[] } {
  const reasons: PairingReason[] = [];
  let score = WEIGHTS.base;

  const {
    cigar: effCigar,
    wrapperForwardBonus,
    reason: geoReason,
  } = applyGeometry(cigar);

  // sinonimi iz scrape podataka (npr. "začini", "cokolada", "mizunara")
  // svode se na kanonske tagove da bi pravila 2, 2b i 5 vidjela sve note
  const cigarTags = normalizeTags(effCigar.flavorTags);
  const drinkTags = normalizeTags(drink.flavorTags);

  // 1) Body match — zlatno pravilo (effCigar: geometrija vitole).
  // Match unutar <0.5 koraka: bodyDelta geometrije (±0.1–0.2) ne smije skinuti
  // puni bonus — inače geometrija preokreće dominantno pravilo.
  const bodyDiff = Math.abs(effCigar.body - drink.body);
  const bodyLabelIdx = Math.round(effCigar.body);
  if (bodyDiff < 0.5) {
    score += WEIGHTS.bodyBonus;
    reasons.push({
      rule: "body-match",
      score: WEIGHTS.bodyBonus,
      text: {
        hr: `Tijela se poklapaju (${BODY_LABEL_HR[bodyLabelIdx]}) — nijedno ne nadjačava drugo.`,
        en: `Bodies match (${BODY_LABEL_EN[bodyLabelIdx]}) — neither overpowers the other.`,
      },
    });
  } else {
    const penalty = bodyDiff * WEIGHTS.bodyPerStep;
    score -= penalty;
    if (bodyDiff >= 2) {
      const cigarHeavier = effCigar.body > drink.body;
      reasons.push({
        rule: "body-mismatch",
        score: -penalty,
        text: {
          hr: cigarHeavier
            ? "Cigara je znatno punija od pića — dim će pregaziti okus."
            : "Piće je znatno punije od cigare — cigara će se izgubiti.",
          en: cigarHeavier
            ? "The cigar is much fuller than the drink — smoke will trample the flavour."
            : "The drink is much fuller than the cigar — the cigar will get lost.",
        },
      });
    }
  }

  // 1b) Jaka cigara + lagano pice = pregazeno
  if (effCigar.strength >= 4 && drink.body <= 2) {
    score -= WEIGHTS.overwhelmPenalty;
    reasons.push({
      rule: "strength-overwhelm",
      score: -WEIGHTS.overwhelmPenalty,
      text: {
        hr: "Jaka cigara (nikotin) guši ovako delikatno piće.",
        en: "A strong cigar (nicotine) smothers such a delicate drink.",
      },
    });
  }

  // 2) Zajednicki tagovi (komplementarno — slicni profili)
  const shared = cigarTags.filter((t) => drinkTags.includes(t));
  if (shared.length > 0) {
    const pts = Math.min(shared.length, 3) * WEIGHTS.tagOverlap;
    score += pts;
    reasons.push({
      rule: "flavor-shared",
      score: pts,
      text: {
        hr: `Dijele note: ${shared.slice(0, 3).join(", ")}.`,
        en: `Shared notes: ${shared.slice(0, 3).join(", ")}.`,
      },
    });
  }

  // 2b) Komplementarni parovi (razliciti ali se nadopunjuju)
  const complemented: string[] = [];
  for (const ct of cigarTags) {
    const comp = COMPLEMENTS[ct];
    if (!comp) continue;
    for (const dt of drinkTags) {
      if (dt !== ct && comp.includes(dt)) complemented.push(`${ct}↔${dt}`);
    }
  }
  if (complemented.length > 0) {
    const pts = Math.min(complemented.length, 3) * WEIGHTS.tagComplement;
    score += pts;
    reasons.push({
      rule: "flavor-complement",
      score: pts,
      text: {
        hr: `Note se nadopunjuju: ${complemented.slice(0, 3).join(", ")}.`,
        en: `Complementary notes: ${complemented.slice(0, 3).join(", ")}.`,
      },
    });
  }

  // 3) Kontrast: slatko pice + puna maduro cigara (bazni body, ne eff — geometrija ne dira ovo pravilo)
  const isDarkWrapper = /maduro|oscuro|san andr|broadleaf/i.test(cigar.wrapper);
  if (drink.sweetness >= 4 && cigar.body >= 4 && isDarkWrapper) {
    score += WEIGHTS.contrastSweetMaduro;
    reasons.push({
      rule: "contrast-sweet-maduro",
      score: WEIGHTS.contrastSweetMaduro,
      text: {
        hr: "Slatkoća pića presijeca gorčinu tamnog dima — klasični kontrast.",
        en: "The drink's sweetness cuts the dark smoke's bitterness — a classic contrast.",
      },
    });
  }

  // 4) Wrapper afinitet — tanka vitola pojačava wrapper-forward bonus
  for (const wa of WRAPPER_AFFINITY) {
    if (!wa.wrapper.test(effCigar.wrapper)) continue;
    const styleHit = wa.styles.includes(drink.style);
    const tagHit = drinkTags.some((t) => wa.tags.includes(t));
    if (styleHit || tagHit) {
      const pts = WEIGHTS.wrapperMatch + wrapperForwardBonus;
      score += pts;
      reasons.push({
        rule: "wrapper-affinity",
        score: pts,
        text: { hr: `${wa.labelHr}.`, en: `${wa.labelEn}.` },
      });
    }
    break; // samo prvi odgovarajuci wrapper profil
  }

  // 5) Snaga: overproof/dimna pica vole jaku cigaru, gaze blagu
  const powerDrink = drinkTags.some((t) =>
    (POWER_TAGS as readonly string[]).includes(t),
  );
  if (powerDrink && effCigar.strength >= 4) {
    score += WEIGHTS.strengthPowerMatch;
    reasons.push({
      rule: "power-match",
      score: WEIGHTS.strengthPowerMatch,
      text: {
        hr: "Snažno piće (esteri/dim/overproof) traži i podnosi jaku cigaru.",
        en: "A powerful drink (esters/smoke/overproof) demands and handles a strong cigar.",
      },
    });
  } else if (powerDrink && effCigar.strength <= 2) {
    score -= WEIGHTS.strengthPowerMismatch;
    reasons.push({
      rule: "power-mismatch",
      score: -WEIGHTS.strengthPowerMismatch,
      text: {
        hr: "Ovako intenzivno piće pregazit će blagu cigaru.",
        en: "Such an intense drink will steamroll a mild cigar.",
      },
    });
  }

  // 6) Kvaliteta pica — blagi nudge da bolji sipperi isplivaju
  if (drink.qualityScore != null) {
    score += (drink.qualityScore - 7) * WEIGHTS.qualityNudge;
  }

  // 7) Osobni nudge iz dnevnika (lokalno, s objasnjenjem) — nikad presudan
  if (prefs) {
    for (const reason of [
      personalStyleReason(prefs, drink.style),
      personalBrandReason(prefs, cigar.brand),
    ]) {
      if (reason) {
        score += reason.score;
        reasons.push(reason);
      }
    }
  }

  if (geoReason) reasons.push(geoReason);

  return { score: clamp(Math.round(score), 0, 100), reasons };
}

export function pairDrinksForCigar(
  cigar: Cigar,
  drinks: Drink[],
  prefs?: PersonalPrefs,
): PairingResult<Drink>[] {
  return drinks
    .filter((d) => d.pairable)
    .map((item) => ({ item, ...scorePairing(cigar, item, prefs) }))
    .sort((a, b) => b.score - a.score);
}

export function pairCigarsForDrink(
  drink: Drink,
  cigars: Cigar[],
  prefs?: PersonalPrefs,
): PairingResult<Cigar>[] {
  return cigars
    .map((item) => ({ item, ...scorePairing(item, drink, prefs) }))
    .sort((a, b) => b.score - a.score);
}
