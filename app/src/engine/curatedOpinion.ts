// Kurirana poruka za par cigara–piće.
// PRAVILO: poruka postoji isključivo kad je match >= 80.
// Nikad ne čita drink.cigarHint (Excel). Tekst je uvijek specifičan za taj par.

import type { Cigar, Drink, LocalizedText, PairingReason } from "../types";
import { WEIGHTS } from "./rules";

const BODY_HR = ["", "vrlo lagano", "lagano", "srednje", "puno", "vrlo puno"];
const BODY_EN = ["", "very light", "light", "medium", "full", "very full"];
const STRENGTH_HR = ["", "blaga", "lagana", "srednja", "jaka", "vrlo jaka"];
const STRENGTH_EN = ["", "mild", "light", "medium", "strong", "very strong"];

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

function wrapperLabel(kind: ReturnType<typeof wrapperKind>, raw: string): string {
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
  const w = wrapperLabel(kind, cigar.wrapper);

  if (profile === "clean-barbados") {
    if (kind === "habano" || (kind === "maduro" && /san andr/i.test(cigar.wrapper))) {
      return {
        hr: `${w} daje dovoljno strukture da se ne izgubi uz suhi, hrastov profil — bez da pregazi piće.`,
        en: `${w} brings enough structure without drowning the dry, oaky profile.`,
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
      hr: `${w} i ${drink.name} su u istom registru punoće — nijedno ne nadjačava drugo.`,
      en: `${w} and ${drink.name} sit in the same weight class — neither overpowers the other.`,
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

function sharedTags(cigar: Cigar, drink: Drink): string[] {
  return cigar.flavorTags.filter((t) => drink.flavorTags.includes(t));
}

function alwaysUniqueBody(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): { hr: string; en: string } {
  const kind = wrapperKind(cigar.wrapper);
  const w = wrapperLabel(kind, cigar.wrapper);
  const shared = sharedTags(cigar, drink);
  const synergy = synergyLine(reasons);
  const verdict = wrapperVerdict(drinkProfile(drink), kind, cigar, drink);

  if (synergy && verdict) {
    return { hr: `${synergy.hr} ${verdict.hr}`, en: `${synergy.en} ${verdict.en}` };
  }
  if (synergy) {
    return {
      hr: `${synergy.hr} ${w} (${STRENGTH_HR[cigar.strength]}) uz ${drink.style} — ${score}%.`,
      en: `${synergy.en} ${w} (${STRENGTH_EN[cigar.strength]}) with ${drink.style} — ${score}%.`,
    };
  }
  if (verdict) return verdict;

  if (shared.length >= 1) {
    const tags = shared.slice(0, 3).join(", ");
    return {
      hr: `Dijele ${tags}; ${w} (${BODY_HR[cigar.body]}) i ${drink.name} grade koherentan par uz ${score}%.`,
      en: `They share ${tags}; ${w} (${BODY_EN[cigar.body]}) and ${drink.name} form a coherent pair at ${score}%.`,
    };
  }

  return {
    hr: `${w}, ${STRENGTH_HR[cigar.strength]} snaga i ${drink.category} (${drink.style}, ${drink.region}) — ${score}% podudaranja.`,
    en: `${w}, ${STRENGTH_EN[cigar.strength]} strength and ${drink.category} (${drink.style}, ${drink.region}) — ${score}% match.`,
  };
}

/**
 * Kurirana poruka za par.
 * - score < 80 → null (nikad ne prikazati)
 * - score >= 80 → uvijek jedinstven tekst za taj par
 * Score je obavezan — bez scorea nema poruke.
 */
export function curatedPairingOpinion(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): LocalizedText | null {
  if (score < WEIGHTS.curatedHintMinScore) return null;

  const cigarName = `${cigar.brand} ${cigar.line}`.trim();
  const body = alwaysUniqueBody(cigar, drink, reasons, score);

  return {
    hr: `${cigarName} i ${drink.name} — ${body.hr}`,
    en: `${cigarName} and ${drink.name} — ${body.en}`,
  };
}
