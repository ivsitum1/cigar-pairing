# Plan: pravi katalog cigara iz svih trgovina (HR + EU + USA)

**Datum:** 2026-07-21
**Status:** predloženo — čeka mrežni pristup / Chrome kontrolu za izvršenje
**Povezano:** `app/src/data/shops.ts` (registar trgovina), `docs/shops-by-region.md`,
PR "Cigar shop links + region filter"

## Problem koji rješavamo

Trenutačni `cigars.json` (514 cigara) scrapan je **isključivo iz HR trgovina**
(`humidor.hr` + `havana-cigar-shop.com` su jedini product-link hostovi). `markets`
oznake `EU`/`USA` su gruba procjena, ne stvaran inventar:

- 66 kubanki (Cohiba, Cuaba, Fonseca…) označeno je *samo HR*, iako ih EU trgovine
  sigurno drže → EU je **podcijenjen**.
- Cigare koje EU/US trgovine imaju a HR nema (100+ po korisniku) **nisu u bazi** —
  nema izvora za njih.

Zato brojevi u panelu "Trgovine" (HR 486 / EU 297 / USA 243) nisu mjerodavni.
Cilj: **stvarna dostupnost + stvarni link po proizvodu za svaku trgovinu.**

## Trgovine (5)

| Regija | Trgovina | Host | Podrijetlo | Napomena |
|--------|----------|------|-----------|----------|
| 🇭🇷 HR | The Humidor | `humidor.hr` | scrapan | cijene po vitoli (EUR) |
| 🇭🇷 HR | Havana Cigar Shop | `havana-cigar-shop.com` | scrapan | age-gate |
| 🇪🇺 EU | CigarWorld | `cigarworld.de` | **novo** | DE, dostava EU; EUR; cookie/consent wall |
| 🇺🇸 USA | Holt's | `holts.com` | **novo** | Magento; USD; bez kubanki (embargo) |
| 🇺🇸 USA | Cigars Daily | `cigarsdaily.com` | **novo** | US ponude/recenzije; USD |

## Mehanizam scrapinga: browser-driven (Playwright + Chrome)

Proxy u web-sesiji blokira te hostove (403 CONNECT po mrežnoj politici). Rješenje:
**mrežni pristup uključen za hostove** + scraping kroz **pravi Chrome preko
Playwrighta** (rješava JS render, cookie/consent zidove, age-gate, paginaciju).

```js
// zajednički launcher — app/scripts/lib/browser.mjs
chromium.launch({ executablePath: <Chrome ili /opt/pw-browsers/chromium…>, headless: true })
```

Pravila za svaku trgovinu:
1. **Consent/age-gate:** prije prve stranice klikni cookie/18+ potvrdu (selektor po
   trgovini), spremi storage state pa reuse.
2. **Paginacija:** iteriraj katalog/kategorije dok ima sljedeće stranice; poštuj
   `?p=`/`?page=` sheme.
3. **Rate-limit:** 1–2 s razmak, retry s backoffom na 429/503; nikad paralelni bulk.
4. **Sirovi ispis:** `app/scripts/output/<shop>_catalog_raw.json` — po SKU: naziv,
   brand, linija, vitola, format (ring × dužina), cijena + valuta, **product URL**,
   država podrijetla (ako je izložena), wrapper (ako je izložen).
5. Idempotentno: re-run osvježi cijene/linkove, ne dira ručnu kalibraciju.

## Normalizacija u shemu `Cigar`

Nova skripta `app/scripts/normalize-catalog.py` (po trgovini adapter):

- **brand / line / vitola** iz naziva (postojeći parser iz `enrich-cigars.py` kao baza).
- **format** → `"{ring} x {length}mm"`; konverzija inča → mm za US trgovine.
- **cijena:** EUR izvorno (HR/EU). US (USD) → EUR uz **pinnani tečaj** (konstanta u
  skripti, dokumentirana), zapis `priceApprox: true`. Ne izmišljati kad cijene nema.
- **država podrijetla** → `country` (za embargo pravilo).
- **wrapper** kad je izložen; inače kasnije `profile-cigars.py`.

## Identitet i spajanje kroz trgovine (ključni dio)

Ista cigara iz 5 trgovina ne smije postati 5 duplikata; umjesto toga **jedan zapis,
`markets` = unija regija, link po regiji.**

- **Kanonski ključ:** `norm(brand) + norm(line) + ring×length`. Fuzzy match (token +
  ring/length tolerancija ±1) uz ručni override popis za rubne slučajeve.
- **Merge pravila:**
  - Postoji u HR bazi → dodaj regiju u `markets` + spremi EU/USA product link; **ne
    diraj** HR podatke (cijena/URL/profil ostaju HR izvor istine).
  - Ne postoji → novi zapis (EU/USA-only), s markets = regije gdje je nađen.
- **Embargo guard:** ako `country` = Kuba → `markets` smije sadržavati `EU`, **nikad
  `USA`** (ni ako neki US izvor navede); US trgovine ionako ne drže kubanke.

## Proširenje sheme: link + cijena po regiji

Trenutačno: jedan `priceUrl` + `vitolas[].url` (HR). Za stvarne EU/USA linkove:

```ts
// types.ts — dodatak na Cigar i Vitola
regionLinks?: Partial<Record<Region, { shop: string; url: string; priceEUR?: number; priceApprox?: boolean }>>;
```

- `cigarShopLinks()` prvo koristi `regionLinks[region]` (izravan product URL); tek ako
  ga nema, fallback na pretragu (postojeće ponašanje).
- `cigarPriceForMarket()` može prikazati EU/USA cijenu kad `regionLinks[region].priceEUR`
  postoji; inače ostaje `null` ("provjeri cijenu"). HR ostaje primarni izvor.
- Zadržava se kompatibilnost: HR i dalje kroz `priceUrl`/`vitolas[].url`.

## Fazni plan (ne jedan mega-PR)

| Faza | Sadržaj | Rezultat |
|------|---------|----------|
| **0** | Browser launcher + consent/age-gate handleri; probni scrape 1 kategorije po trgovini | potvrda selektora i pristupa |
| **1** | Scrape sve 3 nove trgovine → `*_catalog_raw.json` | sirovi katalozi |
| **2** | Normalizacija + matcher; **obogati postojećih 514** stvarnom EU/USA dostupnošću + linkovima (bez novih zapisa) | točni `markets` + `regionLinks` za postojeće |
| **3** | Dodaj **EU/USA-only** cigare kao nove zapise, batchano po brendu; nove marke → `brands.json` | prošireni katalog |
| **4** | Dedupe, embargo guard, cijena/valuta sanity; `npm test`; update panela "Trgovine" (stvarni brojevi) + EU/USA cijene u UI | zeleni testovi + istinit UI |

## Orkestracija

Dodati korake u `app/scripts/pipeline.py` (`--category cigars-shops`):
`scrape-cigarworld → scrape-holts → scrape-cigarsdaily → normalize-catalog →
merge-shops → dedupe-data → npm test`. Staje na prvoj grešci (postojeći uzorak).

## Testovi / integritet (dopune u `cigars.data.test.ts` + `integrity.test.ts`)

- `brands.json` 1:1 pokrivenost (nove marke moraju imati zapis).
- `markets` samo poznata tržišta; **embargo:** nijedna kubanka nema `USA`.
- `regionLinks[r].url` host odgovara trgovini te regije iz `shops.ts`.
- Gdje postoji `regionLinks` product URL, ne koristi se search fallback.
- Cijena: `priceEUR > 0`; US konverzije nose `priceApprox`.
- Bez search-only URL-ova u product poljima (postojeće pravilo prošireno na EU/USA hostove).

## Pravila (nastavak postojeće politike)

- Kanonski edit samo u `cigars.json` / `brands.json` / `shops.ts`.
- Ne izmišljati cijene ni dostupnost; product URL > search URL.
- HR podaci su izvor istine za HR; EU/USA se **dodaju**, ne prepisuju.
- Live scraping nikad u runtimeu — samo build-time skripte.
- Duhan online u HR ostaje referentno; nova regija ne mijenja HR pravni disclaimer.

## Non-goals

- Potpuni dump svih tisuća SKU-ova s EU/US trgovina — scope je brendovi iz kataloga
  + kurirana ekspanzija (Faza 3 batchano), ne beskonačan crawl.
- Real-time cijene / tečaj (pinnani tečaj + `priceApprox`).
- Mijenjanje HR-centričnog modela ocjena/profila.

## Napredak

- **Faza A — ODRAĐENO** (`app/scripts/enrich-region-links.py`): postojećih 514
  cigara obogaćeno stvarnim `regionLinks` (HR/EU/USA product URL + cijena) iz
  `cigar_unified_catalog.json` (9 336 zapisa; unija scrapa 5 trgovina, generirana
  na grani `cursor/shop-raw-catalogs-d678`). Rezultat: 402 cigare s regionLinks,
  EU dostupnost 297→404, USA 243→266, **10 embargo prekršaja popravljeno (Cuban+USA)**.
  UI (`cigarShopLinks`/`cigarPriceForMarket`/DetailSheet/cards) čita `regionLinks`
  i prikazuje izravan EU/USA link + cijenu (USD→EUR `priceApprox`). Testovi: embargo
  guard + regionLinks host guard; 130/130 zeleno. Izvor 26 MB je gitignoriran
  (regeneracija iz grane B).
  - *Poznato ograničenje:* EU/USA cijena je "od" na razini **linije** (shop nema
    uvijek točnu vitolu); link vodi na proizvod te linije u toj trgovini.
- **Faza B — ODRAĐENO** (`app/scripts/build-market-cigars.py`, deterministički +
  idempotentni engine): iz 2 513 shop-only pod postojećim brendovima admitirano uz
  strogi quality gate → **271 novih linija** (514 → 785 cigara), grupirano po
  (brend, linija) u više vitola, čist line/vitola split, embargo-safe (Habanos marke
  preskočene), profil inline (`enrich`), `regionLinks` s EU/USA cijenama. 131/131 test
  (+ market-invariant guard), tsc+build ✓. Dijeljeni: `scripts/data/vitola_lexicon.json`,
  `line_map.json`; `scripts/shop_common.py`. Held ~2 000 (no_format/no_vitola) — kandidati
  za kasniju polish preko `line_map.json`.
- **Faza C — poslije** (batchano): 5 517 pod **novim** brendovima → svaki batch
  dodaje `brands.json` metapodatke (zemlja/founded/blurb) + guard 1:1.

## Deliverables

1. Browser launcher + 3 scrape skripte (cigarworld, holts, cigarsdaily).
2. `normalize-catalog.py` + `merge-shops.py` + matcher s override popisom.
3. Shema `regionLinks` + `cigarShopLinks`/`cigarPriceForMarket` prošireni.
4. Obogaćeni + prošireni `cigars.json`/`brands.json`; embargo guard.
5. Ažuriran panel "Trgovine" sa **stvarnim** brojevima + EU/USA cijene u detalju.
6. Update `docs/shops-by-region.md` i ovog spec-a nakon svake faze.
