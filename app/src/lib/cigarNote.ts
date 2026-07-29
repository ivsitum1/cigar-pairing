// Opis cigare — samo pravi opis.
//
// Velik dio kataloga nosi `notes` koje je generirao pipeline iz atributa
// (`scripts/build-market-cigars.py` → `market_note`, `describe-lines.py`):
//
//   "Nikaragva, Habano pokrov — jače snage, punijeg tijela. Okusi: cedrovina, začini, koža."
//   "Habano wrapper (Nicaragua); fuller and expressive. Notes of cedar, spice, leather."
//
// To nije opis nego ponavljanje onoga što je već na kartici — zemlja, wrapper,
// mjerači snage i tijela, chipovi okusa. Prikazano kao odlomak izgleda kao da
// je netko nešto rekao o cigari, a nije. Ovdje se takve rečenice odbacuju, a
// zadržava se sve što je stvarno napisano (dio linija ima uredničku rečenicu
// zalijepljenu iza generiranog uvoda).

import type { Cigar, Lang, LocalizedText } from "../types";

const GENERATED_HR: RegExp[] = [
  /^Aromatizirana$/i,
  // "<zemlja>, <wrapper> pokrov — <snaga> snage, <tijelo> tijela"
  /—\s*(?:vrlo lagane|lagane|srednje|jače|pune)\s+snage,\s*(?:vrlo laganog|laganog|srednjeg|punijeg|punog)\s+tijela$/i,
  // "<wrapper> pokrov (<zemlja>); <fraza>"
  /(?:pokrov|wrapper)\s*\([^)]*\);/i,
  /^Okusi:/i,
];

const GENERATED_EN: RegExp[] = [
  /^Flavoured\/infused$/i,
  /—\s*(?:very mild|mild|medium|medium-full|full)\s+in strength,\s*(?:very light|light|medium|fuller|full)-bodied$/i,
  /wrapper\s*\([^)]*\);/i,
  /^Notes(?::| of)/i,
];

const sentences = (text: string): string[] =>
  text
    .split(/(?<=\.)\s+/)
    .map((s) => s.trim())
    .filter(Boolean);

const isGeneratedSentence = (sentence: string, lang: Lang): boolean => {
  const bare = sentence.replace(/\.\s*$/, "").trim();
  return (lang === "hr" ? GENERATED_HR : GENERATED_EN).some((re) =>
    re.test(bare),
  );
};

/**
 * Bilješka bez generiranih rečenica. Prazan string = nema pravog opisa,
 * pa se odlomak uopće ne prikazuje (umjesto lažnog opisa).
 */
export function stripGeneratedNote(text: string, lang: Lang): string {
  return sentences(text)
    .filter((s) => !isGeneratedSentence(s, lang))
    .join(" ")
    .trim();
}

/** Je li cijela bilješka na tom jeziku samo prepričavanje atributa. */
export function isGeneratedNote(text: string, lang: Lang): boolean {
  return text.trim().length > 0 && stripGeneratedNote(text, lang).length === 0;
}

/**
 * Opis za prikaz, ili null kad pravog opisa nema. Ako jezik korisnika nema
 * ništa, a drugi ima uredničku rečenicu, radije se pokaže ona nego ništa.
 */
export function cigarDescription(
  cigar: Pick<Cigar, "notes">,
  lang: Lang,
): string | null {
  const notes: LocalizedText = cigar.notes;
  const primary = stripGeneratedNote(notes[lang] ?? "", lang);
  if (primary) return primary;
  const otherLang: Lang = lang === "hr" ? "en" : "hr";
  const fallback = stripGeneratedNote(notes[otherLang] ?? "", otherLang);
  return fallback || null;
}
