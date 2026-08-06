// Pripada li linijski EU/USA link BAŠ ovoj vitoli?
//
// `regionLinks` na razini linije nose JEDAN scrapani proizvod (npr. CigarWorld
// "AJ Fernandez Bellas Artes Maduro Gordo"). Dosad se taj link prikazivao za
// svaku vitolu te linije, pa su Robusto, Lancero i Toro svi otvarali istu —
// krivu — vitolu, a uz to nasljeđivali i njenu cijenu.
//
// Pravilo je isto kao drugdje u appu: bolje pretraga po nazivu nego krivi
// proizvod. Linijski link se odbacuje samo kad ga slug OPOVRGNE: ime vitole
// nije cijelo u slugu, a slug uz to imenuje nešto svoje (drugi oblik, drugi
// pokrov). Slug koji nosi samo marku i liniju (`aging-room-quattro-espressivo`)
// ništa ne tvrdi o veličini pa prolazi — nedostatak podatka nije dokaz greške.
const strip = (s: string) =>
  s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();

const tokenize = (s: string): string[] =>
  strip(s)
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 3 && !/^\d+$/.test(t));

// Riječi koje u slugu ne kažu ništa o vitoli (putanja, pakiranje, ekstenzija).
const GENERIC = new Set([
  "cigar",
  "cigars",
  "zigarre",
  "zigarren",
  "proizvod",
  "product",
  "html",
  "htm",
  "php",
  "box",
  "boxes",
  "pack",
  "packs",
  "stick",
  "sticks",
  "single",
  "singles",
  "shop",
  "buy",
]);

/**
 * Mjera u slugu ("46x5", "5x50", "127mm") govori o veličini, a ne o imenu druge
 * vitole — inače bi `asylum-867-auntie-46x5` ispalo "neka treća cigara".
 * Brojevi koji JESU ime vitole (Nub 460) nisu ovog oblika, pa ostaju značajni.
 */
const isDimensionToken = (t: string): boolean =>
  /^\d+(?:[.,]\d+)?x\d+(?:[.,]\d+)?$/.test(t) || /^\d+(?:mm|cm|ring|rg)$/.test(t);

/** Zadnji segment putanje = slug proizvoda (bez /cigars/, /zigarren/<zemlja>/…). */
const slugOf = (url: string): string => {
  let path = url;
  try {
    path = new URL(url).pathname;
  } catch {
    path = url.split("?")[0].split("#")[0];
  }
  const parts = decodeURIComponent(path).split("/").filter(Boolean);
  return parts.length ? parts[parts.length - 1] : "";
};

/** Riječ u slugu koja imenuje nešto svoje — ni linija, ni mjera, ni putanja. */
const isDiscriminating = (t: string, known: string[]): boolean =>
  !GENERIC.has(t) && !isDimensionToken(t) && !tokenPresent(t, known);

/**
 * Isti oblik pod drugim imenom: trgovine miješaju španjolski i njemački red
 * riječi ("Gran Toro" = "toro-grande"). Prefiksno uspoređivanje bi ovo riješilo,
 * ali bi zajedno s tim izjednačilo i Corona s Coronado — zato popis, ne pravilo.
 */
const SYNONYMS: string[][] = [
  ["gran", "grande", "grand"],
  ["petit", "petite", "petits"],
  ["doble", "double"],
  ["corto", "corta", "short"],
];

const synonymsOf = (t: string): string[] =>
  SYNONYMS.find((group) => group.includes(t)) ?? [t];

/** "robusto" ≈ "robustos" ≈ "gran/grande", ali "toro" ≠ "torpedo". */
const tokenPresent = (token: string, pool: string[]): boolean =>
  synonymsOf(token).some((t) =>
    pool.some((u) => u === t || u === t + "s" || t === u + "s"),
  );

const joined = (s: string): string => strip(s).replace(/[^a-z0-9]+/g, "");

/**
 * Ime vitole zalijepljeno u slug bez razdjelnika ("…kreuz-halfcorona-90015540").
 * Iza pogotka ne smije stajati slovo — inače bi "Corona" pristajala i na
 * "coronado", što je druga cigara.
 */
const joinedContains = (slug: string, vitolaName: string): boolean => {
  const needle = joined(vitolaName);
  if (needle.length < 4) return false;
  const hay = joined(slug);
  for (let i = hay.indexOf(needle); i >= 0; i = hay.indexOf(needle, i + 1)) {
    const after = hay[i + needle.length];
    if (after === undefined || !/[a-z]/.test(after)) return true;
  }
  return false;
};

/** Slug doslovno sadrži svaku riječ iz imena vitole. */
function strictFit(url: string, vitolaName: string): boolean {
  const wanted = tokenize(vitolaName);
  if (wanted.length === 0) return false;
  const slug = slugOf(url);
  if (joinedContains(slug, vitolaName)) return true;
  const slugTokens = tokenize(slug);
  return wanted.every((t) => tokenPresent(t, slugTokens));
}

/** Koliko riječi u slugu ne dolazi ni iz linije ni iz imena vitole. */
function extraCount(url: string, vitolaName: string, lineContext: string): number {
  const known = [...tokenize(lineContext), ...tokenize(vitolaName)];
  return tokenize(slugOf(url)).filter((t) => isDiscriminating(t, known)).length;
}

/**
 * Iz popisa product URL-ova linije (npr. `sourceUrls` — Neptune ima po jedan
 * po vitoli) izaberi onaj koji pripada BAŠ ovoj vitoli.
 *
 * Bez ovoga se uzimao prvi URL tog hosta, pa je Maduro Robusto otvarao
 * "bellas-artes-robusto" (drugi pokrov) ili "short-churchill" (drugi format).
 * Kad nijedan slug ne imenuje vitolu, a kandidata je više, vraća se `null` —
 * pretraga po nazivu je bolja od pogađanja.
 */
export function bestVitolaUrl(
  urls: readonly string[],
  vitolaName: string,
  lineContext = "",
): string | null {
  const strict = urls.filter((u) => strictFit(u, vitolaName));
  if (strict.length > 0) {
    return strict.reduce((best, u) =>
      extraCount(u, vitolaName, lineContext) < extraCount(best, vitolaName, lineContext)
        ? u
        : best,
    );
  }
  const loose = urls.filter((u) => urlFitsVitola(u, vitolaName, lineContext));
  return loose.length === 1 ? loose[0] : null;
}

/**
 * Smije li se linijski link pripisati ovoj vitoli.
 *
 * @param lineContext "marka linija" — riječi koje slug nosi zbog same linije,
 *   pa ne dokazuju da je riječ o drugoj vitoli.
 */
export function urlFitsVitola(
  url: string | null | undefined,
  vitolaName: string,
  lineContext = "",
): boolean {
  if (!url) return false;
  const wanted = tokenize(vitolaName);
  if (wanted.length === 0) return true; // "No. 2" — nema čime opovrgnuti
  const slug = slugOf(url);
  const slugTokens = tokenize(slug);
  if (slugTokens.length === 0) return true;
  if (joinedContains(slug, vitolaName)) return true;

  const missing = wanted.filter((t) => !tokenPresent(t, slugTokens));
  if (missing.length === 0) return true;

  // Slug ne spominje ovu vitolu — je li uopće spomenuo neku drugu?
  const known = [...tokenize(lineContext), ...wanted];
  return !slugTokens.some((t) => isDiscriminating(t, known));
}
