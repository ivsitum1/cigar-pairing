// Prikazno ime pića po jeziku. Većina imena su vlastiti nazivi (GlenDronach,
// Don Julio…) i jednaka su u oba jezika; opisna imena kave ("Turska kava",
// "ledena", "tamna mješavina") nose `nameLoc` s prijevodom.
// Scrape-repovi (% Vol, volumen, poklon kutija) čiste se u drinkDisplayNames.json
// — sirovi `name` ostaje za buy-link i pretragu.

import drinkDisplayNamesJson from "../data/drinkDisplayNames.json";
import type { Drink, LocalizedText } from "../types";

const DISPLAY_NAMES: Record<string, string> =
  (drinkDisplayNamesJson as { names?: Record<string, string> }).names ?? {};

/** LocalizedText prikaznog imena — nameLoc > display map > sirovo name. */
export function drinkNameLoc(d: Drink): LocalizedText {
  if (d.nameLoc) return d.nameLoc;
  const cleaned = DISPLAY_NAMES[d.id];
  if (cleaned) return { hr: cleaned, en: cleaned };
  return { hr: d.name, en: d.name };
}

/**
 * Naziv boce bez imena marke — u tablici marke prefiks je šum na svakom retku
 * („GlenDronach 12" → „12"). Kad je ime jednako marki (jednobočne kuće) ili
 * ne počinje njome, ostaje cijelo: bolje ponoviti marku nego prikazati prazno.
 */
export function bottleLabel(name: string, brand: string): string {
  if (!name.startsWith(brand) || name === brand) return name;
  const rest = name.slice(brand.length).trim();
  return rest || name;
}

/** Sve varijante imena (za pretragu neosjetljivu na jezik). */
export function drinkNameHaystack(d: Drink): string {
  const loc = drinkNameLoc(d);
  const parts = [d.name, loc.hr, loc.en];
  const mapped = DISPLAY_NAMES[d.id];
  if (mapped) parts.push(mapped);
  return [...new Set(parts)].join(" ");
}
