# Plan: istraživanje brend-metapodataka (founded + priča) — za Cursor agenta

**Datum:** 2026-07-21
**Vlasnik izvršenja:** Cursor (ima web pristup)
**Integracija:** Claude (deterministički engine `build-market-cigars.py`)

## Problem

~248 novih shop-brendova (iz Faze C) u `brands.json` imaju **`founded: "—"`** i
generički blurb („marka iz kataloga trgovina"). Korisnik želi znati je li brend
osnovan „prije 2 ili 72 godine" i kratku priču. Scrape te podatke NEMA → treba
istražiti na webu. **Izmišljanje godina = dezinformacija → zabranjeno.**

## Što se puni

Datoteka: **`app/scripts/data/new_brands_draft.json`** (Cursor je vlasnik).
Po brendu (ključ = kanonski brend, isti kao u `brands.json`):

```jsonc
"Nat Sherman": {
  "country": "…",              // ostaje; engine ionako izvodi zemlju iz cigara
  "founded": "1930",           // godina (string) ILI "—" ako nije pouzdano nađeno
  "blurb": {
    "hr": "Njujorška kuća osnovana 1930.; poznata po … (1–2 rečenice, neutralno).",
    "en": "New York house founded 1930; known for … (1–2 sentences, neutral)."
  },
  "source": "https://…"        // URL izvora (za reviziju; engine ga IGNORIRA)
}
```

## Worklist (koje brendove istražiti)

Točan popis = brendovi u `app/src/data/brands.json` s **`founded == "—"`** (to su novi
shop-brendovi; ~248). Cursor:
```
python3 -c "import json;print('\n'.join(b for b,v in json.load(open('app/src/data/brands.json')).items() if v.get('founded')=='—'))"
```
Sortiraj po prominentnosti/broju cigara (više cigara u katalogu = viši prioritet).

## Pravila (protiv dezinformacija — OBAVEZNO)

1. Samo iz **pouzdanih izvora**: službeni brand site, Wikipedia, Cigar Aficionado,
   halfwheel, Cigar Journal, Bezirksregierung/registri. Uvijek upiši `source`.
2. Ako godina osnutka nije pouzdano nađena → **`founded: "—"`** (NE nagađati, ne
   zaokruživati „otprilike").
3. `blurb`: 1–2 rečenice, **činjenično i neutralno**, ne kopirati marketing doslovno;
   HR + EN. Ako se ne nađe ništa konkretno → kratki neutralni opis iz poznatog
   (zemlja, tip pogona/blendera), bez izmišljenih tvrdnji.
4. Ne mijenjati `country` po draftu (engine izvodi zemlju iz cigara); popuni ga
   informativno ako želiš, ali zna se da ga engine preskače.
5. Kubanske marke se ne pojavljuju ovdje (preskočene u pipelineu) — ako naiđeš,
   preskoči.

## Batch

Po batchu 20–40 brendova, redom po prioritetu. Nakon svakog batcha: JSON valjan,
commit **samo** `new_brands_draft.json`, javi. Ne sve odjednom.

## Faze (prioritet)

1. **`founded`** — najlakše provjerljivo, korisnik ga izričito traži.
2. **`blurb`** — kratka priča/kontekst.
3. *(opcionalno, kasnija faza)* per-line kratki hint za najpoznatije linije —
   zaseban plan; NE sada.

## Ne diraj

`cigars.json`, `brands.json`, `build-market-cigars.py`, `types.ts`, komponente,
`vitola_lexicon.json`, `line_map.json`, `brand_dictionary.json`. **Samo**
`new_brands_draft.json`.

## Verifikacija (Cursor, prije commita)

- `python3 -c "import json;json.load(open('app/scripts/data/new_brands_draft.json'))"` prolazi.
- Svaki dirani unos ima `source` **ili** `founded == "—"`.
- `founded` je 4-znamenkasta godina ili „—" (bez „~", „19xx", raspon).
- `npm test` (ako pokreneš engine za probu, vrati podatke: `git checkout HEAD -- app/src/data/cigars.json app/src/data/brands.json`).

## Integracija (Claude, nakon Cursorovih batcheva)

1. `git pull` (povuče ažurirani `new_brands_draft.json`).
2. `cd app && python3 scripts/build-market-cigars.py --phase all` — engine merge-a
   `founded`+`blurb` iz drafta u `brands.json` (zemlja iz cigara; `source` ignoriran).
3. Provjera: brands 1:1, nijedan `founded` osim „—"/godine, `npm test` + `tsc` + build.
4. Commit + merge. Deterministički — isti draft daje identičan `brands.json`.

## Definicija gotovog (po batchu)

- Dirani brendovi imaju `founded` (godina ili „—") + neutralni `blurb` + `source`.
- 0 izmišljenih godina; sve provjerljivo preko `source`.
