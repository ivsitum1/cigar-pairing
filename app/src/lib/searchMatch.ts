// Pretraga po riječima, ne po nizu znakova.
//
// Dosad je upit morao doslovno stajati u nazivu: „Flor de Selva Classic
// Collection Tempo" nije nalazio ništa jer katalog tu cigaru vodi kao
// „Flor de Selva Tempo" — riječi su sve tu, ali ne u tom nizu i s jednom
// viška. Tako se traži ono što piše na kutiji, a ne ono što piše u bazi.
//
// Pravilo: svaka riječ upita mora se pojaviti negdje u opisu stavke, bilo kojim
// redom. Riječi s pakiranja („collection", „edition") ne nose razliku pa se
// ispuštaju — ispuštanje riječi može popis samo proširiti, nikad sakriti
// pogodak.

const strip = (s: string) =>
  s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();

/**
 * Riječi s kutije koje ne razlikuju proizvod. Namjerno kratak popis: „serie",
 * „reserva" i slično JESU dio imena linije i ostaju.
 */
const FILLER = new Set([
  "collection",
  "kolekcija",
  "cigar",
  "cigars",
  "cigara",
  "cigare",
  "the",
]);

/** Upit → značajne riječi. Prazno kad upit nema nijednu. */
export function searchTokens(query: string): string[] {
  return strip(query)
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length > 0 && !FILLER.has(t));
}

/**
 * Kratka riječ mora stajati kao riječ, duga smije biti početak riječi.
 *
 * Bez toga „Oliva Serie O Toro" pogađa i Serie V: slovo „o" kao niz znakova
 * stoji u pola kataloga („Toro", „Robusto"). Duge riječi ostaju popustljive da
 * nedovršen upit („aganor") i dalje nešto nađe.
 */
function hasToken(hay: string, token: string): boolean {
  if (token.length > 2) return hay.includes(token);
  return new RegExp(`(^|[^a-z0-9])${token}([^a-z0-9]|$)`).test(hay);
}

/**
 * Pogađa li opis stavke sve riječi upita?
 *
 * `haystack` je već sastavljen opis (marka, linija, vitola, pokrov, zemlja…).
 * Prazan upit pogađa sve — filtriranje tada nije ni traženo.
 */
export function matchesSearch(haystack: string, query: string): boolean {
  const tokens = searchTokens(query);
  if (tokens.length === 0) return true;
  const hay = strip(haystack);
  return tokens.every((t) => hasToken(hay, t));
}

/** Ista provjera nad više izvora — pogodak u bilo kojem je pogodak. */
export function matchesAnySearch(haystacks: string[], query: string): boolean {
  const tokens = searchTokens(query);
  if (tokens.length === 0) return true;
  const hays = haystacks.map(strip);
  return tokens.every((t) => hays.some((h) => hasToken(h, t)));
}

/**
 * Kazalo marki: dovoljno je da se JEDNA riječ upita poklopi s markom.
 *
 * Kad upišeš puno ime s kutije („Oliva Serie O Toro"), marka se zove samo
 * „Oliva" — traženje svih riječi ondje daje prazno kazalo, iako je marka
 * očito pogođena.
 */
export function matchesAnyToken(haystack: string, query: string): boolean {
  const tokens = searchTokens(query);
  if (tokens.length === 0) return true;
  const hay = strip(haystack);
  return tokens.some((t) => hasToken(hay, t));
}
