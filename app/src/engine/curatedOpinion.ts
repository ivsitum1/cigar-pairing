// Kurirana poruka za par cigara–piće. Tri zone:
//   score >= curatedHintMinScore (80)  -> pozitivna preporuka (tone: praise)
//   score <= curatedWarnMaxScore (45)  -> negativno misljenje (tone: warning)
//   izmedju                            -> null (nista posebno za reci)
// Ton UVIJEK prati score — pohvala uz visok match, upozorenje uz los.
// Nikad ne čita drink.cigarHint (Excel). Tekst je uvijek specifičan za taj par.

import type { Cigar, Drink, LocalizedText, PairingReason } from "../types";
import { drinkNameLoc } from "../lib/drinkName";
import { WEIGHTS, flavorLabel, normalizeTags } from "./rules";

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
  if (category === "tequila") {
    if (/extra-anejo|anejo/i.test(style)) return "aged-tequila";
    if (/reposado/i.test(style)) return "reposado-tequila";
    return "blanco-tequila";
  }
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

// Verdikt uz kuriranu poruku. Poruka se prikazuje ISKLJUCIVO kod matcha
// >= 80, pa ovdje smiju zivjeti samo pozitivna/neutralna objasnjenja —
// upozorenja ("wrapper nije idealan", "pregazio bi") uz visok match su
// kontradikcija i takve kombinacije ionako obaraju score ispod praga.
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
        hr: `${w} daje dovoljno strukture za suhi, hrastov profil, a piću ostavlja prostora.`,
        en: `${w} brings enough structure for the dry, oaky profile while leaving the drink room to breathe.`,
      };
    }
  }

  if (profile === "sweet-rum" && kind === "maduro" && drink.sweetness >= 4) {
    return {
      hr: `Slatkoća ruma i tamni wrapper grade klasičan kontrast — karamela i dim u ravnoteži.`,
      en: `The rum's sweetness and a dark wrapper form a classic contrast — caramel and smoke in balance.`,
    };
  }

  if (profile === "aged-brandy" && kind === "habano") {
    return {
      hr: `Odležani brandy i Habano dijele suho voće, hrast i začine — klasičan večernji par.`,
      en: `Aged brandy and Habano share dried fruit, oak and spice — a classic evening pairing.`,
    };
  }

  if (profile === "peated-whisky" && (kind === "habano" || kind === "maduro")) {
    return {
      hr: `${w} podnosi treset i dim — cigara i whisky ostaju ravnopravni.`,
      en: `${w} stands up to peat and smoke — cigar and whisky stay on equal footing.`,
    };
  }

  if (profile === "agricole" && kind === "connecticut") {
    return {
      hr: `Travnati agricole i svijetli Connecticut dijele svježi, vegetalni registar.`,
      en: `Grassy agricole and a light Connecticut share the same fresh, vegetal register.`,
    };
  }

  if (profile === "dark-coffee" && kind === "maduro") {
    return {
      hr: `Tamna kava i maduro wrapper dijele kakao i karamelu — prirodan, desertni smjer.`,
      en: `Dark coffee and maduro share cocoa and caramel — a natural dessert direction.`,
    };
  }

  if (profile === "aged-tequila" && kind === "maduro") {
    return {
      hr: `Odležana tequila i maduro dijele hrast, kakao i začine — čest sipping spoj.`,
      en: `Aged tequila and maduro share oak, cocoa and spice — a common sipping match.`,
    };
  }

  if (profile === "reposado-tequila" && (kind === "habano" || kind === "natural")) {
    return {
      hr: `Reposado i ${w} dijele srednju težinu — agava i hrast uz duhan bez borbe.`,
      en: `Reposado and ${w} share medium weight — agave and oak with tobacco without a fight.`,
    };
  }

  // Namjerno NEMA generičkog "isti registar punoće" verdikta: tijelo se već
  // spominje u blurbu ("Bodies match…") i u synergy liniji, pa bi ga treći put
  // ponovilo (uz ponovljeno ime pića) — kurirani okvir tako postaje nečitljiv.
  return null;
}

// Negativan verdikt za parove koji se zaista ne poklapaju (score <= 45) —
// konkretan razlog zasto kombinaciju ne preporucujemo.
function wrapperWarning(
  profile: string,
  kind: ReturnType<typeof wrapperKind>,
  cigar: Cigar,
): { hr: string; en: string } | null {
  if (profile === "clean-barbados" && kind === "natural") {
    return {
      hr: `natural wrapper nije idealan uz čisti Barbados rum — Habano ili San Andrés maduro bolje nose suho voće i hrast.`,
      en: `a natural wrapper is not ideal with a clean Barbados rum — Habano or San Andrés maduro carry the dry fruit and oak better.`,
    };
  }
  if (profile === "jamaica-funk" && kind === "connecticut" && cigar.strength <= 2) {
    return {
      hr: `esterski, puni rum traži jaču cigaru — blagi Connecticut bi se brzo izgubio.`,
      en: `this estery, full rum needs a stronger cigar — a mild Connecticut would disappear quickly.`,
    };
  }
  if (profile === "agricole" && (kind === "maduro" || cigar.body >= 4)) {
    return {
      hr: `travnati agricole voli laganu do srednju cigaru — ovako puna pregazila bi vegetalne note.`,
      en: `grassy agricole prefers a mild-to-medium cigar — this much body would swamp the vegetal notes.`,
    };
  }
  if (profile === "peated-whisky" && kind === "connecticut") {
    return {
      hr: `dimljeni whisky pregazio bi blagi Connecticut — Habano ili maduro podnose treset.`,
      en: `peated whisky would steamroll a mild Connecticut — Habano or maduro can handle the peat.`,
    };
  }
  if (profile === "sparkling" && cigar.body >= 4) {
    return {
      hr: `pjenušac traži laganiju cigaru — ova punina gazi mjehuriće i kiselinu.`,
      en: `sparkling wine wants a lighter cigar — this much body tramples the bubbles and acidity.`,
    };
  }
  if ((profile === "light-coffee" || profile === "gin" || profile === "blanco-tequila") && cigar.body >= 4) {
    return {
      hr: `ovako delikatno piće traži laganiju cigaru — puni dim ostaje sam na sceni.`,
      en: `such a delicate drink needs a lighter cigar — the full smoke ends up alone on stage.`,
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

// isti sinonimi kao u scorePairing — poruka mora vidjeti iste note kao engine
function sharedTags(cigar: Cigar, drink: Drink): string[] {
  const drinkTags = normalizeTags(drink.flavorTags);
  return normalizeTags(cigar.flavorTags).filter((t) => drinkTags.includes(t));
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

  // Specifičan verdikt (npr. "Habano daje strukturu za suhi, hrastov profil…")
  // stoji sam — jedna bogata, konkretna rečenica bez ponavljanja.
  if (verdict) return verdict;

  // Inače: jedna synergy linija, po potrebi obogaćena zajedničkim notama
  // (prevedenim!) da svaki par dobije svoju specifičnost — bez dvostrukog
  // spominjanja tijela i bez ponovljenog imena pića.
  if (synergy) {
    if (shared.length >= 1) {
      const hrTags = shared.slice(0, 3).map((t) => flavorLabel(t, "hr")).join(", ");
      const enTags = shared.slice(0, 3).map((t) => flavorLabel(t, "en")).join(", ");
      return {
        hr: `${synergy.hr} Spaja ih ${hrTags}.`,
        en: `${synergy.en} They meet on ${enTags}.`,
      };
    }
    return synergy;
  }

  if (shared.length >= 1) {
    const hrTags = shared.slice(0, 3).map((t) => flavorLabel(t, "hr")).join(", ");
    const enTags = shared.slice(0, 3).map((t) => flavorLabel(t, "en")).join(", ");
    return {
      hr: `${w} (${BODY_HR[cigar.body]}) gradi koherentan par — spajaju ih ${hrTags}.`,
      en: `${w} (${BODY_EN[cigar.body]}) forms a coherent pair — they meet on ${enTags}.`,
    };
  }

  return {
    hr: `${w}, ${STRENGTH_HR[cigar.strength]} snaga i ${drink.category} (${drink.style}, ${drink.region}) — ${score}% podudaranja.`,
    en: `${w}, ${STRENGTH_EN[cigar.strength]} strength and ${drink.category} (${drink.style}, ${drink.region}) — ${score}% match.`,
  };
}

export interface CuratedOpinion {
  tone: "praise" | "warning";
  text: LocalizedText;
}

function warningBody(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
): { hr: string; en: string } {
  const specific = wrapperWarning(drinkProfile(drink), wrapperKind(cigar.wrapper), cigar);
  if (specific) return specific;
  // najteza kazna iz enginea vec nosi objasnjenje (body-mismatch, overwhelm...)
  const worst = reasons.filter((r) => r.score < 0).sort((a, b) => a.score - b.score)[0];
  if (worst) {
    return {
      hr: `${worst.text.hr.replace(/\.$/, "")} — radije potraži drugi par.`,
      en: `${worst.text.en.replace(/\.$/, "")} — better to look for a different pairing.`,
    };
  }
  return {
    hr: `profili se razilaze (${BODY_HR[cigar.body]} dim uz ${BODY_HR[drink.body]} piće) — ovu kombinaciju ne preporučujemo.`,
    en: `the profiles diverge (${BODY_EN[cigar.body]} smoke with a ${BODY_EN[drink.body]} drink) — we would not recommend this combination.`,
  };
}

/**
 * Kurirana poruka za par.
 * - score >= 80 → pozitivna preporuka (tone: praise), jedinstvena za par
 * - score <= 45 → negativno mišljenje (tone: warning) s konkretnim razlogom
 * - između → null
 * Score je obavezan — bez scorea nema poruke.
 */
export function curatedPairingOpinion(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): CuratedOpinion | null {
  const cigarName = `${cigar.brand} ${cigar.line}`.trim();
  const dn = drinkNameLoc(drink);

  if (score >= WEIGHTS.curatedHintMinScore) {
    const body = alwaysUniqueBody(cigar, drink, reasons, score);
    return {
      tone: "praise",
      text: {
        hr: `${cigarName} i ${dn.hr} — ${body.hr}`,
        en: `${cigarName} and ${dn.en} — ${body.en}`,
      },
    };
  }

  if (score <= WEIGHTS.curatedWarnMaxScore) {
    const body = warningBody(cigar, drink, reasons);
    return {
      tone: "warning",
      text: {
        hr: `${cigarName} i ${dn.hr} — ${body.hr}`,
        en: `${cigarName} and ${dn.en} — ${body.en}`,
      },
    };
  }

  return null;
}
