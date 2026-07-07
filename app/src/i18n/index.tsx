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
  "pair.custom": { hr: "Kombiniraj", en: "Combine" },
  "pair.customTitle": { hr: "Izaberi cigaru i piće", en: "Pick a cigar and a drink" },
  "pair.customHint": { hr: "Odaberi jedno i drugo pa vidi koliko se slažu.", en: "Pick both and see how well they match." },
  "pair.changeCigar": { hr: "Promijeni cigaru", en: "Change cigar" },
  "pair.changeDrink": { hr: "Promijeni piće", en: "Change drink" },
  "pair.verdict5": { hr: "Savršen spoj", en: "Perfect match" },
  "pair.verdict4": { hr: "Odličan spoj", en: "Excellent match" },
  "pair.verdict3": { hr: "Dobar spoj", en: "Good match" },
  "pair.verdict2": { hr: "Osrednje", en: "So-so" },
  "pair.verdict1": { hr: "Slab spoj", en: "Poor match" },
  "pair.pickCigar": { hr: "Odaberi cigaru", en: "Pick a cigar" },
  "pair.pickDrink": { hr: "Odaberi piće", en: "Pick a drink" },
  "pair.search": { hr: "Pretraži…", en: "Search…" },
  "pair.why": { hr: "Zašto paše", en: "Why it works" },
  "pair.match": { hr: "match", en: "match" },
  "pair.onlyMine": { hr: "Samo moja kolekcija", en: "My collection only" },
  "pair.noResults": { hr: "Nema rezultata za odabrane filtere.", en: "No results for the selected filters." },
  "pair.excelHint": { hr: "Kurirana preporuka", en: "Curated recommendation" },
  "pair.suggestions": { hr: "Prijedlozi", en: "Suggestions" },
  "pair.next": { hr: "Sljedeći prijedlog", en: "Next suggestion" },
  "pair.coffeeAlt": { hr: "Bezalkoholna opcija — kava", en: "Non-alcoholic option — coffee" },
  "pair.market": { hr: "Gdje kupuješ cigare?", en: "Where do you buy cigars?" },
  "pair.prefs": { hr: "Preferencije (zemlje / brendovi)", en: "Preferences (countries / brands)" },
  "pair.prefsHint": { hr: "Klikni da isključiš iz prijedloga", en: "Click to exclude from suggestions" },
  "pair.pickVitola": { hr: "Odaberi vitolu", en: "Pick a vitola" },
  "pair.pickVitolaHint": { hr: "Ova linija ima više formata — odaberi vitolu.", en: "This line has multiple sizes — pick a vitola." },
  "common.vitolas": { hr: "Vitole", en: "Vitolas" },
  "coll.inCollection": { hr: "U kolekciji", en: "In collection" },
  "common.vitolaCountSuffix": { hr: "vitola", en: "vitolas" },
  "coll.triedTitle": { hr: "Probano", en: "Tried" },
  "ocr.scan": { hr: "Fotografiraj etiketu", en: "Photograph the label" },
  "ocr.working": { hr: "Prepoznajem…", en: "Recognizing…" },
  "ocr.partial": { hr: "Nisam siguran — pogledaj rezultate pretrage", en: "Not sure — check the search results" },
  "ocr.noMatch": { hr: "Tekst nije prepoznat. Pokušaj bliže, uz više svjetla.", en: "No text recognized. Try closer, with more light." },
  "ocr.error": { hr: "Prepoznavanje nije uspjelo (treba internet za prvi put).", en: "Recognition failed (first use needs internet)." },
  "common.buy": { hr: "Gdje kupiti", en: "Where to buy" },
  "common.searchOnline": { hr: "Traži online", en: "Search online" },
  "price.from": { hr: "od", en: "from" },
  "price.check": { hr: "provjeri cijenu", en: "check price" },
  "price.marketNote": {
    hr: "Cijena vrijedi za odabrano tržište. Za druga tržišta koristi gumbe za kupnju.",
    en: "Price applies to the selected market. For other markets use the buy buttons.",
  },
  "rate.qualityWhat": {
    hr: "Urednička procjena kvalitete (1–10) — kurirano iz recenzija i vlastitih bilješki, nije korisnička ocjena.",
    en: "Editorial quality estimate (1–10) — curated from reviews and notes, not a user rating.",
  },
  "rate.matchWhat": {
    hr: "Postotak slaganja — koliko se ovo piće i cigara slažu prema pravilima uparivanja (tijelo, okusi, wrapper).",
    en: "Match percentage — how well this drink and cigar fit per the pairing rules (body, flavours, wrapper).",
  },
  "rate.match": { hr: "% slaganja", en: "% match" },
  "rate.editorial": { hr: "urednička ocjena", en: "editorial score" },
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
  "cat.gin": { hr: "Gin", en: "Gin" },
  "cat.coffee": { hr: "Kava", en: "Coffee" },
  "cat.cigars": { hr: "Cigare", en: "Cigars" },
  "brand.open": { hr: "Otvori brend", en: "Open brand" },
  "brand.byStrength": { hr: "Po snazi", en: "By strength" },
  "brand.byPrice": { hr: "Po cijeni", en: "By price" },
  "brand.viewAll": { hr: "Sve cigare marke", en: "All cigars by brand" },
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
  "coll.historySection": { hr: "Probano / bilješke (nemam)", en: "Tried / notes (not owned)" },
  // shopping
  "shop.tiers": { hr: "Plan kolekcije (razine)", en: "Collection plan (tiers)" },
  "shop.tierDone": { hr: "Nabavljeno", en: "Acquired" },
  "shop.shops": { hr: "Trgovine", en: "Shops" },
  "shop.recs": { hr: "Preporuke sommeliera", en: "Sommelier recommendations" },
  "shop.miniPath": { hr: "Temeljna petorka — pet boca koje pokrivaju cijeli spektar", en: "The essential five — five bottles covering the full spectrum" },
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
  "london-dry": { hr: "London Dry", en: "London Dry" },
  "premium-dry": { hr: "Premium dry gin", en: "Premium dry gin" },
  contemporary: { hr: "Contemporary / New Western", en: "Contemporary / New Western" },
  "navy-strength": { hr: "Navy Strength", en: "Navy Strength" },
  "old-tom": { hr: "Old Tom", en: "Old Tom" },
  genever: { hr: "Genever", en: "Genever" },
  croatian: { hr: "HR craft gin", en: "Croatian craft gin" },
  plymouth: { hr: "Plymouth", en: "Plymouth" },
  flavored: { hr: "Aromatiziran (ne za cigaru)", en: "Flavoured (not for cigars)" },
};

// hrvatska imena zemalja u podacima -> engleski prikaz
export const COUNTRY_LABELS: Record<string, string> = {
  Kuba: "Cuba",
  Nikaragva: "Nicaragua",
  Dominikana: "Dominican Republic",
  Meksiko: "Mexico",
  "SAD/Nikaragva": "USA/Nicaragua",
  Škotska: "Scotland",
  Francuska: "France",
  Španjolska: "Spain",
  Irska: "Ireland",
  Njemačka: "Germany",
  Grčka: "Greece",
  Italija: "Italy",
  Hrvatska: "Croatia",
  Armenija: "Armenia",
  Indija: "India",
  Australija: "Australia",
  Tajvan: "Taiwan",
  Švicarska: "Switzerland",
  Nizozemska: "Netherlands",
};

// ceste "najbolji nacin" serviranja iz podataka -> engleski prikaz
export const SERVING_LABELS: Record<string, string> = {
  "Cisto": "Neat",
  "Cisto / kap vode": "Neat / drop of water",
  "Kap vode": "Drop of water",
  "Kap vode (otvara estere)": "Drop of water (opens the esters)",
  "Kap vode (cask strength)": "Drop of water (cask strength)",
  "Cisto / Ti' Punch": "Neat / Ti' Punch",
  "On the rocks (velika kocka)": "On the rocks (big cube)",
  "On the rocks / kap vode": "On the rocks / drop of water",
  "On the rocks / cisto": "On the rocks / neat",
  "Velika kocka leda ili kap vode": "Big ice cube or a drop of water",
  "Koktel / highball": "Cocktail / highball",
  "Cisto (snifter)": "Neat (snifter)",
  "Cisto / on the rocks": "Neat / on the rocks",
  "Cisto / Old Fashioned": "Neat / Old Fashioned",
  "Cisto / highball": "Neat / highball",
  "Uz kavu": "With coffee",
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
  cn: (country: string) => string; // ime zemlje u aktivnom jeziku
  sv: (serving: string) => string; // nacin serviranja u aktivnom jeziku
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
  // imena zemalja i serviranja u podacima su hrvatska; na EN prevedi mapom
  const cn = (country: string) =>
    lang === "en" ? (COUNTRY_LABELS[country] ?? country) : country;
  const sv = (serving: string) =>
    lang === "en" ? (SERVING_LABELS[serving] ?? serving) : serving;
  return (
    <Ctx.Provider value={{ lang, setLang, t, lx, cn, sv }}>{children}</Ctx.Provider>
  );
}

export const useI18n = () => useContext(Ctx);
