import type { Lang } from "../types";

/**
 * Lokalizacija zemljopisnih dijelova naziva listova (wrapper/binder/filler).
 * Trgovinski nazivi (Habano, Connecticut, Maduro…) ostaju netaknuti.
 */

type Pair = { en: string; hr: string };

/** Duži tokeni prvo — "Dominican Republic" prije "Dominican". */
const GEO_PAIRS: Pair[] = [
  { en: "Dominican Republic", hr: "Dominikanska Republika" },
  { en: "Costa Rica", hr: "Kostarika" },
  { en: "Costa Rican", hr: "kostarikanski" },
  { en: "United States", hr: "SAD" },
  { en: "Nicaraguan", hr: "nikaragvanski" },
  { en: "Nicaragua", hr: "Nikaragva" },
  { en: "Ecuadorian", hr: "ekvadorski" },
  { en: "Ecuador", hr: "Ekvador" },
  { en: "Dominican", hr: "dominikanski" },
  { en: "Honduran", hr: "honduraski" },
  { en: "Honduras", hr: "Honduras" },
  { en: "Mexican", hr: "meksički" },
  { en: "Mexico", hr: "Meksiko" },
  { en: "Brazilian", hr: "brazilski" },
  { en: "Brazil", hr: "Brazil" },
  { en: "Cuban", hr: "kubanski" },
  { en: "Cuba", hr: "Kuba" },
  { en: "Indonesian", hr: "indonezijski" },
  { en: "Indonesia", hr: "Indonezija" },
  { en: "Cameroon", hr: "Kamerun" },
  { en: "Panamanian", hr: "panamski" },
  { en: "Panama", hr: "Panama" },
  { en: "Colombian", hr: "kolumbijski" },
  { en: "Colombia", hr: "Kolumbija" },
  { en: "Columbia", hr: "Kolumbija" }, // česta greška u scrapu
  { en: "Peruvian", hr: "peruanski" },
  { en: "Peru", hr: "Peru" },
  { en: "Philippines", hr: "Filipini" },
  { en: "American", hr: "američki" },
  { en: "USA", hr: "SAD" },
  { en: "DR", hr: "DR" }, // skraćenica — ostaje
];

/** Kanonski EN prikaz zemlje iz HR kataloga (za usporedbu s listom). */
export const COUNTRY_EN: Record<string, string> = {
  Kuba: "Cuba",
  Nikaragva: "Nicaragua",
  "Dominikanska Republika": "Dominican Republic",
  Meksiko: "Mexico",
  Ekvador: "Ecuador",
  Brazil: "Brazil",
  Kamerun: "Cameroon",
  Indonezija: "Indonesia",
  Filipini: "Philippines",
  Kostarika: "Costa Rica",
  Panama: "Panama",
  Peru: "Peru",
  Kolumbija: "Colombia",
  Honduras: "Honduras",
  SAD: "USA",
};

function escapeRe(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function replaceGeo(raw: string, lang: Lang): string {
  let out = raw;
  for (const { en, hr } of GEO_PAIRS) {
    if (en === hr) continue;
    const from = lang === "hr" ? en : hr;
    const to = lang === "hr" ? hr : en;
    // riječna granica; zadrži kapitalizaciju ako je izvor bio Title Case za pridevnike
    const re = new RegExp(`(?<![\\p{L}\\p{N}])${escapeRe(from)}(?![\\p{L}\\p{N}])`, "giu");
    out = out.replace(re, (match) => {
      if (lang === "hr" && /^[a-z]/.test(to) && /^[A-Z]/.test(match)) {
        // "Mexican" → "Meksički" na početku fraze; inače pridevnik malim
        if (match === match.toUpperCase()) return to.toUpperCase();
        // unutar fraze ("Mexican San Andres") → malim kako u testu
        return to;
      }
      if (lang === "en" && /^[a-z]/.test(from) && /^[A-ZÀ-Ž]/.test(match[0] ?? "")) {
        return to.charAt(0).toUpperCase() + to.slice(1);
      }
      return to;
    });
  }
  return out;
}

/** Prikazni naziv lista u aktivnom jeziku. */
export function leafLabel(raw: string | undefined | null, lang: Lang): string {
  if (!raw) return "";
  return replaceGeo(raw.trim(), lang);
}

/**
 * Zemlja kataloga (HR kanon) u aktivnom jeziku — usklađeno s `cn()`.
 */
export function countryLabel(country: string, lang: Lang): string {
  if (lang === "en") return COUNTRY_EN[country] ?? country;
  return country;
}

/**
 * Dijelovi meta linije (list · zemlja) bez ponavljanja kad je list
 * samo sinonim zemlje (npr. wrapper "Nicaragua" + country "Nikaragva").
 * Preferira zemlju; ako list nije isto što zemlja, vraća [list, zemlja].
 */
export function leafMetaParts(
  wrapper: string | undefined | null,
  country: string,
  lang: Lang,
): string[] {
  const leaf = leafLabel(wrapper, lang);
  const land = countryLabel(country, lang);
  if (!leaf) return land ? [land] : [];
  if (!land) return [leaf];
  const norm = (s: string) => s.trim().toLowerCase();
  if (norm(leaf) === norm(land)) return [land];
  return [leaf, land];
}

/**
 * Redak "podrijetlo · naziv lista" bez ponavljanja kad su isto
 * (npr. origin Nikaragva + filler "Nicaragua").
 */
export function leafOriginDisplay(
  origin: string | undefined | null,
  leafName: string | undefined | null,
  lang: Lang,
): string {
  const o = origin ? countryLabel(origin, lang) : "";
  const l = leafLabel(leafName, lang);
  if (!o) return l;
  if (!l) return o;
  if (o.trim().toLowerCase() === l.trim().toLowerCase()) return o;
  return `${o} · ${l}`;
}
