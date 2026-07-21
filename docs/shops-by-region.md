# Trgovine cigarama po regiji

Detaljan popis trgovina koje app koristi za "gdje kupiti" linkove. Izvor istine u
kodu je `app/src/data/shops.ts`; ovaj dokument je čitljiva referenca uz njega.

Filter regije (**Sve · Hrvatska · EU · USA**) u Katalogu i Pairingu radi ovako:

- **Sve** (zadano, bez filtera) — prikazuje **sve** cigare, sortirano; u detalju
  cigare prikazuje trgovine svih regija u kojima je cigara dostupna.
- **Hrvatska / EU / USA** — filtrira popis na cigare dostupne u toj regiji i
  prikazuje **samo** trgovine te regije.

Dostupnost cigare po regiji dolazi iz `markets` polja svakog zapisa u
`app/src/data/cigars.json` (`HR` / `EU` / `USA`; `WW` = globalno dostupno).

## 🇭🇷 Hrvatska

| Trgovina | Link | Tip linka | Napomena |
|----------|------|-----------|----------|
| The Humidor | <https://humidor.hr/hr/> | izravan link na proizvod (gdje postoji) | Zagreb — cijene po vitoli |
| Havana Cigar Shop | <https://havana-cigar-shop.com/> | izravan link na proizvod (gdje postoji) | provjera dobi na ulazu |

HR trgovine imaju scrapane linkove na proizvod u katalogu, pa app vodi izravno na
stranicu te cigare kad taj link postoji (prednost ima link zadane vitole radi
sklada s prikazanom cijenom). Ako izravnog linka nema, koristi se pretraga po
nazivu. **HR cijena je jedina scrapana** i prikazuje se i u filteru "Sve".

## 🇪🇺 Europa

| Trgovina | Link | Tip linka | Napomena |
|----------|------|-----------|----------|
| CigarWorld | <https://www.cigarworld.de/en> | pretraga po nazivu | Njemačka — dostava po EU |

## 🇺🇸 USA

| Trgovina | Link | Tip linka | Napomena |
|----------|------|-----------|----------|
| Holt's | <https://www.holts.com/> | pretraga po nazivu | Philadelphia — klasična US kuća |
| Cigars Daily | <https://cigarsdaily.com/> | pretraga po nazivu | US ponude i recenzije |

EU/USA trgovine nemaju scrapane linkove po proizvodu, pa app vodi na pretragu po
`"{brand} {line}"`. Cijena se za EU/USA **ne prikazuje** (ne izmišlja se broj bez
javnog izvora).

## Dodavanje / izmjena trgovine

1. Uredi `app/src/data/shops.ts` — dodaj `Shop` zapis (regija, `home`, `search`,
   za HR i `productHost` za prepoznavanje izravnih linkova) ili izmijeni postojeći.
2. Ažuriraj ovu tablicu.
3. `cd app && npm test` — testovi u `src/data/cigars.data.test.ts` provjeravaju da
   linkovi po regiji vode na točne trgovine.
