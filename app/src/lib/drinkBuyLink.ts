// Pouzdan "Gdje kupiti" link za pice: odbaci kategorije i ocito krive proizvode.
import type { Drink, DrinkCategory } from "../types";

const STOP = new Set([
  "vol",
  "years",
  "year",
  "old",
  "yo",
  "single",
  "malt",
  "scotch",
  "whisky",
  "whiskey",
  "rum",
  "rhum",
  "ron",
  "cognac",
  "armagnac",
  "calvados",
  "brandy",
  "gin",
  "tequila",
  "port",
  "porto",
  "sherry",
  "wine",
  "the",
  "and",
  "gift",
  "box",
  "giftbox",
  "poklon",
  "kutiji",
  "kutija",
  "dry",
  "extra",
  "reserve",
  "grande",
  "champagne",
  // regije — opisuju stil, ne razlikuju proizvod
  "islay",
  "speyside",
  "highland",
  "lowland",
  "campbeltown",
  "limited",
  "limithed",
  "edition",
  "vintage",
  "blended",
  "blend",
  "distilled",
  "finish",
  "original",
  "fine",
  "premium",
  "superior",
  "prestige",
  "solera",
  "gran",
  "reserva",
  "anejo",
  "anos",
  "ans",
  "liker",
  "liqueur",
  // francuski prefiksi imena
  "chateau",
  "domaine",
  "de",
  "du",
  "des",
  "le",
  "la",
  "les",
  "batch",
  "no",
  "in",
  "gb",
  "l",
  "cl",
  "ml",
]);

// Oznake zrelosti rakija/konjaka: ista marka s drugom oznakom je drugi proizvod.
const GRADES = new Set(["vs", "vsop", "xo"]);

// Blazi stop-popis za PROVJERU SLUGA: samo kategorija pica + pakiranje/volumen.
// Puni STOP je preagresivan za slug — pojeo bi i tokene koji razlikuju
// proizvode ("gran reserva", "edicion"...), pa bi krivi SKU prosao kao "sve
// iz sluga je u imenu".
const LIGHT_STOP = new Set([
  "vol",
  "l",
  "cl",
  "ml",
  "gb",
  "gift",
  "box",
  "giftbox",
  "poklon",
  "kutiji",
  "kutija",
  "in",
  "years",
  "year",
  "old",
  "yo",
  "anos",
  "ans",
  "the",
  "and",
  "single",
  "malt",
  "scotch",
  "blended",
  "whisky",
  "whiskey",
  "rum",
  "rhum",
  "ron",
  "cognac",
  "armagnac",
  "calvados",
  "brandy",
  "gin",
  "tequila",
  "wine",
  // regije/nacionalnosti i marketinski sufiksi u slugovima
  "islay",
  "speyside",
  "highland",
  "lowland",
  "japanese",
  "japanski",
  "irish",
  "irski",
  "skotski",
  "limited",
  "limithed",
  "edition",
]);

/**
 * Svi normalizirani tokeni, redom pojavljivanja (i jednoslovni — trebaju za
 * spojeni potpis, npr. "V.J.O.P." -> "vjop"). Apostrofi se brisu prije rezanja
 * ("Blanton's" -> "blantons", "A'bunadh" -> "abunadh") da se poklope sa
 * slugovima, a granica slovo/broj se reze ("15yo" -> "15 yo", "07l" -> "07 l").
 */
function allTokens(s: string): string[] {
  return s
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/['’]/g, "")
    .replace(/(\d)([a-z])/g, "$1 $2")
    .replace(/([a-z])(\d)/g, "$1 $2")
    .replace(/[^a-z0-9]+/g, " ")
    .split(/\s+/)
    .filter((t) => t.length > 0);
}

function rawTokens(s: string): string[] {
  return allTokens(s).filter((t) => /^\d+$/.test(t) || t.length >= 2);
}

/** Tokeni imena / slug-a (uklj. brojeve godina). */
export function drinkLinkTokens(s: string): Set<string> {
  return new Set(rawTokens(s).filter((t) => !STOP.has(t)));
}

/**
 * Brojevi bez volumena/jakosti: "40-vol" i "40-07l" se preskacu, kao i
 * brojevi s vodecom nulom ("07", "075" — to su litre, ne godine).
 */
function meaningfulNumbers(tokens: string[]): string[] {
  const out: string[] = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i]!;
    if (!/^\d+$/.test(t)) continue;
    if (t.length > 1 && t.startsWith("0")) continue;
    const next = tokens[i + 1];
    if (next === "vol" || next === "l" || next === "cl" || next === "ml") continue;
    if (next && /^0\d/.test(next)) continue; // "40-07l": 40 je jakost
    out.push(t);
  }
  return out;
}

/** "2.0" se reze u ["2","0"] — spoji susjedne znamenke u dodatne kandidate. */
function joinedAdjacentNumbers(tokens: string[]): string[] {
  const out: string[] = [];
  for (let i = 0; i + 1 < tokens.length; i++) {
    if (/^\d+$/.test(tokens[i]!) && /^\d+$/.test(tokens[i + 1]!)) {
      out.push(tokens[i]! + tokens[i + 1]!);
    }
  }
  return out;
}

/** Batch/lot brojevi: broj kojem neposredno prethodi "batch", "no" ili "lot". */
function batchNumbers(tokens: string[]): string[] {
  const out: string[] = [];
  for (let i = 1; i < tokens.length; i++) {
    const t = tokens[i]!;
    if (!/^\d+$/.test(t)) continue;
    const prev = tokens[i - 1];
    if (prev === "batch" || prev === "no" || prev === "lot") {
      out.push(t.replace(/^0+(?=\d)/, ""));
    }
  }
  return out;
}

const isYear = (t: string) => /^\d{4}$/.test(t) && +t >= 1700 && +t <= 2099;
const isSmallNum = (t: string) => /^\d{1,2}$/.test(t);

function slugFromUrl(url: string): string {
  try {
    const path = new URL(url).pathname;
    const parts = path.split("/").filter(Boolean);
    return parts[parts.length - 1] ?? "";
  } catch {
    return "";
  }
}

/** Je li URL stranica proizvoda, a ne katalog/kategorija/pretraga. */
export function isDrinkProductUrl(url: string): boolean {
  let u: URL;
  try {
    u = new URL(url);
  } catch {
    return false;
  }
  const path = u.pathname.toLowerCase();
  const segs = path.split("/").filter(Boolean);
  if (path.includes("/svi-proizvodi/") || path.includes("/proizvod/")) return true;
  // ecuga: /katalog/<kategorija>/<potkategorija>/<proizvod> je proizvod,
  // /katalog/<kategorija>[/<potkategorija>] je listing.
  if (/\/katalog\//.test(path) || path.endsWith("/katalog")) {
    return segs[0] === "katalog" && segs.length >= 4;
  }
  if (/\/vrsta\//.test(path)) return false;
  if (/\/search/.test(path) || /\/shop\/(?:rum|whiskey|whisky|gin|tequila|cognac)\/?$/.test(path)) {
    return false;
  }
  if (/\/webshop\/?$/.test(path)) return false;
  // genericki shop rootovi
  if ((path === "/" || path === "") && !u.search) return false;
  // ostali hostovi: zahtijevaj barem jedan path segment koji nije prazan
  return segs.length >= 1 && segs[segs.length - 1]!.length >= 4;
}

function matchCore(name: string, slug: string): boolean {
  const nameAll = allTokens(name);
  const urlAll = allTokens(slug);
  const nameRaw = nameAll.filter((t) => /^\d+$/.test(t) || t.length >= 2);
  const urlRaw = urlAll.filter((t) => /^\d+$/.test(t) || t.length >= 2);
  const nameToks = new Set(nameRaw.filter((t) => !STOP.has(t)));
  const urlToks = new Set(urlRaw.filter((t) => !STOP.has(t)));
  if (nameToks.size === 0 || urlToks.size === 0) return false;

  // Spojene varijante hvataju "re/define" -> "redefine", "V.J.O.P." -> "vjop".
  const urlJoined = urlAll.join("");
  const nameJoined = nameAll.join("");
  const wordInUrl = (t: string) =>
    urlToks.has(t) || (t.length >= 4 && urlJoined.includes(t));
  const tokenInUrl = (t: string) => (/^\d+$/.test(t) ? urlToks.has(t) : wordInUrl(t));

  // Brojevi se odbijaju na KONFLIKT, ne na izostanak: godiste/starost/batch
  // u slugu mora odgovarati imenu, ali slug bez takvog broja nije dokaz
  // da je proizvod krivi (allez cesto krati slugove).
  const nameNums = meaningfulNumbers(nameRaw);
  const urlNums = meaningfulNumbers(urlRaw);
  const nameYears = nameNums.filter(isYear);
  const urlYears = urlNums.filter(isYear);
  const nameSmall = [...nameNums.filter(isSmallNum), ...joinedAdjacentNumbers(nameRaw)];
  const urlSmall = urlNums.filter(isSmallNum);
  if (
    nameYears.length > 0 &&
    urlYears.length > 0 &&
    !nameYears.some((y) => urlYears.includes(y))
  ) {
    return false;
  }
  if (
    nameSmall.length > 0 &&
    urlSmall.length > 0 &&
    !nameSmall.some((n) => urlSmall.includes(n))
  ) {
    return false;
  }
  // batch/lot: eksplicitan batch se mora poklopiti (batch 4 nije batch 2)
  const nameBatch = batchNumbers(nameRaw);
  const urlBatch = batchNumbers(urlRaw);
  if (
    nameBatch.length > 0 &&
    urlBatch.length > 0 &&
    !nameBatch.some((b) => urlBatch.includes(b))
  ) {
    return false;
  }

  // VS / VSOP / XO: oznaka iz imena mora biti u slugu, inace je to
  // drugi proizvod iste marke.
  const nameGrades = nameRaw.filter((t) => GRADES.has(t));
  const urlGrades = urlRaw.filter((t) => GRADES.has(t));
  if (nameGrades.length > 0 && !nameGrades.some((g) => urlGrades.includes(g))) {
    return false;
  }

  // Skraceni slug (allez/ecuga znaju imati npr. samo "benriach-27-yo" ili
  // "paddy"): ako je SVE smisleno iz sluga sadrzano u imenu, a brojevi se
  // ne kose, to je taj proizvod.
  const slugMeaningful = urlRaw.filter((t) => !LIGHT_STOP.has(t) && !/^\d+$/.test(t));
  const inName = (t: string) =>
    nameToks.has(t) || (t.length >= 4 && nameJoined.includes(t));
  if (slugMeaningful.length >= 1 && slugMeaningful.every(inName)) {
    const firstNameTok = [...nameToks][0];
    if (slugMeaningful.length >= 2 || slugMeaningful[0] === firstNameTok) return true;
  }

  const shared = [...nameToks].filter(tokenInUrl);
  if (shared.length < 2) return false;

  // barem polovica "srednjih" tokena (>=4) mora biti u slug-u
  const mid = [...nameToks].filter((t) => t.length >= 4 && !/^\d+$/.test(t));
  if (mid.length >= 2) {
    const hit = mid.filter(wordInUrl).length;
    if (hit * 2 < mid.length) return false;
  }

  // dugi potpis (>=6): svi moraju biti u slug-u (inače ista marka, krivi SKU)
  const long = [...nameToks].filter((t) => t.length >= 6 && !/^\d+$/.test(t));
  if (long.length >= 1 && !long.every(wordInUrl)) return false;

  return true;
}

/**
 * Da li slug URL-a dovoljno odgovara imenu boce.
 * Namjerno konzervativno: bolje "Traži online" nego krivi proizvod.
 * Imena s "/" (npr. "Doorly's 12 / 14") probaju svaku alternativu.
 */
export function urlMatchesDrinkName(name: string, url: string): boolean {
  if (!isDrinkProductUrl(url)) return false;
  const slug = slugFromUrl(url);
  const base = name.replace(/\([^)]*\)/g, " ");
  const variants = new Set<string>([base]);
  if (base.includes("/")) {
    variants.add(base.replace(/\s*\/.*$/, "")); // sve prije prve "/"
    const m = base.match(/(\S+)\/(\S+)/);
    if (m) {
      // "Plantation/Planteray X" -> "Plantation X"; drugu alternativu namjerno
      // ne probavamo — prekratka je i zna upariti krivi brend.
      variants.add(base.replace(m[0]!, m[1]!));
    }
  }
  return [...variants].some((v) => v.trim().length > 0 && matchCore(v, slug));
}

export type DrinkBuyLink = { href: string; label: "buy" | "search" };

const CATEGORY_HINT: Record<DrinkCategory, string> = {
  whisky: "whisky",
  rum: "rum",
  gin: "gin",
  brandy: "brandy",
  wine: "vino",
  coffee: "kava",
  tequila: "tequila",
};

const KIND_IN_NAME =
  /whisk|rum|gin|tequila|cognac|konjak|armagnac|calvados|brandy|vino|wine|port|sherry|champagne|sampanj|šampanj/i;

/**
 * Google pretraga koja uvijek ima rezultate: BEZ navodnika (fraza pod
 * navodnicima za dugacka imena vrlo cesto vrati nula pogodaka), bez
 * "keyword stuffinga" — samo ocisceno ime + vrsta pica + "cijena".
 */
export function drinkSearchHref(drink: Drink): string {
  const words = drink.name
    .replace(/['’"]/g, "")
    .replace(/[/|]/g, " ")
    .replace(/\([^)]*\)/g, " ")
    .replace(/\d+\s*%/g, " ")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 7);
  const parts = [...words];
  if (!KIND_IN_NAME.test(drink.name)) {
    parts.push(CATEGORY_HINT[drink.category] ?? "");
  }
  parts.push("cijena");
  const q = parts.filter(Boolean).join(" ");
  return `https://www.google.com/search?q=${encodeURIComponent(q)}`;
}

export function drinkBuyLink(drink: Drink): DrinkBuyLink {
  const url = drink.priceUrl ?? null;
  if (!url) return { href: drinkSearchHref(drink), label: "search" };
  if (!urlMatchesDrinkName(drink.name, url)) {
    return { href: drinkSearchHref(drink), label: "search" };
  }
  return { href: url, label: "buy" };
}
