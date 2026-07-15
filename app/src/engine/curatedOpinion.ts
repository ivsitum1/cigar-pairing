// Dinamičko mišljenje o paru — zamjena za statički cigarHint iz Excela.
// Generira se iz konkretne cigare, pića i razloga bodovanja.

import type { Cigar, Drink, LocalizedText, PairingReason } from "../types";
import { WEIGHTS } from "./rules";

const BODY_HR = ["", "vrlo lagano", "lagano", "srednje", "puno", "vrlo puno"];
const BODY_EN = ["", "very light", "light", "medium", "full", "very full"];
const STRENGTH_HR = ["", "blaga", "lagana", "srednja", "jaka", "vrlo jaka"];
const STRENGTH_EN = ["", "mild", "light", "medium", "strong", "very strong"];
const SWEET_HR = ["", "suvo", "polusuho", "uravnoteženo", "slatko", "vrlo slatko"];
const SWEET_EN = ["", "dry", "off-dry", "balanced", "sweet", "very sweet"];

const WRAPPER = {
  connecticut: /connecticut|claro|shade/i,
  habano: /habano|corojo|sumatra|cameroon|honduran habano/i,
  maduro: /maduro|oscuro|san andr[eé]s|broadleaf|brazil/i,
  natural: /\bnatural\b/i,
} as const;

function wrapperKind(wrapper: string): keyof typeof WRAPPER | "other" {
  if (WRAPPER.natural.test(wrapper)) return "natural";
  if (WRAPPER.connecticut.test(wrapper)) return "connecticut";
  if (WRAPPER.maduro.test(wrapper)) return "maduro";
  if (WRAPPER.habano.test(wrapper)) return "habano";
  return "other";
}

function wrapperLabelHr(kind: ReturnType<typeof wrapperKind>, raw: string): string {
  switch (kind) {
    case "connecticut":
      return "Connecticut";
    case "habano":
      return "Habano";
    case "maduro":
      return /san andr/i.test(raw) ? "San Andrés maduro" : "maduro";
    case "natural":
      return "natural wrapper";
    default:
      return raw.split(/[;(]/)[0]?.trim() || raw;
  }
}

function wrapperLabelEn(kind: ReturnType<typeof wrapperKind>, raw: string): string {
  switch (kind) {
    case "connecticut":
      return "Connecticut";
    case "habano":
      return "Habano";
    case "maduro":
      return /san andr/i.test(raw) ? "San Andrés maduro" : "maduro";
    case "natural":
      return "natural wrapper";
    default:
      return raw.split(/[;(]/)[0]?.trim() || raw;
  }
}

function drinkProfile(drink: Drink): string {
  const { category, style, body, sweetness } = drink;
  if (category === "rum") {
    if (style === "barbados" || /foursquare|doorly|barbados/i.test(drink.name))
      return "clean-barbados";
    if (style === "jamaica" || drink.flavorTags.includes("ester-funk")) return "jamaica-funk";
    if (style === "agricole") return "agricole";
    if (sweetness >= 4) return "sweet-rum";
    if (style === "demerara" || style === "solera") return "rich-rum";
  }
  if (category === "whisky") {
    if (/islay|peated/i.test(style)) return "peated-whisky";
    if (/speyside|japanese|irish/i.test(style)) return "elegant-whisky";
    if (/bourbon|rye/i.test(style)) return "bold-whisky";
  }
  if (category === "brandy") {
    if (/cognac-xo|armagnac|brandy-de-jerez/i.test(style)) return "aged-brandy";
    if (/calvados/i.test(style)) return "calvados";
    if (/vinjak/i.test(style)) return "vinjak";
  }
  if (category === "gin") return "gin";
  if (category === "wine") {
    if (sweetness >= 4) return "sweet-wine";
    if (/sparkling|champagne|prosecco/i.test(style)) return "sparkling";
    return "still-wine";
  }
  if (category === "coffee") {
    if (/dark|espresso-dark/i.test(style)) return "dark-coffee";
    return "light-coffee";
  }
  return body >= 4 ? "full-spirit" : body <= 2 ? "light-spirit" : "balanced-spirit";
}

function wrapperVerdict(
  profile: string,
  kind: ReturnType<typeof wrapperKind>,
  cigar: Cigar,
  drink: Drink,
): { hr: string; en: string } | null {
  const wHr = wrapperLabelHr(kind, cigar.wrapper);
  const wEn = wrapperLabelEn(kind, cigar.wrapper);

  if (profile === "clean-barbados") {
    if (kind === "habano" || (kind === "maduro" && /san andr/i.test(cigar.wrapper))) {
      return {
        hr: `${wHr} daje dovoljno strukture da se ne izgubi uz suhi, hrastov profil — bez da pregazi piće.`,
        en: `${wEn} brings enough structure without drowning the dry, oaky profile.`,
      };
    }
    if (kind === "natural") {
      return {
        hr: `Natural wrapper nije idealan uz čisti Barbados rum — Habano ili San Andrés maduro bolje nose suho voće i hrast.`,
        en: `Natural wrapper is not ideal with a clean Barbados rum — Habano or San Andrés maduro carry the dry fruit and oak better.`,
      };
    }
    if (kind === "connecticut" && cigar.body <= 2) {
      return {
        hr: `Blagi Connecticut može raditi uz laganiji tretman, ali Habano daje puniji balans uz Foursquare stil.`,
        en: `A mild Connecticut can work if treated gently, but Habano gives a fuller balance with the Foursquare style.`,
      };
    }
  }

  if (profile === "jamaica-funk" && kind === "connecticut" && cigar.strength <= 2) {
    return {
      hr: `Esterski, puni rum traži jaču cigaru — Connecticut bi se brzo izgubio.`,
      en: `This estery, full rum needs a stronger cigar — Connecticut would disappear quickly.`,
    };
  }

  if (profile === "agricole" && (kind === "maduro" || cigar.body >= 4)) {
    return {
      hr: `Travnati agricole voli laganiju do srednje cigare — puna maduro bi pregazila vegetalne note.`,
      en: `Grassy agricole prefers a mild-to-medium cigar — a full maduro would swamp the vegetal notes.`,
    };
  }

  if (profile === "sweet-rum" && kind === "maduro" && drink.sweetness >= 4) {
    return {
      hr: `Slatkoća ruma i tamni wrapper grade klasičan kontrast — karamela i dim u ravnoteži.`,
      en: `The rum's sweetness and a dark wrapper form a classic contrast — caramel and smoke in balance.`,
    };
  }

  if (profile === "peated-whisky" && kind === "connecticut") {
    return {
      hr: `Dimljeni whisky pregazio bi blagi Connecticut — Habano ili maduro podnose dim.`,
      en: `Peated whisky would steamroll a mild Connecticut — Habano or maduro can handle the smoke.`,
    };
  }

  if (profile === "aged-brandy" && kind === "habano") {
    return {
      hr: `Odležani brandy i Habano dijele suho voće, hrast i začine — klasičan večernji par.`,
      en: `Aged brandy and Habano share dried fruit, oak and spice — a classic evening pairing.`,
    };
  }

  if (profile === "sparkling" && cigar.body >= 4) {
    return {
      hr: `Pjenusac traži laganiju cigaru — ova punina može pregaziti mjehuriće i kiselinu.`,
      en: `Sparkling wine wants a lighter cigar — this much body can overwhelm the bubbles and acidity.`,
    };
  }

  if (profile === "dark-coffee" && kind === "maduro") {
    return {
      hr: `Tamna kava i maduro wrapper dijele kakao i karamelu — prirodan, desertni smjer.`,
      en: `Dark coffee and maduro share cocoa and caramel — a natural dessert direction.`,
    };
  }

  if (cigar.body === drink.body && kind !== "other") {
    return {
      hr: `${wHr} i ${drink.name} su u istom registru punoće — nijedno ne nadjačava drugo.`,
      en: `${wEn} and ${drink.name} sit in the same weight class — neither overpowers the other.`,
    };
  }

  return null;
}

function synergyLine(reasons: PairingReason[]): { hr: string; en: string } | null {
  const top = reasons.filter((r) => r.score > 0).sort((a, b) => b.score - a.score)[0];
  if (!top) return null;
  if (top.rule === "body-match") {
    return {
      hr: "Tijela se poklapaju — dim i okus ostaju u istom registru.",
      en: "Bodies align — smoke and flavour stay in the same register.",
    };
  }
  if (top.rule === "flavor-shared") {
    return {
      hr: "Dijele ključne arome, pa se okusi nadograđuju umjesto da se tuku.",
      en: "They share key aromas, so flavours build on each other instead of fighting.",
    };
  }
  if (top.rule === "flavor-complement") {
    return {
      hr: "Note se nadopunjuju — kontrast je namjeran, ne slučajan.",
      en: "The notes complement each other — the contrast is deliberate, not accidental.",
    };
  }
  if (top.rule === "contrast-sweet-maduro") {
    return {
      hr: "Slatkoća pića lijepo presijeca tamni dim — to je ono što tražiš od ovog para.",
      en: "The drink's sweetness neatly cuts through dark smoke — what you want from this pair.",
    };
  }
  if (top.rule === "wrapper-affinity") {
    return {
      hr: "Wrapper i profil pića prirodno idu u istom smjeru.",
      en: "The wrapper and the drink profile naturally pull in the same direction.",
    };
  }
  if (top.rule === "power-match") {
    return {
      hr: "Oba su intenzivna — nijedno ne zaostaje za drugim.",
      en: "Both are intense — neither lags behind the other.",
    };
  }
  return {
    hr: top.text.hr.replace(/\.$/, ""),
    en: top.text.en.replace(/\.$/, ""),
  };
}

function openingLine(cigar: Cigar, drink: Drink): { hr: string; en: string } {
  const cigarName = `${cigar.brand} ${cigar.line}`.trim();
  return {
    hr: `${cigarName} i ${drink.name} —`,
    en: `${cigarName} and ${drink.name} —`,
  };
}

function sharedTags(cigar: Cigar, drink: Drink): string[] {
  return cigar.flavorTags.filter((t) => drink.flavorTags.includes(t));
}

/** Jedinstveni fallback kad nema synergy/verdict — koristi profil para i bodovanje. */
function highScoreFallback(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): { hr: string; en: string } {
  const kind = wrapperKind(cigar.wrapper);
  const wHr = wrapperLabelHr(kind, cigar.wrapper);
  const wEn = wrapperLabelEn(kind, cigar.wrapper);
  const shared = sharedTags(cigar, drink);
  const bodyDelta = cigar.body - drink.body;
  const topPositive = reasons.filter((r) => r.score > 0).sort((a, b) => b.score - a.score)[0];

  if (shared.length >= 2) {
    const tags = shared.slice(0, 3).join(", ");
    return {
      hr: `Dijele ${tags}; ${wHr} (${BODY_HR[cigar.body]}) i ${drink.name} (${BODY_HR[drink.body]}) grade koherentan profil uz ${score}% podudaranja.`,
      en: `They share ${tags}; ${wEn} (${BODY_EN[cigar.body]}) and ${drink.name} (${BODY_EN[drink.body]}) build a coherent profile at ${score}% match.`,
    };
  }

  if (bodyDelta === 0) {
    return {
      hr: `Ista punoća (${BODY_HR[cigar.body]}) i ${STRENGTH_HR[cigar.strength]} snaga uz ${wHr} drže par u ravnoteži — ${score}% je opravdan rezultat.`,
      en: `Matching weight (${BODY_EN[cigar.body]}) and ${STRENGTH_EN[cigar.strength]} strength with ${wEn} keep the pair balanced — ${score}% is a fair read.`,
    };
  }

  if (Math.abs(bodyDelta) === 1) {
    const heavier = bodyDelta > 0 ? "cigara" : "piće";
    const heavierEn = bodyDelta > 0 ? "cigar" : "drink";
    return {
      hr: `Blaga razlika u tijelu — ${heavier} vodi, ali ${wHr} i ${drink.style} (${drink.region}) ostaju kompatibilni uz ${score}%.`,
      en: `A slight body gap — the ${heavierEn} leads, but ${wEn} and ${drink.style} (${drink.region}) still align at ${score}%.`,
    };
  }

  if (topPositive) {
    return {
      hr: `${topPositive.text.hr.replace(/\.$/, "")} — uz ${wHr} i slatkoću ${SWEET_HR[drink.sweetness]} to drži par iznad ${WEIGHTS.curatedHintMinScore}%.`,
      en: `${topPositive.text.en.replace(/\.$/, "")} — with ${wEn} and ${SWEET_EN[drink.sweetness]} sweetness that keeps the pair above ${WEIGHTS.curatedHintMinScore}%.`,
    };
  }

  return {
    hr: `${wHr}, ${STRENGTH_HR[cigar.strength]} snaga i ${drink.category} profil (${drink.style}) daju solidan večernji par — ${score}% podudaranja.`,
    en: `${wEn}, ${STRENGTH_EN[cigar.strength]} strength and a ${drink.category} profile (${drink.style}) make a solid evening pair — ${score}% match.`,
  };
}

/** Mišljenje o konkretnom paru. Iznad praga uvijek vraća tekst (nikad null). */
export function curatedPairingOpinion(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score?: number,
): LocalizedText | null {
  if (score != null && score < WEIGHTS.curatedHintMinScore) return null;

  const open = openingLine(cigar, drink);
  const synergy = synergyLine(reasons);
  const verdict = wrapperVerdict(drinkProfile(drink), wrapperKind(cigar.wrapper), cigar, drink);

  const partsHr = [open.hr];
  const partsEn = [open.en];

  if (synergy) {
    partsHr.push(synergy.hr);
    partsEn.push(synergy.en);
  }
  if (verdict) {
    partsHr.push(verdict.hr);
    partsEn.push(verdict.en);
  }

  const aboveThreshold =
    score != null && score >= WEIGHTS.curatedHintMinScore;

  if (partsHr.length <= 1) {
    if (!aboveThreshold) return null;
    const fallback = highScoreFallback(cigar, drink, reasons, score);
    partsHr.push(fallback.hr);
    partsEn.push(fallback.en);
  }

  return {
    hr: partsHr.join(" "),
    en: partsEn.join(" "),
  };
}
