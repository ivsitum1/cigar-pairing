# Cigar & Drink Pairing

PWA za sparivanje cigara i pića (rum, whisky, konjak/brandy, gin, vino, tequila, kava) s
indeksima rangiranim po kvaliteti za sipping uz cigaru.

**Live:** https://ivsitum1.github.io/cigar-pairing/ (instalabilno na mobitel, radi offline)

## Uređivačka politika: neutralno i informativno

- **Deklaracija umjesto osude.** Sve što ima dodatke ostaje na popisu; app
  jasno navodi *što* je dodano i *koliko* (izmjerene vrijednosti g/L gdje
  postoji javni izvor: Systembolaget/Alko lab, hidrometrijski testovi).
- **Ocjena unutar stila.** `qualityScore` je neovisna procjena unutar vlastite
  kategorije (agregat javnih ocjena i recenzija) — dodaci se ne kažnjavaju u
  ocjeni, nego se transparentno deklariraju.
- **Sve je pairable.** Engine pošteno boduje spoj po tijelu/slatkoći/okusima;
  korisnik bira što voli.
- **Različita pravila po kategoriji** (prikazano u appu): rum EU ≤20 g/L
  šećera; whisky bez doslađivanja (samo E150a); konjak/armagnac šećer + E150a
  + boisé do 4% obskuracije; London Dry gin ništa nakon destilacije; vino
  sulfiti standard, fortificirana vina dodani destilat.
- Neutralne izmjene tona čuvaju se u `app/scripts/neutral_overrides.json` i
  primjenjuju s `python scripts/apply-neutral-overrides.py` (pokrenuti nakon
  svake regeneracije iz Excela).

## Struktura

- `app/` — Vite + React + TS + Tailwind PWA
  - Hash-routing s deep-linkovima: `#/pairing/cigar/<id>` i `#/pairing/drink/<id>`
    otvaraju pairing s odabranom stavkom (dijeljivi linkovi, back tipka radi)
  - `src/data/*.json` — indeksi (321 rum, 275 whiskyja, 101 brandy/grappa, 70 gin,
    124 vina, 26 tequila, 33 kave, 13 digestiva, 3701 cigara);
    build ih dijeli u odvojene chunkove (`data-cigars`, `data-whiskies`, `data-rums`…) radi
    paralelnog downloada i boljeg cachea
  - **ID-jevi se nikad ne brišu.** Kolekcija i dnevnik žive u `localStorage` i
    ključaju na te ID-jeve, pa uklonjen zapis tiho osiroti korisnikove oznake.
    Kad se linija preimenuje ili razdvoji, nasljednik ide u `drinkIdAliases.json`
    odnosno `cigarIdAliases.json`; `drinkIdRegistry.json` + testovi to čuvaju
  - Personalizacija: ocjene iz dnevnika lokalno naginju prijedloge (±5 bodova,
    s objašnjenjem); filter prilike (jutro/poslijepodne/večer); s pairing rezultata
    **Zabilježi večer** sprema spoj u dnevnik i može označiti stavke kao probane;
    cigare s heuristički izvedenim profilom nose oznaku "procijenjeni profil"
  - `scripts/seed/whiskies_classics_seed.json` — klasici koje allez/ecuga ne drže
    (Talisker 10, Ardbeg 10, Springbank 10, bourboni…); nakon regeneracije iz
    Excela vrati ih s `python scripts/merge-extras.py`
  - `src/data/wines.json` — vino po istom principu punoće (porto, sherry,
    madeira, prošek, puna/srednja crna, bijela, pjenušava, desertna); HR cijene
    (Vivat/Miva/Vrutak/vinoteke), približne označene `priceApprox` (124 zapisa;
    regeneracija: `python scripts/expand-wines.py`)
  - `src/engine/` — rule-based pairing engine s objašnjenjima (kalibracija u `rules.ts`)
  - **`scripts/pipeline.py` — orkestrator: vrti korake regeneracije ispravnim
    redoslijedom i staje na prvoj grešci** (`--category rum|whisky|brandy|gin|tequila|cigars|all`,
    `--scrape` za osvježenje kataloga, `--from <skripta>` za nastavak nakon ručne
    kalibracije Excela, `--list` za pregled koraka); ručno nabrajanje ispod ostaje
    kao referenca
  - `scripts/excel-to-json.py` — regenerira rums.json + shopping.json iz lokalnog Excela
  - `scripts/export-serve-corrections.py` + `scripts/fix-excel-data.py` — ispravni podaci za Excel Serviranje + Cigare
  - `scripts/scrape-whisky-catalog.py` — scrape allez.hr + ecuga.com → whisky_catalog_raw.json
  - `scripts/build-whisky-excel.py` — gradi Whisky_Kolekcija_Checklist.xlsx iz raw kataloga
  - `scripts/excel-to-whisky-json.py` — regenerira whiskies.json iz whisky Excela
  - `scripts/scrape-brandy-catalog.py` — scrape allez.hr + ecuga.com → brandy_catalog_raw.json
  - `scripts/build-brandy-excel.py` — gradi Konjak_Brandy_Checklist.xlsx iz raw kataloga
  - `scripts/excel-to-brandy-json.py` — regenerira brandies.json iz brandy Excela
  - `scripts/scrape-gin-catalog.py` / `build-gin-excel.py` / `excel-to-gin-json.py` — gin pipeline
  - `scripts/scrape-tequila-catalog.py` / `build-tequila-excel.py` / `excel-to-tequila-json.py` — tequila pipeline
  - `scripts/calibrate-master.py` — agent kalibracija MASTER sheetova (gin/tequila/brandy)
  - `scripts/enrich-cigars.py` — vitole/cijene/linkovi iz humidor.hr scrape podataka
  - `scripts/profile-cigars.py` — obogaćuje cigare bez profila (prazan flavorTags →
    izvodi snagu/tijelo/wrapper/okuse iz wrappera, marke i bilješki)
  - `scripts/dedupe-data.py` — uklanja duple ID-jeve nakon regeneracije (pokreni zadnje)
  - `scripts/build-world-outline.mjs` — generira `src/data/world_outline.json`
    (monokromni atlas za Club kartu) iz Natural Earth land TopoJSON-a
  - `scripts/export-indexes.py` — generira `*_Index.xlsx` u root (git-ignorirano)
  - **Redoslijed nakon regeneracije cigara:** `enrich-cigars.py` → `profile-cigars.py`
    → `dedupe-data.py` → `npm test`
  - **Club** (`src/pages/ClubPage.tsx`) — citat dana, činjenice, kviz, karta zemalja + urednički slojevi (redoslijed na indexu):
    1. **101** (`club101.json`) — kurikulum: cigare, pića, pribor, savjeti (33 lekcije u 4 trake)
    2. **Leksikon** (`lexicon.json`) — jezik degustacije i pairing mostova (9 unosa, uklj. gin-koktel most)
    3. **HR vodič** (`hrGuide.json`) — kupnja i dostupnost u HR (7 poglavlja)
    4. **Arhetipovi** (`eveningArchetypes.json`) — stilske slike večeri (6 eseja)
    5. **Bonton** (`bonton.json`) — manire za stol (10 poglavlja; rukopis se ne rewrita u rolloutu)
    - Rotirajući sadržaj: `club.json` (83 činjenice, 80 kviz pitanja)
    - **Kupi vs Traži online:** `src/lib/drinkBuyLink.ts` prikazuje **Kupi** samo kad URL izgleda kao stranica *tog* proizvoda (slug↔ime, bez kategorijskih `/katalog/` linkova); inače **Traži online**. Root cause fuzzy matcha u pipelineu dokumentiran u `docs/superpowers/plans/2026-07-17-content-rollout.md` (Task 0 runtime safeguard; Task 1b stroži match kasnije).
    - **Redoslijed content valova** (kurirane bilješke + `cigarHint` u katalogu): rum MASTER → whisky klasici → fortificirana vina/sherry → brandy/XO i HR vinjak → cigare s `profileEstimated` (vidi brainstorm spec).
- **OCR** (`src/lib/ocrEngine.ts`, `components/OcrScan.tsx`) — fotografiraj
  etiketu/prsten ili račun: `tesseract.js` za etikete, `@paddleocr/paddleocr-js`
  za račune (bolji na termalnim tablicama), pa `lib/receiptParse.ts` složi
  stavke u batch „Imam".
  - OCR bundle je **lazy** (~10,9 MB) — povuče se tek na prvu upotrebu, nije u
    prvom učitavanju ni u SW precacheu. Modeli se dohvaćaju s jsDelivr /
    HuggingFace / ModelScope i keširaju (`ocr-models`, CacheFirst, 30 dana) —
    app je offline-first za vlastite podatke, ali ne i za OCR modele.
- `backend/` — **neobavezan lokalni FastAPI servis** (port 8787) za jači OCR
  računa (PaddleOCR) i vizualno prepoznavanje prstena cigare. Nije dio deploya:
  PWA ga zove samo ako je postavljen `VITE_OCR_API_URL`; bez toga (zadano na
  GitHub Pagesu) koristi ugrađeni paddleocr-js. Vidi `backend/README.md`.
- `app/android/` — Capacitor Android shell (APK) oko istog bundlea; vidi
  **[Android APK](docs/android-apk.md)** (grana `release/android`)
- Deploy: push na `master` → GitHub Actions → GitHub Pages

## Android APK (u izradi)

Uz PWA, isti kod se pakira i kao Android app kroz **Capacitor**. Dva build
targeta iz istog izvora: `npm run build` (Pages, base `/cigar-pairing/`, service
worker) i `npm run build:native` (WebView, relativni base, bez SW).

```powershell
cd app
npm run android:sync     # build:native + cap sync android
npm run android:open     # Android Studio (traži JDK 21 + Android SDK)
```

Debug APK se gradi i u CI-u (`.github/workflows/android.yml`) i skida kao
artefakt run-a. Potpisani release i Play Store još nisu napravljeni — detalji,
odluke i preostali koraci u [`docs/android-apk.md`](docs/android-apk.md).

## Podaci o kolekciji (imam / probao / ocjene / dnevnik)

Spremaju se **lokalno u pregledniku** (localStorage), po uređaju. Backup:
Kolekcija → Export/Import JSON. Nema accounta ni slanja podataka ikamo.

### Plan za kasnije: cloud sync (faza 2)

Kad zatreba sync mobitel ↔ računalo:

1. Supabase free projekt (EU regija), tablica `collections(user_id uuid pk, data jsonb, updated_at)`.
2. Auth: e-mail magic link (`@supabase/supabase-js`), bez lozinki.
3. `store/collection.ts` dobiva sync sloj: localStorage ostaje offline cache
   (source of truth offline), push na svaku promjenu (debounce), pull + merge
   (last-write-wins po stavki) na login/fokus.
4. UI: sekcija "Račun" na stranici Kolekcija (prijava/odjava/status syncanja).
5. Export/Import ostaje kao backup neovisan o cloudu.

## Napomene

- Online prodaja duhana u HR nije dozvoljena — linkovi na cigare su referentni
  (humidor.hr prikazuje cijene po vitoli; havana-cigar-shop.com ima age-gate).
- **Trgovine po regiji** (`app/src/data/shops.ts` — jedini izvor istine):
  HR = The Humidor + Havana Cigar Shop; EU = CigarWorld (cigarworld.de/en);
  USA = Holt's + Cigars Daily. Filter u Katalogu/Pairingu (**Sve · HR · EU · USA**;
  zadano **Sve** = bez filtera → sve cigare, sortirano) mijenja i popis cigara i
  prikazane trgovine. Detalj cigare grupira linkove po regiji; HR daje izravan link
  na proizvod gdje postoji, EU/USA vode na pretragu po nazivu. HR cijena je jedina
  scrapana pa se prikazuje i u "Sve"; EU/USA nemaju cijenu (ne izmišlja se broj).
  Detaljan popis: **Katalog → Trgovine** (`docs/shops-by-region.md`).
- Cijene pića: točni linkovi na allez.hr/ecuga.com gdje postoje (rum, whisky i brandy iz Excel
  kataloga), inače fallback na pretragu. **„Gdje kupiti”** prikazuje izravni shop link samo kad
  URL izgleda kao stranica *tog* proizvoda; inače „Traži online” (fuzzy match kataloga inače
  često veže krivi SKU ili kategoriju — to je posebno vidljivo u Shopping → Praznine).
- **Trgovine pićem** (`app/src/data/drinkShops.ts` — jedini izvor istine): potvrđenu stranicu
  boce ima trećina zapisa (313/963; vino 2/124, rum 42/321), pa detalj boce više ne nudi samo
  Google. Redoslijed: potvrđena stranica (*izravno*) → HR trgovine s pretragom po nazivu
  (Tipsy, Cugaklik) → katalozi (allez.hr, ecuga.com, Roto, Vrutak, Vivat) → Wine-Searcher kao
  svjetski cjenik. Trgovina bez provjerenog endpointa pretrage dobiva link na katalog
  kategorije — URL se **ne izmišlja**. `shopHR` je urednička napomena, pa se prikazuje kao
  „orijentir — provjeri zalihu” osim kad ista trgovina ima potvrđenu stranicu proizvoda.
  Detaljno: **[docs/drink-shops-hr.md](docs/drink-shops-hr.md)**.

## Whisky indeks (pipeline)

Isti model kao rum: puni shop katalog u Excelu + kurirani **MASTER Ocjene** za app.

| Artefakt | Lokacija | Broj stavki |
|----------|----------|-------------|
| Raw scrape | `app/scripts/output/whisky_catalog_raw.json` | ~1098 |
| Excel (lokalno, git-ignorirano) | `Whisky_Kolekcija_Checklist.xlsx` | 7 sheetova |
| App JSON | `app/src/data/whiskies.json` | 278 (MASTER) |
| Export | `Whisky_Index.xlsx` | 278 |

**Sheetovi u Excelu:** Katalog allez+ecuga, Svi viskiji (rang), MASTER Ocjene,
Po tipu (kupnja), Serviranje + Cigare, Kolekcija (plan), Vodič (sažetak).

```powershell
cd app
python scripts/scrape-whisky-catalog.py    # osvježi allez + ecuga katalog
python scripts/build-whisky-excel.py       # gradi/ažurira Whisky_Kolekcija_Checklist.xlsx
# ručna kalibracija MASTER / Po tipu u Excelu (po potrebi)
python scripts/excel-to-whisky-json.py     # regenerira whiskies.json
python scripts/merge-extras.py             # vrati seed dodatke (klasici, grappe)
python scripts/apply-neutral-overrides.py  # neutralni ton + splitovi
python scripts/localize-detail-fields.py   # dvojezicni additiveDetail/cigarHint
python scripts/export-indexes.py           # Whisky_Index.xlsx
npm test
```

Izvori: [allez.hr/shop/whiskey](https://allez.hr/shop/whiskey),
[ecuga.com/katalog/whisky](https://ecuga.com/katalog/whisky) (+ podkategorije).
Flavoured stavke ulaze u app s jasnom deklaracijom (liker/spirit drink) i
ocjenom unutar vlastitog stila — vidi Uređivačka politika.

## Brandy indeks (pipeline)

Isti model kao rum/whisky: puni shop katalog u Excelu + kurirani **MASTER Ocjene** za app.

| Artefakt | Lokacija | Broj stavki |
|----------|----------|-------------|
| Raw scrape | `app/scripts/output/brandy_catalog_raw.json` | ~128 |
| Excel (lokalno, git-ignorirano) | `Konjak_Brandy_Checklist.xlsx` | 7 sheetova |
| Seed (ručne ocjene) | `app/scripts/seed/brandies_seed.json` | 41 |
| App JSON | `app/src/data/brandies.json` | 84 (MASTER) |
| Export | `Konjak_Brandy_Index.xlsx` | 84 |

**Sheetovi u Excelu:** Katalog allez+ecuga, Svi brendiji (rang), MASTER Ocjene,
Po tipu (kupnja), Serviranje + Cigare, Kolekcija (plan), Vodič (sažetak).

```powershell
cd app
python scripts/pipeline.py --category brandy --scrape
# ili korak po korak:
python scripts/scrape-brandy-catalog.py
python scripts/build-brandy-excel.py
python scripts/calibrate-master.py --category brandy
python scripts/excel-to-brandy-json.py
python scripts/export-indexes.py
npm test
```

Izvori: [allez.hr/shop/cognac-calvados-armagnac](https://allez.hr/shop/cognac-calvados-armagnac),
[allez.hr/shop/absinthe-brandy-grappa-sake](https://allez.hr/shop/absinthe-brandy-grappa-sake),
[ecuga.com/katalog/spirits-and-liqueurs/cognac](https://ecuga.com/katalog/spirits-and-liqueurs/cognac).
Grappa/pisco/absinthe/likeri koji uđu u app nose jasnu deklaraciju kategorije
i neutralnu ocjenu unutar vlastitog stila.
HR vinjak (Badel itd.) zadržava se iz seed datoteke i može ostati bez shop linka.

## Gin indeks (pipeline)

Isti model: scrape allez+ecuga → Excel MASTER → agent kalibracija → `gins.json` (merge sa seedom).

```powershell
cd app
python scripts/pipeline.py --category gin --scrape
```

Izvor: [allez.hr/shop/gin1](https://allez.hr/shop/gin1). Flavoured/pink/sloe/RTD ostaju u Katalogu, ne u MASTER-u.

## Tequila indeks (pipeline)

```powershell
cd app
python scripts/pipeline.py --category tequila --scrape
```

Izvor: [allez.hr/shop/tequila-mezcal](https://allez.hr/shop/tequila-mezcal).
Mixto/aromatizirano van MASTER-a; mezcal u MASTER samo uz quality ≥ 7.
