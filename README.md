# Cigar & Drink Pairing

PWA za sparivanje cigara i pića (rum, whisky, konjak/brandy, gin, vino, kava) s
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
  - Personalizacija: ocjene iz dnevnika lokalno naginju prijedloge (±5 bodova,
    s objašnjenjem); filter prilike (jutro/poslijepodne/večer); cigare s
    heuristički izvedenim profilom nose oznaku "procijenjeni profil"
  - `src/data/*.json` — indeksi (147 rumova, 278 whiskyja, 78 brandy/grappa, 20 gin, 52 vina, 23 kave, 480 cigara)
  - `scripts/seed/whiskies_classics_seed.json` — klasici koje allez/ecuga ne drže
    (Talisker 10, Ardbeg 10, Springbank 10, bourboni…); nakon regeneracije iz
    Excela vrati ih s `python scripts/merge-extras.py`
  - `src/data/wines.json` — vino po istom principu punoće (porto, sherry,
    madeira, prošek, puna/srednja crna, bijela, pjenušava, desertna); HR cijene
    (Vivat/Miva/Vrutak/vinoteke), približne označene `priceApprox`
  - `src/engine/` — rule-based pairing engine s objašnjenjima (kalibracija u `rules.ts`)
  - **`scripts/pipeline.py` — orkestrator: vrti korake regeneracije ispravnim
    redoslijedom i staje na prvoj grešci** (`--category rum|whisky|brandy|cigars|all`,
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
  - `scripts/enrich-cigars.py` — vitole/cijene/linkovi iz humidor.hr scrape podataka
  - `scripts/profile-cigars.py` — obogaćuje cigare bez profila (prazan flavorTags →
    izvodi snagu/tijelo/wrapper/okuse iz wrappera, marke i bilješki)
  - `scripts/dedupe-data.py` — uklanja duple ID-jeve nakon regeneracije (pokreni zadnje)
  - `scripts/build-world-outline.mjs` — generira `src/data/world_outline.json`
    (monokromni atlas za Club kartu) iz Natural Earth land TopoJSON-a
  - `scripts/export-indexes.py` — generira `*_Index.xlsx` u root (git-ignorirano)
  - **Redoslijed nakon regeneracije cigara:** `enrich-cigars.py` → `profile-cigars.py`
    → `dedupe-data.py` → `npm test`
- Deploy: push na `master` → GitHub Actions → GitHub Pages

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
- Cijene pića: točni linkovi na allez.hr/ecuga.com gdje postoje (rum, whisky i brandy iz Excel
  kataloga), inače fallback na pretragu.

## Whisky indeks (pipeline)

Isti model kao rum: puni shop katalog u Excelu + kurirani **MASTER Ocjene** za app.

| Artefakt | Lokacija | Broj stavki |
|----------|----------|-------------|
| Raw scrape | `app/scripts/output/whisky_catalog_raw.json` | ~1098 |
| Excel (lokalno, git-ignorirano) | `Whisky_Kolekcija_Checklist.xlsx` | 7 sheetova |
| App JSON | `app/src/data/whiskies.json` | 170 (MASTER) |
| Export | `Whisky_Index.xlsx` | 170 |

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
| App JSON | `app/src/data/brandies.json` | 81 (MASTER) |
| Export | `Konjak_Brandy_Index.xlsx` | 81 |

**Sheetovi u Excelu:** Katalog allez+ecuga, Svi brendiji (rang), MASTER Ocjene,
Po tipu (kupnja), Serviranje + Cigare, Kolekcija (plan), Vodič (sažetak).

```powershell
cd app
python scripts/scrape-brandy-catalog.py
python scripts/build-brandy-excel.py
# ručna kalibracija MASTER / Po tipu u Excelu (po potrebi)
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
