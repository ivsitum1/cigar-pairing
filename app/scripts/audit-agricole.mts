/**
 * Sto mehanizam nudi uz agricole rum — i drzi li se pravila koje je za agricole
 * upisano rucno (travnat, lagan rum trazi laganu do srednju cigaru; puna bi
 * pregazila vegetalne note).
 *
 * Ispisuje deset najboljih cigara po agricole rumu, njihovu snagu/tijelo i
 * oznake, pa presjek: koliko je u vrhu punih cigara (tijelo >= 4) i koliko
 * njih nosi travnatu/vegetalnu oznaku.
 *
 * Run: npx vite-node scripts/audit-agricole.mts
 */
import { ALL_DRINKS, CIGARS } from "../src/data/index";
import { pairCigarsForDrink } from "../src/engine/pairing";

const GRASSY = new Set(["trava-slatka", "travnato", "vegetalno", "biljno", "cvjetno"]);

const agricoles = ALL_DRINKS.filter(
  (d) => d.category === "rum" && d.style === "agricole",
);

console.log(`agricole rumova u katalogu: ${agricoles.length}\n`);

let fullInTop = 0;
let grassyInTop = 0;
let total = 0;

for (const rum of agricoles) {
  const top = pairCigarsForDrink(rum, CIGARS).slice(0, 10);
  console.log(`=== ${rum.name}  (tijelo ${rum.body})`);
  for (const hit of top) {
    const c = hit.item;
    const grassy = (c.flavorTags ?? []).some((t) => GRASSY.has(t));
    total += 1;
    if (c.body >= 4) fullInTop += 1;
    if (grassy) grassyInTop += 1;
    console.log(
      `  ${String(hit.score).padStart(3)}  ${c.brand} ${c.line} ${c.vitola}`.padEnd(64) +
        `S${c.strength} B${c.body}  ${grassy ? "travnato" : "—"}  ${(c.flavorTags ?? []).join(", ")}`,
    );
  }
  console.log();
}

console.log(`u vrhovima ukupno: ${total}`);
console.log(`  punih (tijelo >= 4): ${fullInTop}`);
console.log(`  s travnatom/vegetalnom oznakom: ${grassyInTop}`);
