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

// Katalozi trgovina nose istu bocu i kao poklon-pakiranje ("… u poklon kutiji",
// "3x0,05l", "with Shaker"). Kao ARTIKL su ravnopravni, ali kao PREPORUKA su
// šum — "Monkey 47 Kiosk Set 41% Vol. 3x0,05l u poklon kutiji" je bilo prvo
// predloženo pice uz gotovo svaku cigaru samo zato što je abecedno ispalo prvo
// među izjednačenima.
const PACKAGING =
  /u poklon kutij|gift ?box|in giftbox|kiosk set|ritual set|\bwith (?:shaker|glass)\b|sa[  ][cčć]a[sš]om|\d\s*x\s*0[.,]\d/i;

/** 0 = obična boca, 1 = poklon/višebočno pakiranje. Samo za razrješenje neriješenog. */
export function drinkPackagingRank(d: Drink): number {
  return PACKAGING.test(d.name) ? 1 : 0;
}
