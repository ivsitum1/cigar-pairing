# Trgovine cigarama po regiji

Detaljan popis trgovina koje app koristi za "gdje kupiti" linkove. Izvor istine u
kodu je `app/src/data/shops.ts`; ovaj dokument je čitljiva referenca uz njega.

Filter regije (**Sve · Hrvatska · Europa · USA**) u Katalogu i Pairingu radi ovako:

- **Sve** (zadano, bez filtera) — prikazuje **sve** cigare, sortirano; u detalju
  cigare prikazuje trgovine svih regija u kojima je cigara dostupna.
- **Hrvatska / Europa / USA** — filtrira popis na cigare dostupne u toj regiji i
  prikazuje **samo** trgovine te regije.

Dostupnost cigare po regiji dolazi iz `markets` polja svakog zapisa u
`app/src/data/cigars.json` (`HR` / `EU` / `USA`; `WW` = globalno dostupno).

## 🇭🇷 Hrvatska

| Trgovina | Link | Tip linka | Napomena |
|----------|------|-----------|----------|
| The Humidor | <https://humidor.hr/hr/> | izravan link na proizvod (gdje postoji) | Zagreb — cijene po vitoli |
| Havana Cigar Shop | <https://havana-cigar-shop.com/> | izravan link na proizvod (gdje postoji) | provjera dobi na ulazu |
| Tobacco Petica (Branimir) | <https://www.branimir.hr/minglanje/trgovine/tobacco-petica> | bez linka po proizvodu (`walkIn`) | Zagreb, Branimir centar — kupnja na mjestu |
| Aficionado | <https://www.aficionado.hr/> | bez linka po proizvodu (`walkIn`) | Zagreb — kupnja na mjestu |

Prve dvije trgovine imaju scrapane linkove na proizvod u katalogu, pa app vodi
izravno na stranicu te cigare kad taj link postoji (prednost ima link zadane
vitole radi sklada s prikazanom cijenom). Ako izravnog linka nema, koristi se
pretraga po nazivu. **HR cijena je jedina scrapana** i prikazuje se i u filteru
"Sve".

Trgovina bez web kataloga nosi `walkIn: true`: pojavljuje se u popisu trgovina i
može stajati u `availabilityHR`, ali **ne** dobiva link po proizvodu — pretraga
po nazivu na stranici koja nema katalog vodi u prazno.

## 🇪🇺 Europa

| Trgovina | Link | Tip linka | Napomena |
|----------|------|-----------|----------|
| CigarWorld | <https://www.cigarworld.de/en> | izravan / pretraga | Njemačka — dostava po Europi |
| C.Gars Ltd | <https://www.cgarsltd.co.uk/> | izravan / pretraga | UK — najveći online specijalist (EMS Havana) |
| La Couronne | <https://cigarpassion.ch/en/> | izravan / pretraga | Švicarska — ekskluzivni Habanos uvoznik |

UK i Švicarska nisu EU države, ali u app filteru ulaze u regiju **Europa**
zajedno s CigarWorldom — interni kod marketa ostaje `EU`.
## 🇺🇸 USA

| Trgovina | Link | Tip linka | Napomena |
|----------|------|-----------|----------|
| Holt's | <https://www.holts.com/> | listing / pretraga | Philadelphia — klasična US kuća |
| Cigars Daily | <https://cigarsdaily.com/> | izravan / pretraga | US ponude i recenzije |
| Famous Smoke | <https://www.famous-smoke.com/> | izravan / pretraga | Pennsylvania — velik katalog |
| Neptune Cigar | <https://www.neptunecigar.com/> | izravan / pretraga | Florida — online + ducani |

Kad postoji `regionLinks.USA` ili product URL na poznatom `productHost`, app vodi
izravno na proizvod; inače na pretragu `"{brand} {line}"`. EU/USA cijena se
prikazuje samo kad je scrapana (`regionLinks.*.priceEUR`), inače `null`.

## Dodavanje / izmjena trgovine

1. Uredi `app/src/data/shops.ts` — dodaj `Shop` zapis (regija, `home`, `search`,
   za HR i `productHost` za prepoznavanje izravnih linkova) ili izmijeni postojeći.
2. Ažuriraj ovu tablicu.
3. `cd app && npm test` — testovi u `src/data/cigars.data.test.ts` provjeravaju da
   linkovi po regiji vode na točne trgovine.
