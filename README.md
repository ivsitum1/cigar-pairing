# Cigar & Drink Pairing

PWA za sparivanje cigara i pića (rum, whisky, konjak/brandy, kava) s indeksima
rangiranim po kvaliteti za sipping uz cigaru.

**Live:** https://ivsitum1.github.io/cigar-pairing/ (instalabilno na mobitel, radi offline)

## Struktura

- `app/` — Vite + React + TS + Tailwind PWA
  - `src/data/*.json` — indeksi (136 rumova, 170 whiskyja, 81 brandy, 23 kave, 100 cigara)
  - `src/engine/` — rule-based pairing engine s objašnjenjima (kalibracija u `rules.ts`)
  - `scripts/excel-to-json.py` — regenerira rums.json + shopping.json iz lokalnog Excela
  - `scripts/scrape-whisky-catalog.py` — scrape allez.hr + ecuga.com → whisky_catalog_raw.json
  - `scripts/build-whisky-excel.py` — gradi Whisky_Kolekcija_Checklist.xlsx iz raw kataloga
  - `scripts/excel-to-whisky-json.py` — regenerira whiskies.json iz whisky Excela
  - `scripts/scrape-brandy-catalog.py` — scrape allez.hr + ecuga.com → brandy_catalog_raw.json
  - `scripts/build-brandy-excel.py` — gradi Konjak_Brandy_Checklist.xlsx iz raw kataloga
  - `scripts/excel-to-brandy-json.py` — regenerira brandies.json iz brandy Excela
  - `scripts/enrich-cigars.py` — vitole/cijene/linkovi iz humidor.hr scrape podataka
  - `scripts/export-indexes.py` — generira `*_Index.xlsx` u root (git-ignorirano)
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
python scripts/export-indexes.py           # Whisky_Index.xlsx
npm test
```

Izvori: [allez.hr/shop/whiskey](https://allez.hr/shop/whiskey),
[ecuga.com/katalog/whisky](https://ecuga.com/katalog/whisky) (+ podkategorije).
Flavoured/RTD stavke ostaju u katalogu, ali ne ulaze u MASTER/app (`pairable: false`).

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
Grappa/pisco/absinthe/likeri ostaju u katalogu, ali ne ulaze u MASTER/app (`pairable: false`).
HR vinjak (Badel itd.) zadržava se iz seed datoteke i može ostati bez shop linka.
