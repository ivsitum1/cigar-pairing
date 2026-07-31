import { createContext, useContext, useState, type ReactNode } from "react";
import { resolveLang } from "../lib/safeStorage";
import type { Lang, LocalizedText } from "../types";
import { REGION_LABELS } from "./regions";

const STRINGS = {
  // navigacija
  "nav.pairing": { hr: "Sparivanje", en: "Pairing" },
  "nav.catalog": { hr: "Katalozi", en: "Catalogs" },
  "nav.collection": { hr: "Kolekcija", en: "Collection" },
  "nav.shopping": { hr: "Kupnja", en: "Shopping" },
  "nav.club": { hr: "Klub", en: "Club" },
  // sustav
  "sys.updateReady": { hr: "Nova verzija je spremna.", en: "A new version is ready." },
  "sys.reload": { hr: "Osvježi", en: "Reload" },
  "sys.storageFail": {
    hr: "Spremanje nije uspjelo (prostor za pohranu pun je ili blokiran) — promjene vrijede samo do zatvaranja. Izvezi sigurnosnu kopiju u Kolekciji.",
    en: "Saving failed (storage full or blocked) — changes last only until you close the app. Export a backup from Collection.",
  },
  // klub
  "club.quote": { hr: "Citat dana", en: "Quote of the day" },
  "club.fact": { hr: "Znaš li…?", en: "Did you know…?" },
  "club.factNext": { hr: "Još jedna", en: "Another one" },
  "club.101": { hr: "101 — od nule", en: "101 — the basics" },
  "club.101Hint": {
    hr: "Kratki vodiči o cigarama, pićima i priboru. Poveznice na trgovine su neobavezne i vode na domaće i internetske dućane.",
    en: "Short guides: cigars, drinks and accessories. Shop links are optional — local and online retailers.",
  },
  "club.101Teaser": {
    hr: "Mali tečaj o cigarama, pićima, priboru i sitnim trikovima. Svaka lekcija otvara se na svojoj stranici.",
    en: "A mini course: cigars, drinks, accessories and tips. Lessons open in their own view.",
  },
  "club.101Open": { hr: "Otvori tečaj", en: "Open the course" },
  "club.101CourseHint": {
    hr: "Prvo se bira cjelina, a zatim lekcija. Poveznice na trgovine vode na konkretne kategorije pribora.",
    en: "Pick a track, then a lesson. Shop links go to concrete accessory categories.",
  },
  "club.101BackClub": { hr: "Natrag u Klub", en: "Back to Club" },
  "club.101BackTrack": { hr: "Natrag na popis", en: "Back to list" },
  "club.101OpenLesson": { hr: "Otvori lekciju", en: "Open lesson" },
  "club.101Lessons": { hr: "lekcija", en: "lessons" },
  "club.trackCigars": { hr: "Cigare", en: "Cigars" },
  "club.trackDrinks": { hr: "Pića", en: "Drinks" },
  "club.trackAccessories": { hr: "Pribor", en: "Accessories" },
  "club.trackTips": { hr: "Trikovi", en: "Tips" },
  "club.shopLink": { hr: "Trgovina", en: "Shop" },
  "club.bonton": { hr: "Pušački bonton", en: "Smoking manners" },
  "club.bontonTeaser": {
    hr: "Mala knjiga manira za stol s cigarom i čašom — jedanaest kratkih poglavlja u duhu klasičnog britanskog bontona.",
    en: "A short book of manners for a table with cigar and glass — eleven brief chapters in the spirit of classic British etiquette.",
  },
  "club.bontonOpen": { hr: "Otvori knjigu", en: "Open the book" },
  "club.bontonSubtitle": { hr: "Kratka knjiga manira", en: "A short book of manners" },
  "club.bontonChapters": { hr: "poglavlja", en: "chapters" },
  "club.bontonOpenChapter": { hr: "Čitaj poglavlje", en: "Read chapter" },
  "club.bontonBackList": { hr: "Natrag na sadržaj", en: "Back to contents" },
  "club.lexicon": { hr: "Leksikon sparivanja", en: "Pairing language lexicon" },
  "club.lexiconTeaser": {
    hr: "Kratak vodič za govor o spoju: kako opisati što spaja cigaru i piće — most (zajednička točka), tijelo, snaga, trećine i ritam.",
    en: "A short guide to pairing speech: how to describe what connects a cigar and a drink — the bridge (a shared point), body, strength, thirds and rhythm.",
  },
  "club.lexiconOpen": { hr: "Otvori leksikon", en: "Open the lexicon" },
  "club.lexiconSubtitle": { hr: "Jezik za stol", en: "Language for the table" },
  "club.lexiconEntries": { hr: "unosa", en: "entries" },
  "club.lexiconOpenEntry": { hr: "Čitaj unos", en: "Read entry" },
  "club.lexiconBackClub": { hr: "Natrag u Klub", en: "Back to Club" },
  "club.lexiconBackList": { hr: "Natrag na leksikon", en: "Back to lexicon" },
  "club.dictionary": { hr: "Rječnik", en: "Dictionary" },
  "club.dictionaryTeaser": {
    hr: "Pojmovnik stola: cigara, piće, sparivanje i bonton — definicija plus objašnjenje, ne samo prijevod.",
    en: "A table glossary: cigar, drink, pairing and etiquette — definition plus explanation, not merely a translation.",
  },
  "club.dictionaryOpen": { hr: "Otvori rječnik", en: "Open the dictionary" },
  "club.dictionarySubtitle": { hr: "Pojmovnik stola", en: "Table glossary" },
  "club.dictionaryEntries": { hr: "unosa", en: "entries" },
  "club.dictionaryOpenEntry": { hr: "Čitaj unos", en: "Read entry" },
  "club.dictionaryBackClub": { hr: "Natrag u Klub", en: "Back to Club" },
  "club.dictionaryBackList": { hr: "Natrag na rječnik", en: "Back to dictionary" },
  "club.dictionarySearch": { hr: "Traži pojam…", en: "Search a term…" },
  "club.dictionaryEmpty": { hr: "Nema unosa za taj upit.", en: "No entries match that search." },
  "club.dictionaryCatAll": { hr: "Sve", en: "All" },
  "club.dictionaryCatCigar": { hr: "Cigara", en: "Cigar" },
  "club.dictionaryCatDrink": { hr: "Piće", en: "Drink" },
  "club.dictionaryCatPairing": { hr: "Sparivanje", en: "Pairing" },
  "club.dictionaryCatTable": { hr: "Stol", en: "Table" },
  "club.dictionarySeeAlso": { hr: "Vidi i", en: "See also" },
  "club.dictionaryDoNotConfuse": { hr: "Ne miješati s", en: "Do not confuse with" },
  "club.hrGuide": { hr: "HR vodič kupnje", en: "Croatia buying guide" },
  "club.hrGuideTeaser": {
    hr: "Praktičan vodič za kupnju u Hrvatskoj: duhan, pića, cijene, poveznice, prva oprema, zaliha i pokloni.",
    en: "A practical buying guide for Croatia: tobacco, drinks, prices, links, first kit, stock and gifts.",
  },
  "club.hrGuideOpen": { hr: "Otvori vodič", en: "Open the guide" },
  "club.hrGuideSubtitle": { hr: "Lokalna pravila kupnje", en: "Local buying rules" },
  "club.hrGuideSections": { hr: "odjeljaka", en: "sections" },
  "club.hrGuideOpenSection": { hr: "Čitaj odjeljak", en: "Read section" },
  "club.hrGuideBackClub": { hr: "Natrag u Klub", en: "Back to Club" },
  "club.hrGuideBackList": { hr: "Natrag na vodič", en: "Back to guide" },
  "club.archetypes": { hr: "Večernji arhetipovi", en: "Evening archetypes" },
  "club.archetypesTeaser": {
    hr: "Šest stilskih eseja o večernjem sparivanju: od suhoće Connecticuta i amontillada do espressa uz kratku vitolu.",
    en: "Six style essays for evening pairing: from Connecticut and amontillado dryness to espresso and a short vitola.",
  },
  "club.archetypesOpen": { hr: "Otvori arhetipove", en: "Open archetypes" },
  "club.archetypesSubtitle": { hr: "Stilske slike za večer", en: "Style sketches for the evening" },
  "club.archetypesEntries": { hr: "arhetipova", en: "archetypes" },
  "club.archetypesOpenEntry": { hr: "Čitaj arhetip", en: "Read archetype" },
  "club.archetypesBackClub": { hr: "Natrag u Klub", en: "Back to Club" },
  "club.archetypesBackList": { hr: "Natrag na arhetipove", en: "Back to archetypes" },
  "common.back": { hr: "Natrag", en: "Back" },
  "club.quiz": { hr: "Kviz", en: "Quiz" },
  "club.quizNext": { hr: "Sljedeće pitanje", en: "Next question" },
  "club.quizScore": { hr: "Rezultat", en: "Score" },
  "club.quizStreak": { hr: "Niz", en: "Streak" },
  "club.correct": { hr: "Točno", en: "Correct" },
  "club.wrong": { hr: "Netočno", en: "Incorrect" },
  "club.map": { hr: "Karta podrijetla", en: "Map of origins" },
  "club.mapHint": { hr: "Dodir na zastavicu ili na zemlju s popisa otvara sve cigare i pića iz te zemlje.", en: "Tap a flag or a country in the list — every cigar and drink from that country will appear." },
  "club.mapWorld": { hr: "Svijet", en: "World" },
  "club.mapCarib": { hr: "Karibi i Srednja Amerika", en: "Caribbean & Central America" },
  "club.sources": { hr: "Izvori", en: "Sources" },
  "club.mapEurope": { hr: "Europa", en: "Europe" },
  "club.products": { hr: "proizvoda", en: "products" },
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
  "pair.match": { hr: "slaganje", en: "match" },
  "pair.onlyMine": { hr: "Samo moja kolekcija", en: "My collection only" },
  "pair.drinkTypeAll": { hr: "Sva pića", en: "All drinks" },
  "pair.noResults": { hr: "Nema rezultata za odabrane filtre.", en: "No results for the selected filters." },
  "pair.excelHint": { hr: "Urednička preporuka", en: "Curated recommendation" },
  "pair.curatedWarn": { hr: "Uredničko upozorenje", en: "Curated warning" },
  "pair.suggestions": { hr: "Prijedlozi", en: "Suggestions" },
  "pair.next": { hr: "Sljedeći prijedlog", en: "Next suggestion" },
  "pair.coffeeAlt": { hr: "Bezalkoholna opcija — kava", en: "Non-alcoholic option — coffee" },
  "session.log": { hr: "Zabilježi večer", en: "Log the evening" },
  "session.logThis": { hr: "Zabilježi ovaj spoj", en: "Log this pairing" },
  "session.title": { hr: "Večernji spoj", en: "Evening pairing" },
  "session.hint": {
    hr: "Spremi ovaj spoj u dnevnik — ocjena lokalno naginje buduće prijedloge.",
    en: "Save this match to your journal — the rating gently nudges future suggestions.",
  },
  "session.markTried": { hr: "Označi cigaru i piće kao probano", en: "Mark cigar and drink as tried" },
  "session.save": { hr: "Spremi večer", en: "Save evening" },
  "session.saved": { hr: "Večer zabilježena.", en: "Evening logged." },
  "session.recommendations": { hr: "Preporuke", en: "Recommendations" },
  "session.customDrink": { hr: "Ostalo — pretraži katalog", en: "Other — search catalog" },
  "session.solo": { hr: "Samo cigara", en: "Cigar only" },
  "session.soloLabel": { hr: "solo", en: "solo" },
  "session.searchDrink": { hr: "Traži piće…", en: "Search drinks…" },
  "session.wishlistAtZero": {
    hr: "Zaliha je 0. Dodati na listu želja?",
    en: "Stock is 0. Add to wishlist?",
  },
  "session.noRecommendations": { hr: "Nema preporuka — odaberi iz kataloga ili solo", en: "No recommendations — pick from catalog or solo" },
  "serve.title": { hr: "Kako serviraš?", en: "How do you serve it?" },
  "serve.neat": { hr: "Čisto", en: "Neat" },
  "serve.water": { hr: "Kap vode", en: "Splash of water" },
  "serve.rocks": { hr: "Na ledu", en: "On the rocks" },
  "serve.highball": { hr: "Highball", en: "Highball" },
  "serve.cola": { hr: "S colom", en: "With cola" },
  "serve.best": { hr: "Najbolje", en: "Best" },
  "share.pairing": { hr: "Podijeli", en: "Share" },
  "share.shared": { hr: "Kartica spremna za dijeljenje.", en: "Card ready to share." },
  "share.downloaded": { hr: "Kartica preuzeta (PNG).", en: "Card downloaded (PNG)." },
  "share.failed": { hr: "Dijeljenje nije uspjelo.", en: "Sharing failed." },
  "pair.market": { hr: "Gdje kupuješ cigare?", en: "Where do you buy cigars?" },
  "pair.prefs": { hr: "Postavke (zemlje / marke)", en: "Preferences (countries / brands)" },
  "pair.prefsHint": { hr: "Klikni da isključiš iz prijedloga", en: "Click to exclude from suggestions" },
  "shop.otherShops": { hr: "ostalo", en: "other" },
  "shop.filterAll": { hr: "Sve", en: "All" },
  "pair.occasion": { hr: "Prilika", en: "Occasion" },
  "occ.morning": { hr: "☀ Jutro", en: "☀ Morning" },
  "occ.afternoon": { hr: "🌤 Poslijepodne", en: "🌤 Afternoon" },
  "occ.evening": { hr: "🌙 Večer", en: "🌙 Evening" },
  "common.estimatedProfile": {
    hr: "Procijenjeni profil — okusi izvedeni iz pokrovnog lista i marke, a ne iz degustacije",
    en: "Estimated profile — flavours inferred from wrapper and brand, not from tasting",
  },
  "common.estimatedShort": { hr: "procijenjeno", en: "estimated" },
  "common.flavoured": { hr: "Aromatizirano", en: "Flavoured" },
  "common.formatEstimated": {
    hr: "duljina procijenjena iz vitole — trgovina nije navela dimenzije",
    en: "length estimated from the vitola (shop didn't state dimensions)",
  },
  "common.strengthReal": { hr: "snaga iz ocjene trgovine", en: "strength from shop rating" },
  "footer.copyright": {
    hr: "© 2026 Cigar & Pairing. Sva prava pridržana.",
    en: "© 2026 Cigar & Pairing. All rights reserved.",
  },
  "footer.music": {
    hr: "Glazba: Night in Venice i No Frills Cumbia, Kevin MacLeod (incompetech.com), licenca CC BY 4.0.",
    en: "Music: Night in Venice and No Frills Cumbia by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0.",
  },
  "footer.tobacco": {
    hr: "Prodaja duhana na daljinu u Hrvatskoj nije dopuštena — poveznice na cigare služe samo kao informacija. Samo za punoljetne (18+).",
    en: "Distance sale of tobacco is not permitted in Croatia — cigar links are for reference only. Adults only (18+).",
  },
  "footer.alcohol": {
    hr: "Alkoholna pića su namijenjena punoljetnima (18+) — uživaj odgovorno.",
    en: "Alcoholic drinks are for adults only (18+) — enjoy responsibly.",
  },
  "footer.prices": {
    hr: "Cijene i dostupnost su okvirne i podložne promjeni — provjeri u trgovini.",
    en: "Prices and availability are indicative and subject to change — verify with the shop.",
  },
  "footer.data": {
    hr: "Dio profila (okusi, tijelo, snaga, duljina) je procjena, a ne rezultat degustacije. Aplikacija nije povezana s trgovinama ni markama; nazivi i marke pripadaju svojim vlasnicima.",
    en: "Some profiles (flavour, body, strength, length) are estimates, not from tasting. Not affiliated with the shops or brands; names and trademarks belong to their owners.",
  },
  "footer.health": {
    hr: "Pušenje šteti zdravlju.",
    en: "Smoking harms your health.",
  },
  "pair.pickVitola": { hr: "Odaberi vitolu", en: "Pick a vitola" },
  "pair.pickVitolaHint": { hr: "Ova linija ima više formata — odaberi vitolu.", en: "This line has multiple sizes — pick a vitola." },
  "common.vitolas": { hr: "Vitole", en: "Vitolas" },
  "common.vitola": { hr: "Vitola", en: "Vitola" },
  "coll.inCollection": { hr: "U kolekciji", en: "In collection" },
  "common.vitolaCountSuffix": { hr: "vitola", en: "vitolas" },
  "coll.triedTitle": { hr: "Probano", en: "Tried" },
  "ocr.scan": { hr: "Fotografiraj etiketu", en: "Photograph the label" },
  "ocr.scanReceipt": { hr: "Fotografiraj račun", en: "Photograph the receipt" },
  "ocr.working": { hr: "Prepoznajem…", en: "Recognizing…" },
  "ocr.workingPaddle": { hr: "PaddleOCR (račun)…", en: "PaddleOCR (receipt)…" },
  "ocr.workingTess": { hr: "Čitam etiketu…", en: "Reading label…" },
  "ocr.partial": { hr: "Nisam siguran — pogledaj rezultate pretrage", en: "Not sure — check the search results" },
  "ocr.noMatch": { hr: "Nema pogodaka u katalogu. Pokušaj bliže / više svjetla.", en: "No catalog match. Try closer / more light." },
  "ocr.error": { hr: "Prepoznavanje nije uspjelo.", en: "Recognition failed." },
  "ocr.modeCigar": { hr: "Jedna cigara / etiketa", en: "Single cigar / label" },
  "ocr.modeReceipt": { hr: "Račun", en: "Receipt" },
  "ocr.modeCigarShort": { hr: "Cigara", en: "Cigar" },
  "ocr.modeReceiptShort": { hr: "Račun", en: "Bill" },
  "ocr.confirmTitle": { hr: "Prepoznato", en: "Recognized" },
  "ocr.confirmHint": { hr: "Ne sprema se u Imam dok ne potvrdiš", en: "Not saved as Owned until you confirm" },
  "ocr.actionPair": { hr: "Sparivanje", en: "Pairing" },
  "ocr.actionOwned": { hr: "Označi Imam", en: "Mark as Owned" },
  "ocr.actionDetail": { hr: "Samo detalj", en: "Details only" },
  "ocr.actionWrong": { hr: "Nije to — zatvori", en: "Wrong — dismiss" },
  "ocr.receiptTitle": { hr: "Cigare na računu", en: "Cigars on receipt" },
  "ocr.receiptHint": { hr: "Provjeri popis pa unesi označene u Imam.", en: "Review the list, then add selected to Owned." },
  "ocr.receiptCommit": { hr: "Unesi sve označeno u Imam", en: "Add selected to Owned" },
  "ocr.receiptDone": { hr: "Dodano u Imam: {n}", en: "Added to Owned: {n}" },
  "common.buy": { hr: "Gdje kupiti", en: "Where to buy" },
  "common.searchOnline": { hr: "Traži online", en: "Search online" },
  "price.from": { hr: "od", en: "from" },
  "price.check": { hr: "provjeri cijenu", en: "check price" },
  "price.marketNote": {
    hr: "Cijena vrijedi za odabrano tržište. Za druga tržišta koristi gumbe za kupnju.",
    en: "Price applies to the selected market. For other markets use the buy buttons.",
  },
  "rate.qualityWhat": {
    hr: "Neovisna procjena kvalitete (1–10) unutar vlastitog stila — agregat javnih ocjena i recenzija. Dodaci se ne kažnjavaju u ocjeni, nego se zasebno deklariraju.",
    en: "Independent quality estimate (1–10) within its own style — aggregated from public ratings and reviews. Additives are not penalized in the score; they are declared separately.",
  },
  "rate.matchWhat": {
    hr: "Postotak slaganja — koliko se ovo piće i cigara slažu prema pravilima sparivanja (tijelo, okusi, pokrovni list).",
    en: "Match percentage — how well this drink and cigar fit per the pairing rules (body, flavours, wrapper).",
  },
  "rate.match": { hr: "% slaganja", en: "% match" },
  "rate.editorial": { hr: "neovisna procjena", en: "independent estimate" },
  "market.ALL": { hr: "Sve", en: "All" },
  "market.HR": { hr: "Hrvatska", en: "Croatia" },
  "market.EU": { hr: "Europa", en: "Europe" },
  "market.USA": { hr: "SAD", en: "USA" },
  "market.WW": { hr: "Svijet", en: "Worldwide" },
  "shops.title": { hr: "Trgovine", en: "Shops" },
  "shops.intro": {
    hr: "Gdje kupiti po regiji. Hrvatske trgovine imaju izravne poveznice na proizvod ondje gdje postoje; Europa i SAD vode na pretragu po nazivu (ili izravno kad postoji scrapani link).",
    en: "Where to buy by region. Croatian shops link directly to the product where available; Europe and USA link to a search by name (or direct when a scraped link exists).",
  },
  "shops.availableHere": { hr: "dostupno ovdje", en: "available here" },
  "shops.direct": { hr: "izravno", en: "direct" },
  "shops.search": { hr: "pretraga", en: "search" },
  "shops.walkIn": { hr: "na mjestu", en: "in store" },
  // opće
  "common.body": { hr: "Tijelo", en: "Body" },
  "common.strength": { hr: "Snaga", en: "Strength" },
  "common.sweetness": { hr: "Slatkoća", en: "Sweetness" },
  "common.cigar": { hr: "Cigara", en: "Cigar" },
  "common.drink": { hr: "Piće", en: "Drink" },
  "common.wrapper": { hr: "Pokrovni list", en: "Wrapper" },
  "common.quality": { hr: "Kvaliteta", en: "Quality" },
  "common.price": { hr: "Cijena", en: "Price" },
  "common.approx": { hr: "cca", en: "approx." },
  "common.minutes": { hr: "min", en: "min" },
  "common.all": { hr: "Sve", en: "All" },
  "common.serving": { hr: "Posluživanje", en: "Serving" },
  "common.lineup": { hr: "Boce u seriji", en: "Bottles in the series" },
  "common.samplerContents": { hr: "Cigare u pakiranju", en: "Cigars in the pack" },
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
  "cat.wine": { hr: "Vino", en: "Wine" },
  "cat.coffee": { hr: "Kava", en: "Coffee" },
  "cat.tequila": { hr: "Tekila", en: "Tequila" },
  "cat.digestif": { hr: "Biljni digestivi", en: "Herbal digestifs" },
  "cat.cigars": { hr: "Cigare", en: "Cigars" },
  "cat.pairWithDrink": { hr: "Upari s pićem →", en: "Pair with a drink →" },
  "cat.pairWithCigar": { hr: "Upari s cigarama →", en: "Pair with cigars →" },
  "brand.open": { hr: "Otvori marku", en: "Open brand" },
  "brand.byStrength": { hr: "Po snazi", en: "By strength" },
  "brand.byPrice": { hr: "Po cijeni", en: "By price" },
  "brand.viewAll": { hr: "Sve linije marke", en: "All lines by brand" },
  "brand.index": { hr: "Marke", en: "Brands" },
  "brand.lines": { hr: "linija", en: "lines" },
  "brand.from": { hr: "od", en: "from" },
  "brand.noneInMarket": {
    hr: "Nema linija dostupnih na odabranom tržištu. Promijeni filtar iznad.",
    en: "No lines available in the selected market. Change the filter above.",
  },
  "search.hits": { hr: "Rezultati", en: "Results" },
  "search.kindBrand": { hr: "marka", en: "brand" },
  "search.kindLine": { hr: "linija", en: "line" },
  "search.kindVitola": { hr: "vitola", en: "vitola" },
  "catalog.showMore": { hr: "Prikaži još", en: "Show more" },
  // kolekcija
  "coll.owned": { hr: "Imam", en: "Owned" },
  "coll.tried": { hr: "Probano", en: "Tried" },
  "coll.wishlist": { hr: "Lista želja", en: "Wishlist" },
  "coll.wishlistTitle": { hr: "Lista želja (za kupnju)", en: "Wishlist (to buy)" },
  "coll.onWishlist": { hr: "Na listi želja", en: "On wishlist" },
  "coll.myRating": { hr: "Moja ocjena", en: "My rating" },
  "coll.note": { hr: "Bilješka", en: "Note" },
  "coll.notePlaceholder": { hr: "Dojmovi, uz što je pasalo…", en: "Impressions, what it paired with…" },
  "coll.empty": {
    hr: "Kolekcija je prazna. Označi Probano za cigare koje pušiš drugdje, ili Imam za vitole koje imaš a još nisu u humidoru.",
    en: "Collection is empty. Mark Tried for cigars you smoke elsewhere, or Owned for vitolas you have that are not in a humidor yet.",
  },
  "coll.export": { hr: "Izvoz podataka", en: "Export data" },
  "coll.import": { hr: "Uvoz podataka", en: "Import data" },
  "coll.journal": { hr: "Dnevnik sparivanja", en: "Pairing journal" },
  "coll.journalEmpty": { hr: "Još nema zabilježenih spojeva. Nakon dobre kombinacije zabilježi je ovdje.", en: "No pairings logged yet. After a good combination, log it here." },
  "coll.addPairing": { hr: "Zabilježi spoj", en: "Log a pairing" },
  "coll.save": { hr: "Spremi", en: "Save" },
  "coll.delete": { hr: "Obriši", en: "Delete" },
  "coll.importOk": { hr: "Podaci uvezeni.", en: "Data imported." },
  "coll.importErr": { hr: "Neispravna datoteka.", en: "Invalid file." },
  "coll.stats": { hr: "u shortlistu / bez zalihe", en: "in shortlist / without stock" },
  "coll.historySection": { hr: "Probano / shortlist", en: "Tried / shortlist" },
  "coll.ownedNoStock": {
    hr: "Imam (još nije u humidoru)",
    en: "Owned (not in humidor yet)",
  },
  "coll.drinks": { hr: "Pića", en: "Drinks" },
  // humidor
  "hum.title": { hr: "Humidor", en: "Humidor" },
  "hum.tabCollection": { hr: "Kolekcija", en: "Collection" },
  "hum.tabHumidor": { hr: "Humidor", en: "Humidor" },
  "hum.tabCalendar": { hr: "Kalendar", en: "Calendar" },
  "hum.empty": {
    hr: "Još nemaš nijedan humidor. Otvori prvi i u njega slaži cigare — aplikacija onda prati koliko ih je ostalo.",
    en: "No humidor yet. Open your first one and start filling it — the app then tracks how many are left.",
  },
  "hum.add": { hr: "Novi humidor", en: "New humidor" },
  "hum.addHint": { hr: "Naziv (npr. Radni stol, Putni)", en: "Name (e.g. Desk, Travel)" },
  "hum.defaultName": { hr: "Moj humidor", en: "My humidor" },
  "hum.rename": { hr: "Preimenuj", en: "Rename" },
  "hum.remove": { hr: "Obriši humidor", en: "Delete humidor" },
  "hum.removeConfirm": {
    hr: "Obrisati ovaj humidor i cijelu njegovu zalihu?",
    en: "Delete this humidor and all of its stock?",
  },
  "hum.stock": { hr: "Stanje", en: "Stock" },
  "hum.cigarsCount": { hr: "cigara", en: "cigars" },
  "hum.stockEmpty": {
    hr: "Ovaj je humidor prazan. Otvori cigaru u katalogu i dodaj je ovamo.",
    en: "This humidor is empty. Open a cigar in the catalogue and add it here.",
  },
  "hum.addToHumidor": { hr: "U humidor", en: "To humidor" },
  "hum.inHumidor": { hr: "U humidoru", en: "In humidor" },
  "hum.pickHumidor": { hr: "Odaberi humidor", en: "Pick a humidor" },
  "hum.smokeOne": { hr: "Popušio jednu", en: "Smoked one" },
  "hum.totalPieces": { hr: "komada ukupno", en: "pieces in total" },
  "hum.lines": { hr: "linija", en: "lines" },
  "hum.calendarEmpty": {
    hr: "Nema zapisa u ovom mjesecu. Zabilježi večer sa stranice sparivanja i pojavit će se ovdje.",
    en: "No entries this month. Log an evening from the pairing screen and it will show up here.",
  },
  "hum.calendarPickDay": { hr: "Odaberi dan za detalje.", en: "Pick a day to see the details." },
  "hum.calendarDayEmpty": { hr: "Toga dana nema zapisa.", en: "Nothing logged that day." },
  "hum.today": { hr: "Danas", en: "Today" },
  "hum.prevMonth": { hr: "Prethodni mjesec", en: "Previous month" },
  "hum.nextMonth": { hr: "Sljedeći mjesec", en: "Next month" },
  "hum.entriesThisMonth": { hr: "zapisa u mjesecu", en: "entries this month" },
  "hum.quickAdd": { hr: "Brzi unos iz kolekcije", en: "Quick add from collection" },
  "hum.quickAddHint": {
    hr: "Cigare koje si označio s „Imam”, a još nisu u ovom humidoru. Dodir dodaje jednu.",
    en: "Cigars you marked as owned that are not in this humidor yet. Tap to add one.",
  },
  "hum.quickAddEmpty": {
    hr: "Sve cigare iz kolekcije već su u ovom humidoru.",
    en: "Every cigar in your collection is already in this humidor.",
  },
  "hum.quickAddNone": {
    hr: "Nijedna cigara još nije označena s „Imam”. Označi ih u katalogu i pojavit će se ovdje.",
    en: "No cigar is marked as owned yet. Mark them in the catalogue and they will show up here.",
  },
  "hum.quickAddAll": { hr: "Dodaj sve", en: "Add all" },
  "hum.quickAddShow": { hr: "Prikaži", en: "Show" },
  "hum.quickAddHide": { hr: "Sakrij", en: "Hide" },
  // shopping
  "shop.tiers": { hr: "Plan kolekcije po razinama", en: "Collection plan by tiers" },
  "shop.tier": { hr: "Razina", en: "Tier" },
  "shop.wishlistEmpty": { hr: "Lista želja zasad je prazna. Označi boce i cigare zvjezdicom (☆) na njihovim karticama i ovdje će se pojaviti zajedno s cijenama.", en: "Your wishlist is empty for now. Star (☆) bottles and cigars on their cards and they will appear here along with their prices." },
  "shop.total": { hr: "Ukupno", en: "Total" },
  "shop.share": { hr: "Podijeli ili kopiraj", en: "Share or copy" },
  "shop.copied": { hr: "Kopirano", en: "Copied" },
  "shop.wishlistNote": { hr: "Lista želja u potpunosti je tvoja: na nju ulazi samo ono što sam označiš zvjezdicom. Preporuke u nastavku ne mijenjaju je niti se ravnaju prema njoj.", en: "The wishlist is entirely yours: only items you star yourself appear on it. The recommendations below neither change it nor take it into account." },
  "shop.gaps": { hr: "Praznine u kolekciji", en: "Gaps in the collection" },
  "shop.gapsHint": { hr: "Segmenti u kojima još nemaš nijednu bocu, uz prijedlog kojom ih popuniti. Plan se sam ažurira prema onome što označiš oznakom „Imam”.", en: "Segments in which you do not yet own a single bottle, with a suggestion to fill each. The plan updates itself as you mark bottles as owned." },
  "shop.gapsDone": { hr: "Svi su segmenti pokriveni — kolekcija obuhvaća cijeli spektar. 🥃", en: "Every segment is covered — your collection spans the full spectrum. 🥃" },
  "shop.segments": { hr: "Preporuke po segmentima", en: "Recommendations by segment" },
  "shop.pickTop": { hr: "Vrh ponude", en: "Top of the range" },
  "shop.pickValue": { hr: "Najbolji omjer cijene i kvalitete", en: "Best value for money" },
  "shop.pickBudget": { hr: "Pristupačno (do 30 €)", en: "Affordable (up to €30)" },
  "shop.buffet": { hr: "Petorka za bife", en: "The buffet five" },
  "shop.buffetHint": { hr: "Pet najboljih boca koje zajedno daju presjek kategorije: iz svakoga segmenta po jedna, s najvišom ocjenom uz razuman strop cijene (120 € po boci). Boce koje već imaš preskaču se. Ova je preporuka neovisna o tvojoj listi želja — ono što je već na listi nosi oznaku ☆.", en: "The five best bottles that together cover the category: one per segment, highest rating within a sensible price cap (€120 a bottle). Bottles you already own are skipped. This recommendation is independent of your wishlist — anything already on the list is marked ☆." },
  "shop.myPlan": { hr: "Moj plan", en: "My plan" },
  "shop.tierDone": { hr: "Nabavljeno", en: "Acquired" },
  "shop.shops": { hr: "Trgovine", en: "Shops" },
  "shop.legalNote": { hr: "Internetska prodaja duhana u Hrvatskoj nije dopuštena — cijene cigara informativne su, a kupnja je moguća samo u trgovini.", en: "Online tobacco sales are not permitted in Croatia — cigar prices are indicative only, and purchases can be made solely in store." },
  // filteri
  "filter.style": { hr: "Stil", en: "Style" },
  "filter.strength": { hr: "Snaga", en: "Strength" },
  "filter.shape": { hr: "Oblik", en: "Shape" },
  "shape.robusto": { hr: "Robusto", en: "Robusto" },
  "shape.toro": { hr: "Toro", en: "Toro" },
  "shape.corona": { hr: "Corona", en: "Corona" },
  "shape.churchill": { hr: "Churchill", en: "Churchill" },
  "shape.gordo": { hr: "Gordo", en: "Gordo" },
  "shape.lancero": { hr: "Lancero", en: "Lancero" },
  "shape.figurado": { hr: "Figurado", en: "Figurado" },
  "filter.maxPrice": { hr: "Cijena do", en: "Price up to" },
  "filter.clean": { hr: "Samo čisti (bez aditiva)", en: "Clean only (no additives)" },
  "filter.wrapper": { hr: "Pokrovni list", en: "Wrapper" },
  "filter.binder": { hr: "Vezni list", en: "Binder" },
  "filter.filler": { hr: "Punjenje", en: "Filler" },
  "filter.puro": { hr: "Samo puro", en: "Puro only" },
  "leaf.wrapper": { hr: "Pokrovni list", en: "Wrapper" },
  "leaf.binder": { hr: "Vezni list", en: "Binder" },
  "leaf.filler": { hr: "Punjenje", en: "Filler" },
  "leaf.puro": { hr: "Puro", en: "Puro" },
  // sortiranje
  "sort.label": { hr: "Poredaj", en: "Sort" },
  "sort.quality": { hr: "Kvaliteta", en: "Quality" },
  "sort.price": { hr: "Cijena", en: "Price" },
  "sort.body": { hr: "Tijelo", en: "Body" },
  "sort.sweetness": { hr: "Slatkoća", en: "Sweetness" },
  "sort.strength": { hr: "Snaga", en: "Strength" },
  "sort.name": { hr: "Naziv", en: "Name" },
} satisfies Record<string, LocalizedText>;

export type StringKey = keyof typeof STRINGS;

// stilovi pića — labels
export const STYLE_LABELS: Record<string, LocalizedText> = {
  jamaica: { hr: "Jamajka (esterski)", en: "Jamaica (high ester)" },
  agricole: { hr: "Agricole", en: "Agricole" },
  cachaca: { hr: "Cachaça (Brazil)", en: "Cachaça (Brazil)" },
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
  dominican: { hr: "Dominikanska Republika", en: "Dominican Republic" },
  navy: { hr: "Navy blend", en: "Navy blend" },
  blend: { hr: "Blend (više regija)", en: "Multi-region blend" },
  panama: { hr: "Panama", en: "Panama" },
  other: { hr: "Ostalo", en: "Other" },
  spiced: { hr: "Spiced / aromatiziran", en: "Spiced / flavoured" },
  liqueur: { hr: "Liker", en: "Liqueur" },
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
  lowland: { hr: "Lowland", en: "Lowland" },
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
  "brandy-other": { hr: "Brandy", en: "Brandy" },
  vinjak: { hr: "Vinjak (HR)", en: "Vinjak (HR)" },
  calvados: { hr: "Calvados", en: "Calvados" },
  grappa: { hr: "Grappa (odležana)", en: "Grappa (aged)" },
  "espresso-dark": { hr: "Espresso (tamni)", en: "Espresso (dark)" },
  "espresso-medium": { hr: "Espresso (medium)", en: "Espresso (medium)" },
  americano: { hr: "Americano", en: "Americano" },
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
  flavored: { hr: "Aromatiziran", en: "Flavoured" },
  // vino
  "port-ruby": { hr: "Porto (ruby / LBV / vintage)", en: "Port (ruby / LBV / vintage)" },
  "port-tawny": { hr: "Porto (tawny)", en: "Port (tawny)" },
  "sherry-dry": { hr: "Sherry (fino / amontillado / oloroso)", en: "Sherry (fino / amontillado / oloroso)" },
  "sherry-sweet": { hr: "Sherry (PX / cream)", en: "Sherry (PX / cream)" },
  madeira: { hr: "Madeira", en: "Madeira" },
  prosek: { hr: "Prošek / desertno (HR)", en: "Prošek / dessert (HR)" },
  "red-full": { hr: "Crno — puno tijelo", en: "Red — full body" },
  "red-medium": { hr: "Crno — srednje tijelo", en: "Red — medium body" },
  "white-fresh": { hr: "Bijelo — svježe", en: "White — fresh" },
  "white-rich": { hr: "Bijelo — bogato (barrique)", en: "White — rich (barrique)" },
  sparkling: { hr: "Pjenušavo", en: "Sparkling" },
  "dessert-wine": { hr: "Desertno / botritis", en: "Dessert / botrytis" },
  blanco: { hr: "Blanco / plata", en: "Blanco / silver" },
  reposado: { hr: "Reposado", en: "Reposado" },
  anejo: { hr: "Añejo", en: "Añejo" },
  "extra-anejo": { hr: "Extra añejo", en: "Extra añejo" },
  "herbal-bitter-central": { hr: "Srednjoeuropski biljni biter", en: "Central European herbal bitter" },
  "herbal-bitter-italian": { hr: "Talijanski amaro", en: "Italian amaro" },
  fernet: { hr: "Fernet", en: "Fernet" },
  "herbal-monastic": { hr: "Monastički biljni", en: "Monastic herbal" },
  "herbal-saffron-yellow": { hr: "Žuti biljni (šafran)", en: "Yellow herbal (saffron)" },
  pelinkovac: { hr: "Pelinkovac", en: "Pelinkovac" },
  "specialty-botanical": { hr: "Jedinstveni botanik", en: "Specialty botanical" },
};

// hrvatska imena zemalja u podacima -> engleski prikaz
export const COUNTRY_LABELS: Record<string, string> = {
  Kuba: "Cuba",
  Nikaragva: "Nicaragua",
  "Dominikanska Republika": "Dominican Republic",
  "Dominikanska Republika / Švicarska": "Dominican Republic / Switzerland",
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
  "Velika casa, 16-18 C": "Large glass, 16–18 °C",
  "Casa za porto, 14-16 C": "Port glass, 14–16 °C",
  "Casa za sherry, 12-14 C": "Sherry glass, 12–14 °C",
  "Blago ohladjeno, 12-14 C": "Lightly chilled, 12–14 °C",
  "Ohladjeno, 8-10 C": "Chilled, 8–10 °C",
  "Dobro ohladjeno, 6-8 C": "Well chilled, 6–8 °C",
  "Mala casa, 10-12 C": "Small glass, 10–12 °C",
  "Cisti ili martini": "Neat or a martini",
  "Cisto / Sazerac koktel": "Neat / a Sazerac",
  "Cisto / daiquiri": "Neat / a daiquiri",
  "Cisto / kap vode (otvara dim)": "Neat / a drop of water (opens the smoke)",
  "Cisto / koktel": "Neat / a cocktail",
  "Cisto / lagano ohlađeno": "Neat / lightly chilled",
  "Cisto / mala kocka leda": "Neat / a small ice cube",
  "Cisto ili velika kocka leda": "Neat or a large ice cube",
  "Daiquiri / Dark'n'Stormy": "Daiquiri / Dark'n'Stormy",
  "Doppio (60 ml)": "Doppio (60 ml)",
  "Džezva, polako, uz rahat-lokum": "Cezve, slowly, with Turkish delight",
  "Espresso": "Espresso",
  "Espresso (30 ml)": "Espresso (30 ml)",
  "Espresso (30-36 ml)": "Espresso (30–36 ml)",
  "Espresso + 43/Licor, brandy ili rum": "Espresso + Licor 43, brandy or rum",
  "Espresso / cafecito sa šećerom": "Espresso / cafecito with sugar",
  "Espresso / moka / filter": "Espresso / moka / filter",
  "Filter / aeropress": "Filter / AeroPress",
  "Filter / espresso": "Filter / espresso",
  "Filter / espresso, večer": "Filter / espresso, evening",
  "Filter / french press": "Filter / French press",
  "Filter, bez mlijeka": "Filter, no milk",
  "French press / filter": "French press / filter",
  "French press, 4 min": "French press, 4 min",
  "G&T ili martini": "G&T or a martini",
  "Hladno, velika kocka leda": "Cold, a large ice cube",
  "Jutro, uz laganu cigaru": "Morning, with a mild cigar",
  "Kap vode ILI highball": "A drop of water OR a highball",
  "Koktel / RTD": "Cocktail / RTD",
  "Koktel / cola": "Cocktail / cola",
  "Macchiato": "Macchiato",
  "Moka, kućni ritual": "Moka pot, the home ritual",
  "On the rocks": "On the rocks",
  "Ristretto (20 ml)": "Ristretto (20 ml)",
  "Topao, sa šlagom": "Warm, with whipped cream",
  "V60 / aeropress": "V60 / AeroPress",
  "V60 / pour-over": "V60 / pour-over",
  "Velika kocka leda ILI kap vode": "A large ice cube OR a drop of water",
  "Čisto": "Neat",
  "Čisto / Caipirinha": "Neat / Caipirinha",
};

/** Ukloni dijakritiku radi usporedbe (Čisto ≈ Cisto). */
export function foldServingKey(s: string): string {
  return s.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
}

/**
 * Engleski prikaz serving.best iz podataka.
 * 1) točan ključ  2) dijakritika-fold cijelog stringa
 * 3) token-fallback (dijelovi razdvojeni / ili ili|ILI)
 */
export function localizeServing(serving: string, lang: Lang): string {
  if (lang !== "en") return serving;
  const exact = SERVING_LABELS[serving];
  if (exact) return exact;

  const folded = foldServingKey(serving);
  for (const [key, en] of Object.entries(SERVING_LABELS)) {
    if (foldServingKey(key) === folded) return en;
  }

  // Tokeni: "Čisto / Caipirinha", "On the rocks / kap vode", "X ili Y"
  const parts = serving.split(/\s*(?:\/|\bili\b|\bILI\b)\s*/);
  if (parts.length < 2) return serving;

  let anyHit = false;
  const translated = parts.map((part) => {
    const pExact = SERVING_LABELS[part];
    if (pExact) {
      anyHit = true;
      return pExact;
    }
    const pFold = foldServingKey(part);
    for (const [key, en] of Object.entries(SERVING_LABELS)) {
      if (foldServingKey(key) === pFold) {
        anyHit = true;
        return en;
      }
    }
    return part;
  });
  if (!anyHit) return serving;

  // Sačuvaj razdjelnik sličan originalu
  if (/\s+ILI\s+/.test(serving)) return translated.join(" OR ");
  if (/\s+ili\s+/i.test(serving)) return translated.join(" or ");
  return translated.join(" / ");
}

export const ADDITIVE_LABELS: Record<string, LocalizedText> = {
  clean: { hr: "Čist", en: "Clean" },
  low: { hr: "Vrlo nizak", en: "Very low" },
  light: { hr: "Blagi dodatak", en: "Light addition" },
  moderate: { hr: "Umjeren dodatak", en: "Moderate addition" },
  sweetened: { hr: "Dosladjen", en: "Sweetened" },
  flavored: { hr: "Aromatiziran", en: "Flavoured" },
  fortified: { hr: "Fortificirano", en: "Fortified" },
  unknown: { hr: "Nepoznato", en: "Unknown" },
};

// Neutralna pravila po kategoriji — što je zakonski dopušteno dodati.
// Informacija, ne osuda: svatko bira svoje piće, app deklarira što je unutra.
export const ADDITIVE_RULES: Record<string, LocalizedText> = {
  rum: {
    hr: "EU pravila: rum smije imati do 20 g/L dodanog šećera; iznad toga se u EU označava kao 'spirit drink'. Izmjerene vrijednosti (Systembolaget / hidrometrija / lab) navodimo kad postoje.",
    en: "EU rules: rum may contain up to 20 g/L added sugar; above that it is labelled 'spirit drink' in the EU. Measured values (Systembolaget / hydrometer / lab) are listed where available.",
  },
  whisky: {
    hr: "Whisky (EU/Scotch) ne smije biti doslađen ni aromatiziran — dopušten je samo karamel E150a za ujednačavanje boje. Aromatizirane varijante (med, jabuka…) zakonski su likeri/spirit drink, ne whisky.",
    en: "Whisky (EU/Scotch) may not be sweetened or flavoured — only E150a caramel for colour consistency is allowed. Flavoured variants (honey, apple…) are legally liqueurs/spirit drinks, not whisky.",
  },
  brandy: {
    hr: "Konjak i armagnac tradicionalno smiju sadržavati šećer, karamel E150a i boisé (infuziju hrasta), ukupno do 4% obskuracije (~15 g/L), bez obveze deklaracije na etiketi. To je dio stila, ne mana.",
    en: "Cognac and armagnac may traditionally contain sugar, E150a caramel and boisé (oak infusion), up to 4% obscuration total (~15 g/L), with no labelling requirement. It is part of the style, not a flaw.",
  },
  gin: {
    hr: "London Dry gin ne smije ništa dodati nakon destilacije (šećer ≤0,1 g/L). Ostali stilovi gina smiju biti slađeni ili aromatizirani — to se ovdje deklarira.",
    en: "London Dry gin may add nothing after distillation (sugar ≤0.1 g/L). Other gin styles may be sweetened or flavoured — declared here.",
  },
  tequila: {
    hr: "100% agave tequila ne smije biti miješana s drugim šećerima (mixto je druga kategorija). Odležavanje: blanco (neodležana/kratko), reposado (2–12 mj.), añejo (1–3 g.), extra añejo (3+ g.).",
    en: "100% agave tequila may not be blended with other sugars (mixto is a different category). Aging: blanco (unaged/brief), reposado (2–12 mo.), añejo (1–3 yr), extra añejo (3+ yr).",
  },
  wine: {
    hr: "Sulfiti su standardni dio vinarstva. Fortificirana vina (porto, sherry, madeira, prošek) imaju dodani vinski destilat; slatkoća dolazi iz grožđa ili zaustavljene fermentacije — deklariramo neutralno.",
    en: "Sulphites are a standard part of winemaking. Fortified wines (port, sherry, madeira, prošek) contain added grape spirit; sweetness comes from grapes or arrested fermentation — declared neutrally.",
  },
};

interface I18nCtx {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: StringKey) => string;
  lx: (text: LocalizedText | string | undefined | null) => string;
  cn: (country: string) => string; // ime zemlje u aktivnom jeziku
  sv: (serving: string) => string; // nacin serviranja u aktivnom jeziku
  rgn: (region: string) => string; // regija pica u aktivnom jeziku
}

const Ctx = createContext<I18nCtx>(null!);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    const resolved = resolveLang(localStorage.getItem("lang"));
    document.documentElement.lang = resolved;
    return resolved;
  });
  const setLang = (l: Lang) => {
    localStorage.setItem("lang", l);
    setLangState(l);
    document.documentElement.lang = l;
  };
  const t = (key: StringKey) => STRINGS[key][lang];
  // tolerira i obicni string — regenerirani podaci iz Excela mogu jos biti jednojezicni
  const lx = (text: LocalizedText | string | undefined | null) => {
    if (!text) return "";
    if (typeof text === "string") return text;
    return text[lang] || text.hr || text.en;
  };
  // imena zemalja i serviranja u podacima su hrvatska; na EN prevedi mapom
  const cn = (country: string) =>
    lang === "en" ? (COUNTRY_LABELS[country] ?? country) : country;
  const sv = (serving: string) => localizeServing(serving, lang);
  const rgn = (region: string) =>
    lang === "en" ? (REGION_LABELS[region] ?? region) : region;
  return (
    <Ctx.Provider value={{ lang, setLang, t, lx, cn, sv, rgn }}>{children}</Ctx.Provider>
  );
}

export const useI18n = () => useContext(Ctx);
