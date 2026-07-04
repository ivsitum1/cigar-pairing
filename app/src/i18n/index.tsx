import { createContext, useContext, useState, type ReactNode } from "react";
import type { Lang, LocalizedText } from "../types";

const STRINGS = {
  // navigacija
  "nav.pairing": { hr: "Pairing", en: "Pairing" },
  "nav.catalog": { hr: "Katalozi", en: "Catalogs" },
  "nav.collection": { hr: "Kolekcija", en: "Collection" },
  "nav.shopping": { hr: "Kupovina", en: "Shopping" },
  // pairing
  "pair.cigarToDrink": { hr: "Cigara → Piće", en: "Cigar → Drink" },
  "pair.drinkToCigar": { hr: "Piće → Cigara", en: "Drink → Cigar" },
  "pair.pickCigar": { hr: "Odaberi cigaru", en: "Pick a cigar" },
  "pair.pickDrink": { hr: "Odaberi piće", en: "Pick a drink" },
  "pair.search": { hr: "Pretraži…", en: "Search…" },
  "pair.why": { hr: "Zašto paše", en: "Why it works" },
  "pair.match": { hr: "match", en: "match" },
  "pair.onlyMine": { hr: "Samo moja kolekcija", en: "My collection only" },
  "pair.noResults": { hr: "Nema rezultata za odabrane filtere.", en: "No results for the selected filters." },
  "pair.excelHint": { hr: "Preporuka iz tvoje tablice", en: "Recommendation from your spreadsheet" },
  "pair.suggestions": { hr: "Prijedlozi", en: "Suggestions" },
  "pair.next": { hr: "Sljedeći prijedlog", en: "Next suggestion" },
  "pair.coffeeAlt": { hr: "Bezalkoholna opcija — kava", en: "Non-alcoholic option — coffee" },
  "pair.market": { hr: "Gdje kupuješ cigare?", en: "Where do you buy cigars?" },
  "pair.prefs": { hr: "Preferencije (zemlje / brendovi)", en: "Preferences (countries / brands)" },
  "pair.prefsHint": { hr: "Klikni da isključiš iz prijedloga", en: "Click to exclude from suggestions" },
  "common.vitolas": { hr: "Vitole", en: "Vitolas" },
  "ocr.scan": { hr: "Fotografiraj etiketu", en: "Photograph the label" },
  "ocr.working": { hr: "Prepoznajem…", en: "Recognizing…" },
  "ocr.partial": { hr: "Nisam siguran — pogledaj rezultate pretrage", en: "Not sure — check the search results" },
  "ocr.noMatch": { hr: "Tekst nije prepoznat. Pokušaj bliže, uz više svjetla.", en: "No text recognized. Try closer, with more light." },
  "ocr.error": { hr: "Prepoznavanje nije uspjelo (treba internet za prvi put).", en: "Recognition failed (first use needs internet)." },
  "common.buy": { hr: "Gdje kupiti", en: "Where to buy" },
  "common.searchOnline": { hr: "Traži online", en: "Search online" },
  "market.HR": { hr: "Hrvatska", en: "Croatia" },
  "market.EU": { hr: "EU", en: "EU" },
  "market.USA": { hr: "USA", en: "USA" },
  "market.WW": { hr: "Svijet", en: "Worldwide" },
  // opće
  "common.body": { hr: "Tijelo", en: "Body" },
  "common.strength": { hr: "Snaga", en: "Strength" },
  "common.sweetness": { hr: "Slatkoća", en: "Sweetness" },
  "common.cigar": { hr: "Cigara", en: "Cigar" },
  "common.drink": { hr: "Piće", en: "Drink" },
  "common.wrapper": { hr: "Wrapper", en: "Wrapper" },
  "common.quality": { hr: "Kvaliteta", en: "Quality" },
  "common.price": { hr: "Cijena", en: "Price" },
  "common.approx": { hr: "cca", en: "approx." },
  "common.minutes": { hr: "min", en: "min" },
  "common.all": { hr: "Sve", en: "All" },
  "common.serving": { hr: "Serviranje", en: "Serving" },
  "common.additives": { hr: "Aditivi", en: "Additives" },
  "common.close": { hr: "Zatvori", en: "Close" },
  "common.time": { hr: "Vrijeme", en: "Time" },
  "common.shop": { hr: "Trgovina", en: "Shop" },
  "common.buyIn": { hr: "Kupnja", en: "Buy" },
  "common.sources": { hr: "Izvori cijena i opisa", en: "Price & description sources" },
  "common.markets": { hr: "Dostupnost", en: "Availability" },
  // kategorije
  "cat.rum": { hr: "Rum", en: "Rum" },
  "cat.whisky": { hr: "Whisky", en: "Whisky" },
  "cat.brandy": { hr: "Konjak / Brandy", en: "Cognac / Brandy" },
  "cat.coffee": { hr: "Kava", en: "Coffee" },
  "cat.cigars": { hr: "Cigare", en: "Cigars" },
  // kolekcija
  "coll.owned": { hr: "Imam", en: "Owned" },
  "coll.tried": { hr: "Probao", en: "Tried" },
  "coll.myRating": { hr: "Moja ocjena", en: "My rating" },
  "coll.note": { hr: "Bilješka", en: "Note" },
  "coll.notePlaceholder": { hr: "Dojmovi, uz što je pasalo…", en: "Impressions, what it paired with…" },
  "coll.empty": { hr: "Kolekcija je prazna. Označi boce i cigare u katalozima ili ovdje.", en: "Collection is empty. Mark bottles and cigars in the catalogs or here." },
  "coll.export": { hr: "Export podataka", en: "Export data" },
  "coll.import": { hr: "Import podataka", en: "Import data" },
  "coll.journal": { hr: "Dnevnik pairinga", en: "Pairing journal" },
  "coll.journalEmpty": { hr: "Još nema zabilježenih pairinga. Nakon dobre kombinacije, zabilježi je ovdje.", en: "No pairings logged yet. After a good combination, log it here." },
  "coll.addPairing": { hr: "Zabilježi pairing", en: "Log a pairing" },
  "coll.save": { hr: "Spremi", en: "Save" },
  "coll.delete": { hr: "Obriši", en: "Delete" },
  "coll.importOk": { hr: "Podaci uvezeni.", en: "Data imported." },
  "coll.importErr": { hr: "Neispravna datoteka.", en: "Invalid file." },
  "coll.stats": { hr: "boca/cigara u kolekciji", en: "bottles/cigars in collection" },
  // shopping
  "shop.tiers": { hr: "Plan kolekcije (tierovi)", en: "Collection plan (tiers)" },
  "shop.tierDone": { hr: "Nabavljeno", en: "Acquired" },
  "shop.shops": { hr: "Trgovine", en: "Shops" },
  "shop.recs": { hr: "Najbolji potezi", en: "Best moves" },
  "shop.miniPath": { hr: "Mini-put: 5 boca = prava širina", en: "Mini path: 5 bottles = real breadth" },
  "shop.legalNote": { hr: "Internetska prodaja duhana u Hrvatskoj nije dozvoljena — cijene cigara su referentne, kupnja u trgovini.", en: "Online tobacco sales are not allowed in Croatia — cigar prices are reference only, buy in store." },
  // filteri
  "filter.style": { hr: "Stil", en: "Style" },
  "filter.strength": { hr: "Snaga", en: "Strength" },
  "filter.maxPrice": { hr: "Cijena do", en: "Price up to" },
  "filter.clean": { hr: "Samo čisti (bez aditiva)", en: "Clean only (no additives)" },
} satisfies Record<string, LocalizedText>;

export type StringKey = keyof typeof STRINGS;

// stilovi pića — labels
export const STYLE_LABELS: Record<string, LocalizedText> = {
  jamaica: { hr: "Jamajka (esterski)", en: "Jamaica (high ester)" },
  agricole: { hr: "Agricole", en: "Agricole" },
  barbados: { hr: "Barbados", en: "Barbados" },
  cuba: { hr: "Kuba", en: "Cuba" },
  demerara: { hr: "Demerara", en: "Demerara" },
  solera: { hr: "Solera", en: "Solera" },
  "nicaragua-dry": { hr: "Nikaragva (suhi)", en: "Nicaragua (dry)" },
  colombia: { hr: "Kolumbija", en: "Colombia" },
  "st-lucia": { hr: "Sv. Lucija", en: "St. Lucia" },
  trinidad: { hr: "Trinidad", en: "Trinidad" },
  "puerto-rico": { hr: "Puerto Rico", en: "Puerto Rico" },
  venezuela: { hr: "Venezuela", en: "Venezuela" },
  dominican: { hr: "Dominikana", en: "Dominican" },
  navy: { hr: "Navy blend", en: "Navy blend" },
  blend: { hr: "Blend (više regija)", en: "Multi-region blend" },
  panama: { hr: "Panama", en: "Panama" },
  other: { hr: "Ostalo", en: "Other" },
  spiced: { hr: "Spiced (ne za cigaru)", en: "Spiced (not for cigars)" },
  liqueur: { hr: "Liker (ne za cigaru)", en: "Liqueur (not for cigars)" },
  mixing: { hr: "Mixing", en: "Mixing" },
  "speyside-sherry": { hr: "Speyside/sherry", en: "Speyside/sherry" },
  "speyside-fruity": { hr: "Speyside (voćni)", en: "Speyside (fruity)" },
  highland: { hr: "Highland", en: "Highland" },
  island: { hr: "Otočni", en: "Island" },
  "islay-peated": { hr: "Islay (treset)", en: "Islay (peated)" },
  campbeltown: { hr: "Campbeltown", en: "Campbeltown" },
  "blended-scotch": { hr: "Blended scotch", en: "Blended scotch" },
  bourbon: { hr: "Bourbon", en: "Bourbon" },
  tennessee: { hr: "Tennessee", en: "Tennessee" },
  rye: { hr: "Rye", en: "Rye" },
  "irish-pot-still": { hr: "Irski pot still", en: "Irish pot still" },
  "irish-blend": { hr: "Irski blend", en: "Irish blend" },
  "irish-single-malt": { hr: "Irski single malt", en: "Irish single malt" },
  japanese: { hr: "Japan", en: "Japan" },
  world: { hr: "Svijet", en: "World" },
  "cognac-vs": { hr: "Cognac VS", en: "Cognac VS" },
  "cognac-vsop": { hr: "Cognac VSOP", en: "Cognac VSOP" },
  "cognac-xo": { hr: "Cognac XO", en: "Cognac XO" },
  armagnac: { hr: "Armagnac", en: "Armagnac" },
  "brandy-de-jerez": { hr: "Brandy de Jerez", en: "Brandy de Jerez" },
  "brandy-spanish": { hr: "Španjolski brandy", en: "Spanish brandy" },
  "brandy-greek": { hr: "Grčki brandy", en: "Greek brandy" },
  "brandy-italian": { hr: "Talijanski brandy", en: "Italian brandy" },
  "brandy-armenian": { hr: "Armenski brandy", en: "Armenian brandy" },
  "brandy-german": { hr: "Njemački brandy", en: "German brandy" },
  vinjak: { hr: "Vinjak (HR)", en: "Vinjak (HR)" },
  calvados: { hr: "Calvados", en: "Calvados" },
  "espresso-dark": { hr: "Espresso (tamni)", en: "Espresso (dark)" },
  "espresso-medium": { hr: "Espresso (medium)", en: "Espresso (medium)" },
  turkish: { hr: "Turska/domaća", en: "Turkish" },
  moka: { hr: "Moka pot", en: "Moka pot" },
  "filter-light": { hr: "Filter (light roast)", en: "Filter (light roast)" },
  "filter-medium": { hr: "Filter (medium)", en: "Filter (medium)" },
  "filter-dark": { hr: "Filter (dark)", en: "Filter (dark)" },
  cold: { hr: "Cold brew", en: "Cold brew" },
  milk: { hr: "S mlijekom", en: "With milk" },
  spiked: { hr: "S alkoholom", en: "Spiked" },
};

export const ADDITIVE_LABELS: Record<string, LocalizedText> = {
  clean: { hr: "Čist", en: "Clean" },
  low: { hr: "Vrlo nizak", en: "Very low" },
  light: { hr: "Blagi dodatak", en: "Light addition" },
  moderate: { hr: "Umjeren dodatak", en: "Moderate addition" },
  sweetened: { hr: "Dosladjen", en: "Sweetened" },
  flavored: { hr: "Aromatiziran", en: "Flavoured" },
  unknown: { hr: "Nepoznato", en: "Unknown" },
};

interface I18nCtx {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: StringKey) => string;
  lx: (text: LocalizedText | undefined | null) => string;
}

const Ctx = createContext<I18nCtx>(null!);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(
    () => (localStorage.getItem("lang") as Lang) || "hr",
  );
  const setLang = (l: Lang) => {
    localStorage.setItem("lang", l);
    setLangState(l);
  };
  const t = (key: StringKey) => STRINGS[key][lang];
  const lx = (text: LocalizedText | undefined | null) => {
    if (!text) return "";
    return text[lang] || text.hr || text.en;
  };
  return <Ctx.Provider value={{ lang, setLang, t, lx }}>{children}</Ctx.Provider>;
}

export const useI18n = () => useContext(Ctx);
