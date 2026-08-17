// Coffee↔cigar overlay.
// Coffee side (roast, acidity, body, origin/flavor families): distilled from
// James Hoffmann, The World Atlas of Coffee (From Beans to Brewing).
// Cigar pairing rules apply that book's balance / intensity / harmony logic;
// they are not a chapter from the atlas. Soft nudges only (< bodyPerStep).
// Reference model: data/coffeePairingModel.json — validate weights empirically.

import type { Cigar, CoffeeRoast, Drink, PairingReason } from "../types";
import { WEIGHTS, normalizeTags } from "./rules";

export type { CoffeeRoast };
export type CoffeeIntensity = "low" | "medium" | "high";
export type CoffeeAcidity = "low" | "medium" | "high";
export type CoffeeFlavorFamily =
  | "floral"
  | "fruity"
  | "nuttyCocoa"
  | "herbalSavory"
  | "earthy";

export interface CoffeeProfile {
  roast: CoffeeRoast;
  intensity: CoffeeIntensity;
  acidity: CoffeeAcidity;
  flavorFamily: CoffeeFlavorFamily;
}

const DARK_STYLES = new Set([
  "espresso-dark",
  "filter-dark",
  "turkish",
  "moka",
]);
const LIGHT_STYLES = new Set(["filter-light"]);
const HIGH_TDS_STYLES = new Set([
  "espresso-dark",
  "espresso-medium",
  "turkish",
  "moka",
]);
// Americano = espresso + hot water → medium TDS (body drives the rest).
const LOW_TDS_STYLES = new Set(["filter-light", "cold"]);

/** Region / name hints for acidity & origin character. */
function regionBlob(drink: Drink): string {
  return `${drink.region ?? ""} ${drink.country ?? ""} ${drink.name}`.toLowerCase();
}

function inferRoast(drink: Drink): CoffeeRoast {
  if (drink.coffeeDetail?.roast) return drink.coffeeDetail.roast;
  if (DARK_STYLES.has(drink.style)) return "dark";
  if (LIGHT_STYLES.has(drink.style)) return "light";
  return "medium";
}

function inferIntensity(drink: Drink): CoffeeIntensity {
  const style = drink.style;
  if (style === "americano") return "medium";
  if (drink.coffeeDetail?.species === "robusta") return "high";
  if (HIGH_TDS_STYLES.has(style) || drink.body >= 4.5) return "high";
  if (LOW_TDS_STYLES.has(style) || drink.body <= 2) return "low";
  return "medium";
}

function inferAcidity(drink: Drink, roast: CoffeeRoast, tags: string[]): CoffeeAcidity {
  const process = drink.coffeeDetail?.process;
  if (drink.coffeeDetail?.species === "robusta") return "low";
  if (process === "semi-washed" || process === "monsoon") return "low";
  if (process === "washed" && roast === "light") return "high";
  const blob = regionBlob(drink);
  if (
    /etiop|ethiop|kenij|kenya|burundi|rwanda|yirgacheffe|sidamo|guji|nyeri|panama|geisha|costa rica/.test(
      blob,
    )
  ) {
    return "high";
  }
  if (
    /brazil|sumatra|indonez|indonesia|malabar|yemen|jemen|cuba|kuba|jamaica|jamajka/.test(
      blob,
    )
  ) {
    return "low";
  }
  if (roast === "light" && (tags.includes("citrus") || tags.includes("cvjetno"))) {
    return "high";
  }
  if (roast === "dark") return "low";
  return "medium";
}

function inferFlavorFamily(drink: Drink, tags: string[], blob: string): CoffeeFlavorFamily {
  const process = drink.coffeeDetail?.process;
  // Giling basah / monsoon wins over cocoa tags.
  if (process === "semi-washed" || process === "monsoon" || /sumatra|indonez|giling|malabar/.test(blob)) {
    return "earthy";
  }
  if (process === "natural" && (tags.includes("voce") || tags.includes("tamno-voce") || tags.includes("borovnica"))) {
    return "fruity";
  }
  const earthyTags = tags.filter((t) =>
    t === "zemljano" || t === "koza" || t === "duhan",
  ).length;
  const cocoaTags = tags.filter((t) =>
    t === "kakao" || t === "karamela" || t === "orasasti",
  ).length;
  if (earthyTags >= 2 || (earthyTags >= 1 && cocoaTags === 0)) {
    return "earthy";
  }
  if (tags.includes("cvjetno") || /geisha|yirgacheffe|panama/.test(blob)) {
    return "floral";
  }
  if (
    tags.includes("citrus") ||
    tags.includes("voce") ||
    tags.includes("tamno-voce") ||
    tags.includes("tropsko-voce") ||
    /kenya|kenij|burundi|rwanda/.test(blob)
  ) {
    return "fruity";
  }
  if (
    tags.includes("zacini") ||
    tags.includes("papar") ||
    (tags.includes("dim") && cocoaTags === 0)
  ) {
    return "herbalSavory";
  }
  return "nuttyCocoa";
}

function hasMilk(drink: Drink): boolean {
  return drink.coffeeDetail?.milk === true || drink.style === "milk";
}

export function inferCoffeeProfile(drink: Drink): CoffeeProfile {
  const tags = normalizeTags(drink.flavorTags);
  const roast = inferRoast(drink);
  return {
    roast,
    intensity: inferIntensity(drink),
    acidity: inferAcidity(drink, roast, tags),
    flavorFamily: inferFlavorFamily(drink, tags, regionBlob(drink)),
  };
}

const EARTHY_CIGAR = new Set(["zemljano", "duhan", "koza", "dim", "drvo", "cedar"]);
const NUTTY_CIGAR = new Set(["kakao", "karamela", "orasasti", "kava", "slatko", "med"]);
const FLORAL_CIGAR = new Set(["cvjetno", "citrus", "kremasto", "med", "caj", "voce"]);
const SPICY_CIGAR = new Set(["zacini", "papar", "zacini-slatki"]);

/**
 * Soft coffee-specific reasons. Empty for non-coffee drinks.
 * Body matching stays in pairing.ts — this layer only nudges intensity/flavor/contrast.
 */
export function coffeePairingReasons(
  cigar: Cigar,
  drink: Drink,
): PairingReason[] {
  if (drink.category !== "coffee") return [];

  const reasons: PairingReason[] = [];
  const profile = inferCoffeeProfile(drink);
  const cigarTags = normalizeTags(cigar.flavorTags);

  // I — intensity / roast vs cigar strength
  const strength = cigar.strength;
  const intensityAligned =
    (profile.intensity === "high" && strength >= 4) ||
    (profile.intensity === "low" && strength <= 2) ||
    (profile.intensity === "medium" && strength >= 2 && strength <= 4);
  const intensityClash =
    (profile.intensity === "high" && strength <= 2) ||
    (profile.intensity === "low" && strength >= 4);

  if (intensityAligned) {
    const pts = WEIGHTS.coffeeIntensityMatch;
    reasons.push({
      rule: "coffee-intensity-match",
      score: pts,
      text: {
        hr:
          profile.intensity === "high"
            ? "Gust espresso/tamna kava traži i podnosi jaču cigaru."
            : profile.intensity === "low"
              ? "Lagana filtar kava i blaga cigara dijele isti ritam intenziteta."
              : "Srednja snaga kave i cigare ostaju u ravnoteži.",
        en:
          profile.intensity === "high"
            ? "Dense espresso/dark coffee wants and handles a stronger cigar."
            : profile.intensity === "low"
              ? "Light filter coffee and a mild cigar share the same intensity pace."
              : "Medium coffee and cigar strength stay balanced.",
      },
    });
  } else if (intensityClash) {
    const pts = -WEIGHTS.coffeeIntensityMismatch;
    reasons.push({
      rule: "coffee-intensity-mismatch",
      score: pts,
      text: {
        hr:
          profile.intensity === "high"
            ? "Gusti napitak pregazit će ovako blagu cigaru."
            : "Jaka cigara pregazit će delikatnu filtar kavu.",
        en:
          profile.intensity === "high"
            ? "This dense cup will steamroll such a mild cigar."
            : "A strong cigar will steamroll this delicate filter coffee.",
      },
    });
  }

  // Delicate floral/citrus bridge vs overwhelm (body-first for tea-like cups)
  const delicate =
    profile.flavorFamily === "floral" ||
    (profile.roast === "light" && profile.intensity === "low");
  if (delicate && cigar.body <= 2 && strength <= 2) {
    const pts = WEIGHTS.coffeeDelicateBridge;
    reasons.push({
      rule: "coffee-delicate-bridge",
      score: pts,
      text: {
        hr: "Cvjetno-citrusna kava traži delikatnog partnera da se ne izgubi.",
        en: "Floral-citrus coffee needs a delicate partner so it is not lost.",
      },
    });
  } else if (delicate && (cigar.body >= 4 || strength >= 4)) {
    const pts = -WEIGHTS.coffeeDelicateOverwhelm;
    reasons.push({
      rule: "coffee-delicate-overwhelm",
      score: pts,
      text: {
        hr: "Puna/jaka cigara pregazit će tea-like kavu bez obzira na note.",
        en: "A full/strong cigar drowns tea-like coffee regardless of shared notes.",
      },
    });
  }

  // F — complementary flavor bridges
  let bridge: "earthy" | "nutty" | "floral" | null = null;
  if (
    profile.flavorFamily === "earthy" &&
    cigarTags.some((t) => EARTHY_CIGAR.has(t))
  ) {
    bridge = "earthy";
  } else if (
    profile.flavorFamily === "nuttyCocoa" &&
    cigarTags.some((t) => NUTTY_CIGAR.has(t))
  ) {
    bridge = "nutty";
  } else if (
    profile.flavorFamily === "herbalSavory" &&
    cigarTags.some((t) => SPICY_CIGAR.has(t) || EARTHY_CIGAR.has(t))
  ) {
    bridge = "earthy";
  } else if (
    (profile.flavorFamily === "floral" || profile.flavorFamily === "fruity") &&
    cigarTags.some((t) => FLORAL_CIGAR.has(t)) &&
    cigar.body <= 3
  ) {
    bridge = "floral";
  }

  if (bridge) {
    const pts = WEIGHTS.coffeeFlavorBridge;
    const copy =
      bridge === "earthy"
        ? {
            hr: "Zemljano-začinski most: indonezijski / teški profil uz sličan dim.",
            en: "Earthy-spicy bridge: Indonesian/heavy cup with a similar smoke.",
          }
        : bridge === "nutty"
          ? {
              hr: "Oražasto-kakao most: slatka, niska kiselost uz kakao/karamele dim.",
              en: "Nutty-cocoa bridge: sweet, low-acid cup with cocoa/caramel smoke.",
            }
          : {
              hr: "Cvjetno-citrusni most uz dovoljno laganu cigaru.",
              en: "Floral-citrus bridge with a cigar light enough to keep up.",
            };
    reasons.push({
      rule: "coffee-flavor-bridge",
      score: pts,
      text: copy,
    });
  }

  // Contrast: high acidity as cleanser for heavy cigar
  if (profile.acidity === "high" && cigar.body >= 4) {
    const pts = WEIGHTS.coffeeAcidityContrast;
    reasons.push({
      rule: "coffee-acidity-contrast",
      score: pts,
      text: {
        hr: "Visoka kiselost kave čisti nepce uz tešku cigaru (kontrast).",
        en: "High coffee acidity cleanses the palate against a heavy cigar (contrast).",
      },
    });
  }

  // Sweetness mellows spicy/earthy cigar
  if (
    drink.sweetness >= 3 &&
    profile.acidity !== "high" &&
    (profile.flavorFamily === "nuttyCocoa" || drink.sweetness >= 4) &&
    cigarTags.some((t) => SPICY_CIGAR.has(t) || EARTHY_CIGAR.has(t))
  ) {
    const pts = WEIGHTS.coffeeSweetMellow;
    reasons.push({
      rule: "coffee-sweet-mellow",
      score: pts,
      text: {
        hr: "Slatkoća kave ublažava začinski ili zemljani dim.",
        en: "Coffee sweetness softens spicy or earthy smoke.",
      },
    });
  }

  // Milk: softens pepper, hides nuance, loses to full cigars
  if (hasMilk(drink)) {
    if (cigarTags.some((t) => SPICY_CIGAR.has(t)) && cigar.body <= 3) {
      reasons.push({
        rule: "coffee-milk-mellow",
        score: WEIGHTS.coffeeMilkMellow,
        text: {
          hr: "Mlijeko omekšava papar u dimu, pa blaga do srednja cigara ostaje čitka.",
          en: "Milk softens pepper in the smoke, so a mild-to-medium cigar stays readable.",
        },
      });
    }
    if (
      cigarTags.some((t) => t === "cvjetno" || t === "citrus") ||
      (cigar.body <= 2 && cigar.strength <= 2 && profile.flavorFamily === "floral")
    ) {
      reasons.push({
        rule: "coffee-milk-mask",
        score: -WEIGHTS.coffeeMilkMask,
        text: {
          hr: "Mlijeko pokriva cvjetne i mineralne note — fina cigara ostaje iza zavjese.",
          en: "Milk covers floral and mineral notes — a fine cigar stays behind a curtain.",
        },
      });
    }
    if (cigar.body >= 4 && cigar.strength >= 4) {
      reasons.push({
        rule: "coffee-milk-heavy",
        score: -WEIGHTS.coffeeMilkHeavy,
        text: {
          hr: "Puna, jaka cigara pregazi mliječnu šalicu; biraj espresso ili french press.",
          en: "A full, strong cigar overruns a milky cup; pick espresso or french press.",
        },
      });
    }
  }

  // Natural process: fruit body as contrast with a cigar light enough to keep it
  if (
    drink.coffeeDetail?.process === "natural" &&
    (profile.flavorFamily === "fruity" || drink.sweetness >= 4) &&
    cigar.body <= 3 &&
    cigar.strength <= 3
  ) {
    reasons.push({
      rule: "coffee-natural-fruit",
      score: WEIGHTS.coffeeProcessBridge,
      text: {
        hr: "Natural obrada diže voće i tijelo — kontrast uz cigaru koja još ostavlja prostora.",
        en: "Natural process lifts fruit and body — contrast with a cigar that still leaves room.",
      },
    });
  }

  // Spiked coffee sits with after-dinner weight
  if (drink.style === "spiked") {
    if (cigar.body >= 3 && cigar.strength >= 3) {
      reasons.push({
        rule: "coffee-spiked-weight",
        score: WEIGHTS.coffeeSpikedWeight,
        text: {
          hr: "Kava s žesticom nosi srednju do punu cigaru nakon jela.",
          en: "Coffee with spirit carries a medium to full cigar after a meal.",
        },
      });
    } else if (cigar.body <= 2) {
      reasons.push({
        rule: "coffee-spiked-delicate",
        score: -WEIGHTS.coffeeSpikedDelicate,
        text: {
          hr: "Žestica u šalici pregazi blagu cigaru; ostavi Shade za jutarnji filter.",
          en: "Spirit in the cup overruns a mild cigar; leave Shade for morning filter.",
        },
      });
    }
  }

  return reasons;
}
