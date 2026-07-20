// Zemljopis pica i cigara — koordinate za kartu i uparivanje po zemlji.
// Kljuc je hrvatsko ime zemlje kako se pojavljuje u podacima (region/country).

import type { Cigar, Drink } from "../types";

export interface CountryInfo {
  hr: string;
  en: string;
  flag: string;
  lat: number;
  lon: number;
}

export const COUNTRIES: CountryInfo[] = [
  { hr: "Kuba", en: "Cuba", flag: "🇨🇺", lat: 22.0, lon: -79.5 },
  { hr: "Dominikanska Republika", en: "Dominican Republic", flag: "🇩🇴", lat: 18.9, lon: -70.2 },
  { hr: "Jamajka", en: "Jamaica", flag: "🇯🇲", lat: 18.1, lon: -77.3 },
  { hr: "Barbados", en: "Barbados", flag: "🇧🇧", lat: 13.2, lon: -59.5 },
  { hr: "Trinidad", en: "Trinidad", flag: "🇹🇹", lat: 10.5, lon: -61.3 },
  { hr: "Sv. Lucija", en: "St Lucia", flag: "🇱🇨", lat: 13.9, lon: -61.0 },
  { hr: "Martinique", en: "Martinique", flag: "🇲🇶", lat: 14.6, lon: -61.0 },
  { hr: "Guadeloupe", en: "Guadeloupe", flag: "🇬🇵", lat: 16.2, lon: -61.5 },
  { hr: "Puerto Rico", en: "Puerto Rico", flag: "🇵🇷", lat: 18.2, lon: -66.4 },
  { hr: "Bermuda", en: "Bermuda", flag: "🇧🇲", lat: 32.3, lon: -64.8 },
  { hr: "Gvajana", en: "Guyana", flag: "🇬🇾", lat: 5.0, lon: -58.9 },
  { hr: "Venezuela", en: "Venezuela", flag: "🇻🇪", lat: 7.0, lon: -66.0 },
  { hr: "Kolumbija", en: "Colombia", flag: "🇨🇴", lat: 4.0, lon: -73.0 },
  { hr: "Peru", en: "Peru", flag: "🇵🇪", lat: -9.0, lon: -75.0 },
  { hr: "Brazil", en: "Brazil", flag: "🇧🇷", lat: -10.0, lon: -52.0 },
  { hr: "Paragvaj", en: "Paraguay", flag: "🇵🇾", lat: -23.4, lon: -58.4 },
  { hr: "Argentina", en: "Argentina", flag: "🇦🇷", lat: -34.0, lon: -64.0 },
  { hr: "Panama", en: "Panama", flag: "🇵🇦", lat: 8.4, lon: -80.1 },
  { hr: "Kostarika", en: "Costa Rica", flag: "🇨🇷", lat: 9.7, lon: -84.0 },
  { hr: "Nikaragva", en: "Nicaragua", flag: "🇳🇮", lat: 12.9, lon: -85.2 },
  { hr: "Honduras", en: "Honduras", flag: "🇭🇳", lat: 14.6, lon: -86.6 },
  { hr: "El Salvador", en: "El Salvador", flag: "🇸🇻", lat: 13.7, lon: -88.9 },
  { hr: "Gvatemala", en: "Guatemala", flag: "🇬🇹", lat: 15.5, lon: -90.3 },
  { hr: "Meksiko", en: "Mexico", flag: "🇲🇽", lat: 23.0, lon: -102.0 },
  { hr: "SAD", en: "USA", flag: "🇺🇸", lat: 38.0, lon: -97.0 },
  { hr: "Kanada", en: "Canada", flag: "🇨🇦", lat: 52.0, lon: -100.0 },
  { hr: "Škotska", en: "Scotland", flag: "🏴󠁧󠁢󠁳󠁣󠁴󠁿", lat: 56.8, lon: -4.2 },
  { hr: "Irska", en: "Ireland", flag: "🇮🇪", lat: 53.3, lon: -8.0 },
  { hr: "Sjeverna Irska", en: "Northern Ireland", flag: "🇬🇧", lat: 54.6, lon: -6.7 },
  { hr: "Wales", en: "Wales", flag: "🏴󠁧󠁢󠁷󠁬󠁳󠁿", lat: 52.3, lon: -3.7 },
  { hr: "UK", en: "England", flag: "🇬🇧", lat: 52.0, lon: -1.0 },
  { hr: "Francuska", en: "France", flag: "🇫🇷", lat: 46.5, lon: 2.5 },
  { hr: "Španjolska", en: "Spain", flag: "🇪🇸", lat: 40.0, lon: -3.7 },
  { hr: "Portugal", en: "Portugal", flag: "🇵🇹", lat: 39.6, lon: -8.0 },
  { hr: "Italija", en: "Italy", flag: "🇮🇹", lat: 42.8, lon: 12.5 },
  { hr: "Njemačka", en: "Germany", flag: "🇩🇪", lat: 51.0, lon: 10.0 },
  { hr: "Austrija", en: "Austria", flag: "🇦🇹", lat: 47.5, lon: 14.5 },
  { hr: "Švicarska", en: "Switzerland", flag: "🇨🇭", lat: 46.8, lon: 8.2 },
  { hr: "Nizozemska", en: "Netherlands", flag: "🇳🇱", lat: 52.2, lon: 5.3 },
  { hr: "Danska", en: "Denmark", flag: "🇩🇰", lat: 56.0, lon: 10.0 },
  { hr: "Mađarska", en: "Hungary", flag: "🇭🇺", lat: 47.2, lon: 19.5 },
  { hr: "Hrvatska", en: "Croatia", flag: "🇭🇷", lat: 44.5, lon: 16.4 },
  { hr: "Grčka", en: "Greece", flag: "🇬🇷", lat: 39.0, lon: 22.0 },
  { hr: "Armenija", en: "Armenia", flag: "🇦🇲", lat: 40.3, lon: 45.0 },
  { hr: "Turska", en: "Turkey", flag: "🇹🇷", lat: 39.0, lon: 35.0 },
  { hr: "Kenija", en: "Kenya", flag: "🇰🇪", lat: 0.4, lon: 37.9 },
  { hr: "Etiopija", en: "Ethiopia", flag: "🇪🇹", lat: 8.6, lon: 39.6 },
  { hr: "Mauricijus", en: "Mauritius", flag: "🇲🇺", lat: -20.3, lon: 57.6 },
  { hr: "Reunion", en: "Réunion", flag: "🇷🇪", lat: -21.1, lon: 55.5 },
  { hr: "Sejšeli", en: "Seychelles", flag: "🇸🇨", lat: -4.7, lon: 55.5 },
  { hr: "Indija", en: "India", flag: "🇮🇳", lat: 21.0, lon: 78.0 },
  { hr: "Indonezija", en: "Indonesia", flag: "🇮🇩", lat: -2.5, lon: 118.0 },
  { hr: "Filipini", en: "Philippines", flag: "🇵🇭", lat: 12.0, lon: 122.0 },
  { hr: "Tajvan", en: "Taiwan", flag: "🇹🇼", lat: 23.7, lon: 121.0 },
  { hr: "Japan", en: "Japan", flag: "🇯🇵", lat: 36.5, lon: 138.5 },
  { hr: "Fiji", en: "Fiji", flag: "🇫🇯", lat: -17.8, lon: 178.0 },
  { hr: "Australija", en: "Australia", flag: "🇦🇺", lat: -25.0, lon: 134.0 },
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
