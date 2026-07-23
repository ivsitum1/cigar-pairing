// Serve style — kako se piće servira mijenja spoj s cigarom.
//
// Model (potvrđeno izvorima, vidi docs/.../serve-style-format-share-card.md §0.5):
//  - kap vode OTVARA aromu (amfipatski spojevi tipa gvajakol migriraju na
//    površinu i lakše isparavaju) i UMIRUJE žestinu etanola — tijelo ostaje
//    slično (NE spušta se bitno);
//  - led ZATVARA aromu (hlađenje snižava tlak para hlapljivih spojeva) i
//    prigušuje slatkoću; blaga dilucija tijela;
//  - highball/cola razrjeđuju tijelo; cola naglo diže slatkoću.
//
// Zato serve ne mijenja samo body/sweetness, nego nosi i dva množitelja:
//  aromaFactor (množi aroma-sinergiju: rules 2 + 2b) i
//  tameFactor  (množi kazne žestine: rules 1b + 5 negativna grana).

import type { Drink, PairingReason, ServeStyle } from "../types";

export interface ServeEffect {
  bodyDelta: number; // pomak EFEKTIVNOG tijela (dilucija) — voda ≈ 0
  sweetnessDelta: number; // pomak EFEKTIVNE slatkoće — cola +, led −
  aromaFactor: number; // množi aroma-sinergiju: >1 otvara, <1 zatvara
  tameFactor: number; // množi kazne žestine: <1 umiruje alkohol
}

// Kalibracija namjerno konzervativna — serve nikad presudan. Jedno mjesto za ugađanje.
export const SERVE_EFFECT: Record<ServeStyle, ServeEffect> = {
  neat: { bodyDelta: 0.0, sweetnessDelta: 0.0, aromaFactor: 1.0, tameFactor: 1.0 },
  // kap (mlake) vode: OTVARA aromu, UMIRUJE žestinu; tijelo ~netaknuto
  water: { bodyDelta: 0.0, sweetnessDelta: 0.0, aromaFactor: 1.15, tameFactor: 0.65 },
  // led: hladno ZATVARA aromu i prigušuje slatkoću; blaga dilucija tijela
  rocks: { bodyDelta: -0.2, sweetnessDelta: -0.3, aromaFactor: 0.8, tameFactor: 0.85 },
  // highball: jaka dilucija tijela + svježina; aroma blago prigušena
  highball: { bodyDelta: -1.3, sweetnessDelta: 0.3, aromaFactor: 0.95, tameFactor: 0.5 },
  // cola: šećer naglo diže slatkoću (mijenja contrast-sweet-maduro), razrjeđuje tijelo
  cola: { bodyDelta: -0.8, sweetnessDelta: 1.3, aromaFactor: 0.9, tameFactor: 0.6 },
};

const clamp15 = (v: number) => Math.max(1, Math.min(5, v));

const SERVE_REASON: Record<Exclude<ServeStyle, "neat">, PairingReason> = {
  water: {
    rule: "serve-water",
    score: 0,
    text: {
      hr: "Kap vode otvara aromu i umiruje žestinu — spoj podnosi i blažu cigaru (tijelo ostaje slično).",
      en: "A drop of water opens the aroma and tames the heat — it tolerates a milder cigar (body stays similar).",
    },
  },
  rocks: {
    rule: "serve-rocks",
    score: 0,
    text: {
      hr: "Led zatvara aromu i prigušuje slatkoću — manje aromatskog preklapanja s cigarom.",
      en: "Ice closes the aroma and dampens sweetness — less aromatic overlap with the cigar.",
    },
  },
  highball: {
    rule: "serve-highball",
    score: 0,
    text: {
      hr: "Highball razrjeđuje tijelo i dodaje svježinu — traži lakšu cigaru.",
      en: "A highball dilutes the body and adds lift — it calls for a lighter cigar.",
    },
  },
  cola: {
    rule: "serve-cola",
    score: 0,
    text: {
      hr: "Cola naglo diže slatkoću — pojačava kontrast prema tamnijoj, punijoj cigari.",
      en: "Cola spikes the sweetness — it strengthens the contrast toward a darker, fuller cigar.",
    },
  },
};

/**
 * Vrati EFEKTIVNO piće (body/sweetness dotjerani), množitelje efekta i
 * objašnjenje serve stila. Za `neat`/undefined vraća original i neutralne
 * množitelje bez objašnjenja.
 */
export function applyServe(
  drink: Drink,
  serve: ServeStyle | undefined,
): { drink: Drink; effect: ServeEffect; reason?: PairingReason } {
  const effect = SERVE_EFFECT[serve ?? "neat"];
  if (!serve || serve === "neat") return { drink, effect };
  const adjusted: Drink = {
    ...drink,
    body: clamp15(drink.body + effect.bodyDelta),
    sweetness: clamp15(drink.sweetness + effect.sweetnessDelta),
  };
  return { drink: adjusted, effect, reason: SERVE_REASON[serve] };
}
