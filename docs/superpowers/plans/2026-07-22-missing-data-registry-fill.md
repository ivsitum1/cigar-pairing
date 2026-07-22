# Plan: popuniti Missing Data Registry — za LOKALNI Cursor agent

**Datum:** 2026-07-22
**Izvršava:** lokalni Cursor agent (veći kapacitet za dubinsko web istraživanje)
**Integracija:** Claude (deterministički engine `build-market-cigars.py`)

Sav prethodni rad (founded za 400 brendova, konsolidacija linija) je na `master`.
Nepopunjeno je konsolidirano u **`app/scripts/data/missing_founded_registry.json`**.

## Worklist

`missing_founded_registry.json` → polje **`missing`** (40 unosa). Po unosu:
`brand, cigar_count, category, country_draft, lines[], draft_has_blurb,
draft_has_source, note_en, source`.

Kategorije (`stats.by_category`):
- **`holts_or_value_closeout` (26)** — Holt's/value/closeout privatni labeli; javna godina često ne postoji.
- **`ambiguous_or_mixed_key` (8)** — katalog-ključ miješa više marki/linija (npr. „Dos" = Dos Amigos 87 + Dos Jotas; „Samana" = više linija). NEMA jedinstvene godine dok se identitet ne razriješi.
- **`researched_year_unconfirmed` (6)** — identitet poznat, godina nejasna.

## Zlatna pravila (protiv dezinformacija — OBAVEZNO)

1. **NE izmišljaj godine.** `founded` je `YYYY` ili `"—"`. Ako nakon dubinskog traženja nema pouzdanog izvora → ostaje `"—"` (to je valjan, pošten ishod).
2. Uvijek upiši **`source`** (URL) kad upisuješ godinu ili tvrdnju.
3. Prednost izvorima: brand site, Wikipedia, Cigar Aficionado, halfwheel, Cigar Journal, SEC/službene prijave, InterTabak/trade press, archive.org.

## Strategija po kategoriji

### A. `holts_or_value_closeout` (26)
Dubinski traži (Holt's povijest, trade press, forumi rec.cigars, archive.org snapshotovi kataloga). Ako je to Holt's kućni label bez javne godine → `founded: "—"`, ali **poboljšaj blurb** (što se zna: proizvođač, zemlja, tip). Ne gađaj godinu Holt'sa (1898) kao godinu labela.

### B. `ambiguous_or_mixed_key` (8) — RAZRIJEŠI IDENTITET (najveći kapacitet)
Ključ miješa marke. Za svaki:
1. Utvrdi koje su STVARNE marke pod tim ključem (iz `lines[]` + istraživanja).
2. **Ispravi `app/scripts/data/brand_dictionary.json`** da slugovi vode na PRAVU marku (razdvoji „Dos" → „Dos Amigos 87" / „Dos Jotas" itd.). Slugove nađi:
   ```
   grep -i "<ključ>" app/scripts/data/brand_dictionary.json
   ```
3. Za svaku pravu marku dodaj `new_brands_draft.json` unos (country/founded/blurb/source).
4. U registru označi razriješeno (vidi §Output). Ako je ključ ne-marka (npr. „Factory Overrun") → zabilježi da ide na izbacivanje (Claude će filtrirati).

### C. `researched_year_unconfirmed` (6)
Traži potvrdu godine iz drugog neovisnog izvora. Nema potvrde → ostaje `"—"` uz bilješku.

## Output (što i gdje pisati)

- **`app/scripts/data/new_brands_draft.json`** — `founded` (YYYY/„—"), `blurb{hr,en}`, `source`. (Zemlju engine izvodi iz cigara; možeš je popuniti informativno.)
- **`app/scripts/data/brand_dictionary.json`** — samo za §B (ispravci slug→marka).
- **`app/scripts/data/missing_founded_registry.json`** — pomakni riješene iz `missing` u `filled_this_pass` (s `brand, founded, reason`), ažuriraj `stats`.
- **NE diraj:** `cigars.json`, `brands.json`, `build-market-cigars.py`, `types.ts`, komponente, `vitola_lexicon.json`, `line_map.json`.

## Verifikacija (lokalni agent, prije commita)
- Svi JSON valjani (`ensure_ascii=False, indent=2`).
- Svaki novi `founded != "—"` ima `source`.
- 0 izmišljenih godina.
- (Nije nužno pokretati engine; ako pokreneš za probu, vrati: `git checkout HEAD -- app/src/data/cigars.json app/src/data/brands.json`.)

## Integracija (Claude, nakon agentovih commitova)
`git pull` → `cd app && python3 scripts/build-market-cigars.py --phase all` →
engine ubaci `founded`/`blurb` iz drafta i primijeni `brand_dictionary` ispravke;
1:1 brands, embargo 0, `npm test` + `tsc` + build; commit/merge. Deterministički.

## Sekundarni trak (opcionalno, isti agent, veći kapacitet)
Per-linija okusi/pairing (`line_notes.json`) je tek načet (vidi
`2026-07-21-line-quality-and-flavor-research.md` §B) — pravi kandidat za lokalni
agent: prave okusne bilješke + pairing za istaknute linije, SAMO iz poznatog
tag-vokabulara, s izvorima. Zaseban batch od gornjeg.

## Definicija gotovog
- `missing` popis smanjen; svi filani imaju `source`; 0 izmišljenih godina.
- Dvosmisleni ključevi razriješeni u `brand_dictionary.json` ili označeni za izbacivanje.
