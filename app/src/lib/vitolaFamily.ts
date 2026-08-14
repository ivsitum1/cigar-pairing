// Vrsta vitole — obitelj formata iza konkretnog imena.
//
// Katalog zna deset imena za istu stvar (Robusto, Epicure No. 2, Rothschild),
// a na listi želja te zanima „hoću nešto kratko i debelo”. Ovdje se ime svodi
// na obitelj koja se može ponuditi kao filter.
import type { Lang, LocalizedText } from "../types";

export type VitolaFamily =
  | "figurado"
  | "lancero"
  | "petit"
  | "double-corona"
  | "churchill"
  | "robusto"
  | "toro"
  | "gordo"
  | "corona"
  | "other";

/**
 * Redoslijed je pravilo, ne ukras: oblik pobjeđuje veličinu (Torpedo je
 * figurado i kad se zove „Torpedo Grande”), a uže ime pobjeđuje šire
 * („Short Robusto” je petit, „Double Corona” nije corona).
 */
const RULES: { family: VitolaFamily; match: RegExp }[] = [
  {
    family: "figurado",
    match: /culebra|diadema|salomon|salomón|perfecto|belicoso|torpedo|pir[aá]mide|pyramid|figurado|campana/i,
  },
  { family: "lancero", match: /lancero|pan[ae]tela|laguito|slim\b/i },
  {
    family: "petit",
    match: /petit|minuto|half\s+corona|short\b|demi|chiquito|\bmini\b|rothschild|perla|cadete|entreacto|purito/i,
  },
  { family: "double-corona", match: /double\s+corona|prominente/i },
  { family: "churchill", match: /churchill|julieta/i },
  { family: "robusto", match: /robusto|epicure/i },
  { family: "toro", match: /\btoro\b|ca[ñn]onazo|sublime/i },
  { family: "gordo", match: /gordo|magnum|gigante|grande\b|\b6\d\s*rg\b/i },
  { family: "corona", match: /corona|mareva/i },
];

export function vitolaFamily(name: string | null | undefined): VitolaFamily {
  const n = (name ?? "").trim();
  if (!n) return "other";
  for (const rule of RULES) {
    if (rule.match.test(n)) return rule.family;
  }
  return "other";
}

export const VITOLA_FAMILY_LABELS: Record<VitolaFamily, LocalizedText> = {
  figurado: { hr: "Figurado", en: "Figurado" },
  lancero: { hr: "Lancero / panetela", en: "Lancero / panetela" },
  petit: { hr: "Petit / kratke", en: "Petit / short" },
  "double-corona": { hr: "Double Corona", en: "Double Corona" },
  churchill: { hr: "Churchill", en: "Churchill" },
  robusto: { hr: "Robusto", en: "Robusto" },
  toro: { hr: "Toro", en: "Toro" },
  gordo: { hr: "Gordo", en: "Gordo" },
  corona: { hr: "Corona", en: "Corona" },
  other: { hr: "Ostali formati", en: "Other formats" },
};

export function vitolaFamilyLabel(family: VitolaFamily, lang: Lang): string {
  const label = VITOLA_FAMILY_LABELS[family];
  return lang === "en" ? label.en : label.hr;
}

/** Redoslijed prikaza filtera — od najkraćeg prema najdužem, „ostalo” zadnje. */
export const VITOLA_FAMILY_ORDER: VitolaFamily[] = [
  "petit",
  "robusto",
  "corona",
  "toro",
  "gordo",
  "churchill",
  "double-corona",
  "lancero",
  "figurado",
  "other",
];
