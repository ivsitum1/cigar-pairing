// Prikazno ime pića po jeziku. Većina imena su vlastiti nazivi (GlenDronach,
// Don Julio…) i jednaka su u oba jezika; opisna imena kave ("Turska kava",
// "ledena", "tamna mješavina") nose `nameLoc` s prijevodom.

import type { Drink, LocalizedText } from "../types";

/** LocalizedText prikaznog imena — `nameLoc` ako postoji, inače sirovo `name`. */
export function drinkNameLoc(d: Drink): LocalizedText {
  return d.nameLoc ?? { hr: d.name, en: d.name };
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
  return d.nameLoc ? `${d.name} ${d.nameLoc.hr} ${d.nameLoc.en}` : d.name;
}
