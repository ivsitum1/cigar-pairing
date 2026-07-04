# Cigar & Drink Pairing

PWA za sparivanje cigara i pića (rum, whisky, konjak/brandy, kava) s indeksima
rangiranim po kvaliteti za sipping uz cigaru.

**Live:** https://ivsitum1.github.io/cigar-pairing/ (instalabilno na mobitel, radi offline)

## Struktura

- `app/` — Vite + React + TS + Tailwind PWA
  - `src/data/*.json` — indeksi (136 rumova, 93 whiskyja, 41 brandy, 23 kave, 100 cigara)
  - `src/engine/` — rule-based pairing engine s objašnjenjima (kalibracija u `rules.ts`)
  - `scripts/excel-to-json.py` — regenerira rums.json + shopping.json iz lokalnog Excela
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
- Cijene pića: točni linkovi na allez.hr/ecuga.com gdje postoje (rum iz Excel
  kataloga), inače fallback na pretragu.
