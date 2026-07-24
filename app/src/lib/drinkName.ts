// Prikazno ime pića po jeziku. Većina imena su vlastiti nazivi (GlenDronach,
// Don Julio…) i jednaka su u oba jezika; opisna imena kave ("Turska kava",
// "ledena", "tamna mješavina") nose `nameLoc` s prijevodom.

import type { Drink, LocalizedText } from "../types";

/** LocalizedText prikaznog imena — `nameLoc` ako postoji, inače sirovo `name`. */
export function drinkNameLoc(d: Drink): LocalizedText {
  return d.nameLoc ?? { hr: d.name, en: d.name };
}

/** Sve varijante imena (za pretragu neosjetljivu na jezik). */
export function drinkNameHaystack(d: Drink): string {
  return d.nameLoc ? `${d.name} ${d.nameLoc.hr} ${d.nameLoc.en}` : d.name;
}
