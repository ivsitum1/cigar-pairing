// Coffee↔cigar overlay.
// Coffee side (roast, acidity, body, origin/flavor families): distilled from
// James Hoffmann, The World Atlas of Coffee (From Beans to Brewing).
// Cigar pairing rules apply that book's balance / intensity / harmony logic;
// they are not a chapter from the atlas. Soft nudges only (< bodyPerStep).
// Reference model: data/coffeePairingModel.json — validate weights empirically.

import type { Cigar, Drink, PairingReason } from "../types";
import { WEIGHTS, normalizeTags } from "./rules";

export type CoffeeRoast = "light" | "medium" | "dark";
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

// `style` kod kave nosi PRIPREMU; prženje je vlastito polje (`roast`).
// Stari, spojeni ključevi ("espresso-dark", "filter-light") ostaju pokriveni
// kao zaliha za zapise koji još nisu migrirani.
const LEGACY_DARK_STYLES = new Set([
  "espresso-dark",
  "filter-dark",
  "turkish",
  "moka",
]);
const LEGACY_LIGHT_STYLES = new Set(["filter-light"]);

/** Priprema koja daje gust ekstrakt (visok TDS) bez obzira na zrno. */
const HIGH_TDS_PREPS = new Set([
  "espresso",
  "ristretto",
  "turkish",
  "moka",
  "espresso-dark",
  "espresso-medium",
]);
// Americano = espresso + hot water → medium TDS (body drives the rest).
const LOW_TDS_PREPS = new Set(["cold-brew", "cold", "filter-light"]);

/** Region / name hints for acidity & origin character. */
function regionBlob(drink: Drink): string {
  return `${drink.region ?? ""} ${drink.country ?? ""} ${drink.name}`.toLowerCase();
}

function inferRoast(drink: Drink): CoffeeRoast {
  if (drink.roast) return drink.roast;
  if (LEGACY_DARK_STYLES.has(drink.style)) return "dark";
  if (LEGACY_LIGHT_STYLES.has(drink.style)) return "light";
  return "medium";
}

/**
 * Gustoća šalice: prvo priprema, pa tijelo. Svijetli filter je čajan i kad je
 * zrno bogato; espresso je gust i kad je zrno svijetlo.
 */
function inferIntensity(style: string, roast: CoffeeRoast, body: number): CoffeeIntensity {
  if (style === "americano") return "medium";
  if (HIGH_TDS_PREPS.has(style) || body >= 4.5) return "high";
  if (LOW_TDS_PREPS.has(style) || (style === "filter" && roast === "light")) return "low";
  if (body <= 2) return "low";
  return "medium";
}

function inferAcidity(drink: Drink, roast: CoffeeRoast, tags: string[]): CoffeeAcidity {
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

function inferFlavorFamily(tags: string[], blob: string): CoffeeFlavorFamily {
  // Regional earthy (Giling Basah / monsoon) wins over cocoa tags.
  if (/sumatra|indonez|giling|malabar/.test(blob)) {
    return "earthy";
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

export function inferCoffeeProfile(drink: Drink): CoffeeProfile {
  const tags = normalizeTags(drink.flavorTags);
  const roast = inferRoast(drink);
  return {
    roast,
    intensity: inferIntensity(drink.style, roast, drink.body),
    acidity: inferAcidity(drink, roast, tags),
    flavorFamily: inferFlavorFamily(tags, regionBlob(drink)),
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

  return reasons;
}
