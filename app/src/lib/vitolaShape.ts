// Klasifikacija vitole u obitelj oblika za filter Kataloga.
// Signali po prioritetu: shape polje (ako postoji) → naziv (regex obitelji) →
// geometrija (ring/duljina) kao fallback. `shape` je prerijedak da bi bio jedini
// izvor; ring/lengthMM su ~potpuni, a naziv je najbogatiji signal.
import type { Cigar, Vitola } from "../types";
import { uniqueVitolas } from "./cigarVitola";
import { GEOMETRY } from "../engine/vitolaGeometry";

export type ShapeFamily =
  | "robusto"
  | "toro"
  | "churchill"
  | "corona"
  | "gordo"
  | "lancero"
  | "figurado";

// Redoslijed = redoslijed prikaza chipova.
export const SHAPE_FAMILIES: ShapeFamily[] = [
  "robusto",
  "toro",
  "corona",
  "churchill",
  "gordo",
  "lancero",
  "figurado",
];

// Regex obitelji — specifično prije općenitog. Šiljasti (figurado) i tanki
// (lancero) idu prvi jer bi ih inače pojeo generički "corona"/"toro".
const NAME_RULES: { family: ShapeFamily; match: RegExp }[] = [
  {
    family: "figurado",
    match:
      /figurado|torpedo|belicoso|pir[aá]mide|piramide|pyramid|perfecto|diadema|salomon|culebra/i,
  },
  { family: "lancero", match: /lancero|pan[ae]tela|laguito/i },
  {
    family: "churchill",
    match: /churchill|julieta|double corona|doble corona|prominente|presidente|lonsdale|larga corona/i,
  },
  { family: "gordo", match: /gordo|gigante|magnum 60|grande extra|\bgrande\b/i },
  { family: "toro", match: /\btoro\b|ca[nñ]onazo/i },
  {
    family: "corona",
    match:
      /corona gorda|gran corona|grand corona|half corona|petit corona|short corona|\bcorona\b|mareva|minuto|\bperla\b|cadete/i,
  },
  {
    family: "robusto",
    match: /robusto|rothschild|epicure no\.?\s?2/i,
  },
];

function familyFromText(text: string | null | undefined): ShapeFamily | null {
  if (!text) return null;
  for (const r of NAME_RULES) {
    if (r.match.test(text)) return r.family;
  }
  return null;
}

// Fallback iz geometrije kad naziv/shape ne kažu ništa. Pragovi dijele
// kalibraciju s vitolaGeometry.ts (tanko/debelo/dugo).
function familyFromGeometry(ring: number | null, len: number | null): ShapeFamily | null {
  if (ring == null) return null;
  if (ring >= GEOMETRY.thickRingMin + 2) return "gordo"; // ≥56
  if (ring <= GEOMETRY.thinRingMax - 2) return "lancero"; // ≤40
  if (ring <= 45) return "corona";
  if (ring >= GEOMETRY.thickRingMin) return "toro"; // 54–55
  // 46–53: duljina razdvaja robusto (kratko) od toro (dugo)
  if (len != null && len >= GEOMETRY.longLenMin) return "toro";
  return "robusto";
}

export function classifyVitola(v: Vitola): ShapeFamily | null {
  return (
    familyFromText(v.shape) ??
    familyFromText(v.name) ??
    familyFromGeometry(v.ring ?? null, v.lengthMM ?? null)
  );
}

/** Sve obitelji oblika koje linija sadrži (po jedinstvenim vitolama). */
export function cigarShapes(cigar: Cigar): Set<ShapeFamily> {
  const out = new Set<ShapeFamily>();
  for (const v of uniqueVitolas(cigar)) {
    const f = classifyVitola(v);
    if (f) out.add(f);
  }
  return out;
}

/** Prva vitola linije koja pripada traženoj obitelji (za pred-odabir). */
export function firstVitolaOfShape(cigar: Cigar, family: ShapeFamily): Vitola | undefined {
  return uniqueVitolas(cigar).find((v) => classifyVitola(v) === family);
}
