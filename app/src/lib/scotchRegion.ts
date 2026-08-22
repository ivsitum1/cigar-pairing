// Škotska regija se u podacima ne vodi kao zasebno polje — živi kao prefiks
// slobodnog teksta u `region` ("Islay, Škotska", "Orkney, Škotska",
// "Škotska (blend)"). Ovdje se iz tog niza izvodi jedan od šest ključeva, pa
// filter u katalogu ne mora poznavati pravopis svakog otoka.
//
// Pet je službenih regija po Scotch Whisky Regulations 2009 (Speyside,
// Highland, Lowland, Islay, Campbeltown); Otoci su praksa, ne propis — zakonski
// spadaju pod Highland. Vodimo ih odvojeno jer dijele morski ton, a lekcija u
// `whiskyRegions.json` to izrijekom kaže da nauk ne bude kriv.
import type { Drink, LocalizedText } from "../types";
import whiskyRegions from "../data/whiskyRegions.json";

export type ScotchRegion =
  | "speyside"
  | "highland"
  | "islay"
  | "islands"
  | "lowland"
  | "campbeltown";

/** Redoslijed prikaza chipova — po broju boca u katalogu, ne abecedno. */
export const SCOTCH_REGIONS: ScotchRegion[] = [
  "speyside",
  "islay",
  "highland",
  "islands",
  "campbeltown",
  "lowland",
];

/** Zemlja (u podacima hrvatski) čije boce uopće imaju škotske regije. */
export const SCOTLAND = "Škotska";

// Otoci koji se u podacima pojavljuju imenom, bez riječi "Otoci".
const ISLAND_NAMES = ["orkney", "skye", "jura", "arran", "mull", "lewis"];

/**
 * Regija jedne boce, ili null kad je nema: blendovi ("Škotska (blend)") i
 * neodređeno "Škotska" nisu ničija regija i namjerno ispadaju iz filtra —
 * blend po definiciji miješa više regija.
 */
export function scotchRegionOf(drink: Pick<Drink, "region" | "country">): ScotchRegion | null {
  if (drink.country !== SCOTLAND) return null;
  const r = (drink.region ?? "").toLowerCase();
  if (r.startsWith("speyside")) return "speyside";
  if (r.startsWith("islay")) return "islay";
  if (r.startsWith("lowland")) return "lowland";
  if (r.startsWith("campbeltown")) return "campbeltown";
  if (ISLAND_NAMES.some((i) => r.startsWith(i))) return "islands";
  // "Highlands", "Highland, Škotska (liker)", "West Highlands" — sve je Highland
  if (r.includes("highland")) return "highland";
  return null;
}

interface RegionCard {
  id: string;
  label: LocalizedText;
  summary: LocalizedText;
  body: LocalizedText;
}
interface StyleNote {
  id: string;
  note: LocalizedText;
}

const REGION_CARDS = whiskyRegions.regions as RegionCard[];
const STYLE_NOTES = whiskyRegions.styles as StyleNote[];

export function scotchRegionCard(region: ScotchRegion): RegionCard {
  const card = REGION_CARDS.find((c) => c.id === region);
  // svaki ključ ima karticu — čuva scotchRegion.test.ts
  return card!;
}

/** Kratka pouka uz odabranu vrstu whiskyja; null kad je stil bez bilješke. */
export function whiskyStyleNote(style: string): LocalizedText | null {
  return STYLE_NOTES.find((s) => s.id === style)?.note ?? null;
}
