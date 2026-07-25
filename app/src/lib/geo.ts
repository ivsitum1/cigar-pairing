// Zemljopis pica i cigara — koordinate za kartu i uparivanje po zemlji.
// Kljuc je hrvatsko ime zemlje kako se pojavljuje u podacima (region/country).

import type { Cigar, Drink } from "../types";

export interface CountryInfo {
  hr: string;
  en: string;
  /** Unicode emoji — fallback / a11y; Windows often renders as ISO letters. */
  flag: string;
  /** flagcdn / ISO 3166-1 alpha-2 (lowercase); regional: gb-sct, gb-wls, gb-nir */
  iso: string;
  lat: number;
  lon: number;
}

/** PNG URL for a country flag (works on Windows where emoji flags do not). */
export function flagSrc(iso: string, width = 40): string {
  return `https://flagcdn.com/w${width}/${iso}.png`;
}

export const COUNTRIES: CountryInfo[] = [
  { hr: "Kuba", en: "Cuba", flag: "🇨🇺", iso: "cu", lat: 22.0, lon: -79.5 },
  { hr: "Dominikanska Republika", en: "Dominican Republic", flag: "🇩🇴", iso: "do", lat: 18.9, lon: -70.2 },
  { hr: "Jamajka", en: "Jamaica", flag: "🇯🇲", iso: "jm", lat: 18.1, lon: -77.3 },
  { hr: "Barbados", en: "Barbados", flag: "🇧🇧", iso: "bb", lat: 13.2, lon: -59.5 },
  { hr: "Trinidad", en: "Trinidad", flag: "🇹🇹", iso: "tt", lat: 10.5, lon: -61.3 },
  { hr: "Sv. Lucija", en: "St Lucia", flag: "🇱🇨", iso: "lc", lat: 13.9, lon: -61.0 },
  { hr: "Martinique", en: "Martinique", flag: "🇲🇶", iso: "mq", lat: 14.6, lon: -61.0 },
  { hr: "Guadeloupe", en: "Guadeloupe", flag: "🇬🇵", iso: "gp", lat: 16.2, lon: -61.5 },
  { hr: "Puerto Rico", en: "Puerto Rico", flag: "🇵🇷", iso: "pr", lat: 18.2, lon: -66.4 },
  { hr: "Bermuda", en: "Bermuda", flag: "🇧🇲", iso: "bm", lat: 32.3, lon: -64.8 },
  { hr: "Gvajana", en: "Guyana", flag: "🇬🇾", iso: "gy", lat: 5.0, lon: -58.9 },
  { hr: "Venezuela", en: "Venezuela", flag: "🇻🇪", iso: "ve", lat: 7.0, lon: -66.0 },
  { hr: "Kolumbija", en: "Colombia", flag: "🇨🇴", iso: "co", lat: 4.0, lon: -73.0 },
  { hr: "Peru", en: "Peru", flag: "🇵🇪", iso: "pe", lat: -9.0, lon: -75.0 },
  { hr: "Brazil", en: "Brazil", flag: "🇧🇷", iso: "br", lat: -10.0, lon: -52.0 },
  { hr: "Paragvaj", en: "Paraguay", flag: "🇵🇾", iso: "py", lat: -23.4, lon: -58.4 },
  { hr: "Argentina", en: "Argentina", flag: "🇦🇷", iso: "ar", lat: -34.0, lon: -64.0 },
  { hr: "Panama", en: "Panama", flag: "🇵🇦", iso: "pa", lat: 8.4, lon: -80.1 },
  { hr: "Kostarika", en: "Costa Rica", flag: "🇨🇷", iso: "cr", lat: 9.7, lon: -84.0 },
  { hr: "Nikaragva", en: "Nicaragua", flag: "🇳🇮", iso: "ni", lat: 12.9, lon: -85.2 },
  { hr: "Honduras", en: "Honduras", flag: "🇭🇳", iso: "hn", lat: 14.6, lon: -86.6 },
  { hr: "El Salvador", en: "El Salvador", flag: "🇸🇻", iso: "sv", lat: 13.7, lon: -88.9 },
  { hr: "Gvatemala", en: "Guatemala", flag: "🇬🇹", iso: "gt", lat: 15.5, lon: -90.3 },
  { hr: "Meksiko", en: "Mexico", flag: "🇲🇽", iso: "mx", lat: 23.0, lon: -102.0 },
  { hr: "SAD", en: "USA", flag: "🇺🇸", iso: "us", lat: 38.0, lon: -97.0 },
  { hr: "Kanada", en: "Canada", flag: "🇨🇦", iso: "ca", lat: 52.0, lon: -100.0 },
  { hr: "Škotska", en: "Scotland", flag: "🏴󠁧󠁢󠁳󠁣󠁴󠁿", iso: "gb-sct", lat: 56.8, lon: -4.2 },
  { hr: "Irska", en: "Ireland", flag: "🇮🇪", iso: "ie", lat: 53.3, lon: -8.0 },
  { hr: "Sjeverna Irska", en: "Northern Ireland", flag: "🇬🇧", iso: "gb-nir", lat: 54.6, lon: -6.7 },
  { hr: "Wales", en: "Wales", flag: "🏴󠁧󠁢󠁷󠁬󠁳󠁿", iso: "gb-wls", lat: 52.3, lon: -3.7 },
  { hr: "UK", en: "England", flag: "🇬🇧", iso: "gb", lat: 52.0, lon: -1.0 },
  { hr: "Francuska", en: "France", flag: "🇫🇷", iso: "fr", lat: 46.5, lon: 2.5 },
  { hr: "Španjolska", en: "Spain", flag: "🇪🇸", iso: "es", lat: 40.0, lon: -3.7 },
  { hr: "Portugal", en: "Portugal", flag: "🇵🇹", iso: "pt", lat: 39.6, lon: -8.0 },
  { hr: "Italija", en: "Italy", flag: "🇮🇹", iso: "it", lat: 42.8, lon: 12.5 },
  { hr: "Njemačka", en: "Germany", flag: "🇩🇪", iso: "de", lat: 51.0, lon: 10.0 },
  { hr: "Austrija", en: "Austria", flag: "🇦🇹", iso: "at", lat: 47.5, lon: 14.5 },
  { hr: "Švicarska", en: "Switzerland", flag: "🇨🇭", iso: "ch", lat: 46.8, lon: 8.2 },
  { hr: "Nizozemska", en: "Netherlands", flag: "🇳🇱", iso: "nl", lat: 52.2, lon: 5.3 },
  { hr: "Danska", en: "Denmark", flag: "🇩🇰", iso: "dk", lat: 56.0, lon: 10.0 },
  { hr: "Mađarska", en: "Hungary", flag: "🇭🇺", iso: "hu", lat: 47.2, lon: 19.5 },
  { hr: "Hrvatska", en: "Croatia", flag: "🇭🇷", iso: "hr", lat: 44.5, lon: 16.4 },
  { hr: "Grčka", en: "Greece", flag: "🇬🇷", iso: "gr", lat: 39.0, lon: 22.0 },
  { hr: "Armenija", en: "Armenia", flag: "🇦🇲", iso: "am", lat: 40.3, lon: 45.0 },
  { hr: "Turska", en: "Turkey", flag: "🇹🇷", iso: "tr", lat: 39.0, lon: 35.0 },
  { hr: "Kenija", en: "Kenya", flag: "🇰🇪", iso: "ke", lat: 0.4, lon: 37.9 },
  { hr: "Etiopija", en: "Ethiopia", flag: "🇪🇹", iso: "et", lat: 8.6, lon: 39.6 },
  { hr: "Mauricijus", en: "Mauritius", flag: "🇲🇺", iso: "mu", lat: -20.3, lon: 57.6 },
  { hr: "Reunion", en: "Réunion", flag: "🇷🇪", iso: "re", lat: -21.1, lon: 55.5 },
  { hr: "Sejšeli", en: "Seychelles", flag: "🇸🇨", iso: "sc", lat: -4.7, lon: 55.5 },
  { hr: "Indija", en: "India", flag: "🇮🇳", iso: "in", lat: 21.0, lon: 78.0 },
  { hr: "Indonezija", en: "Indonesia", flag: "🇮🇩", iso: "id", lat: -2.5, lon: 118.0 },
  { hr: "Filipini", en: "Philippines", flag: "🇵🇭", iso: "ph", lat: 12.0, lon: 122.0 },
  { hr: "Tajvan", en: "Taiwan", flag: "🇹🇼", iso: "tw", lat: 23.7, lon: 121.0 },
  { hr: "Japan", en: "Japan", flag: "🇯🇵", iso: "jp", lat: 36.5, lon: 138.5 },
  { hr: "Fiji", en: "Fiji", flag: "🇫🇯", iso: "fj", lat: -17.8, lon: 178.0 },
  { hr: "Australija", en: "Australia", flag: "🇦🇺", iso: "au", lat: -25.0, lon: 134.0 },
];

// aliasi koji se u regijama pojavljuju umjesto/uz ime zemlje
const ALIASES: Record<string, string> = {
  Skotska: "Škotska", Spanjolska: "Španjolska", Madjarska: "Mađarska",
  Njemacka: "Njemačka", Grcka: "Grčka",
  Kentucky: "SAD", Tennessee: "SAD", California: "SAD", Indiana: "SAD", Vermont: "SAD",
  London: "UK", Plymouth: "UK",
  Douro: "Portugal", Madeira: "Portugal",
  Jerez: "Španjolska", Rioja: "Španjolska", Penedes: "Španjolska", Katalonija: "Španjolska",
  Cognac: "Francuska", Armagnac: "Francuska", Champagne: "Francuska", Bordeaux: "Francuska",
  Normandija: "Francuska", Burgundija: "Francuska", Rhone: "Francuska", Borderies: "Francuska",
  Veneto: "Italija", Toskana: "Italija", Piemont: "Italija", Puglia: "Italija", Lombardija: "Italija",
  Tokaj: "Mađarska", Mosel: "Njemačka", Schwarzwald: "Njemačka", Rüdesheim: "Njemačka",
  Istra: "Hrvatska", Dalmacija: "Hrvatska", Slavonija: "Hrvatska", Pelješac: "Hrvatska",
  Peljesac: "Hrvatska", Plešivica: "Hrvatska", Primošten: "Hrvatska",
  "Korčula/Brač": "Hrvatska", Negros: "Filipini", Islay: "Škotska", Speyside: "Škotska",
  Highlands: "Škotska", Campbeltown: "Škotska", Orkney: "Škotska", Skye: "Škotska",
  Arran: "Škotska", Dublin: "Irska", Melbourne: "Australija", "Yarra Valley": "Australija",
  Barossa: "Australija", Goa: "Indija", Malabar: "Indija", Sumatra: "Indonezija",
  Jamajka: "Jamajka", Antigua: "Gvatemala", Demerara: "Gvajana", Anguilla: "Sv. Lucija",
};

const byHr = new Map(COUNTRIES.map((c) => [c.hr, c]));

/** Zemlje na koje se odnosi jedno pice (parsira region string). */
export function drinkCountries(d: Drink): CountryInfo[] {
  const region = d.region || "";
  const hits = new Set<CountryInfo>();
  for (const c of COUNTRIES) {
    if (region.includes(c.hr)) hits.add(c);
  }
  for (const [alias, hr] of Object.entries(ALIASES)) {
    if (region.includes(alias)) {
      const c = byHr.get(hr);
      if (c) hits.add(c);
    }
  }
  return [...hits];
}

/** Zemlje jedne cigare (country moze biti "SAD/Nikaragva"). */
export function cigarCountries(c: Cigar): CountryInfo[] {
  return c.country
    .split("/")
    .map((part) => byHr.get(part.trim()))
    .filter((x): x is CountryInfo => Boolean(x));
}
