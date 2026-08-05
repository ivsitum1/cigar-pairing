# Trgovine pićem u Hrvatskoj

Popis trgovina koje app koristi za **„Gdje kupiti"** kod boca. Izvor istine u
kodu je `app/src/data/drinkShops.ts`; ovaj dokument je čitljiva referenca uz
njega. Cigare imaju vlastiti registar (`app/src/data/shops.ts`,
[docs/shops-by-region.md](shops-by-region.md)) jer se duhan u HR ne prodaje
online.

## Zašto postoji

Katalog ima potvrđen link na stranicu boce za trećinu zapisa (324 od 946) i to
vrlo neravnomjerno — scrape pokriva allez/ecuga:

| Kategorija | Potvrđena stranica boce |
|------------|-------------------------|
| viski | 197 / 275 |
| digestiv | 13 / 13 |
| brendi/konjak | 34 / 90 |
| gin | 23 / 65 |
| tequila | 8 / 26 |
| rum | 47 / 320 |
| vino | 2 / 124 |
| kava | 0 / 33 |

Za sve ostale je u detalju pisalo `Trgovina: allez.hr`, a gumb je vodio na
Google — tvrdnja o dostupnosti bez pokrića. Sada app kaže **što zna, i koliko
pouzdano**.

## Tipovi poveznica

| Tip | Oznaka u appu | Znači |
|-----|---------------|-------|
| `product` | izravno | `priceUrl` je potvrđena stranica **te** boce (slug se poklapa s imenom, provjera u `lib/drinkBuyLink.ts`) |
| `search` | pretraga | trgovina ima pretragu po nazivu — link stvarno traži tu bocu, ali pogodak nije zajamčen |
| `browse` | katalog | trgovinu znamo, ali ne i njen endpoint pretrage → link vodi na katalog kategorije (nikad na izmišljen URL) |
| `ref` | provjeri cijenu | svjetski cjenik (Wine-Searcher) — orijentir za cijenu i za to drži li bocu itko |

Redoslijed u detalju boce: potvrđena stranica → trgovine s pretragom →
katalozi → svjetski cjenik. Najviše pet HR poveznica po boci.

## 🇭🇷 Hrvatska

| Trgovina | Link | Tip linka | Kategorije | Napomena |
|----------|------|-----------|------------|----------|
| allez.hr | <https://allez.hr/> | izravan (kad je boca u katalogu) / katalog | žestica | najširi online izbor u HR |
| ecuga.com | <https://ecuga.com/> | izravan (kad je boca u katalogu) / katalog | žestica | specijalist za viski i rum |
| Tipsy | <https://tipsy.hr/> | pretraga po nazivu | žestica, vino | Zagreb — dostava |
| Cugaklik | <https://www.cugaklik.hr/> | pretraga po nazivu | žestica, vino | dostava po RH |
| Roto | <https://webshop.rotodinamic.hr/> | katalog | žestica | veleprodajni webshop |
| Vrutak | <https://www.vrutak.hr/> | katalog | žestica | velik odjel u trgovini |
| Vivat fina vina | <https://www.vivat-finavina.hr/> | katalog | vino | vinoteka s webshopom |

Kava nema trgovinu u registru — ondje ostaje jedan link na web pretragu.

## 🌍 Referenca

| Servis | Link | Čemu služi |
|--------|------|------------|
| Wine-Searcher | <https://www.wine-searcher.com/> | cijene i ponuda po svijetu za žesticu i vino (`/find/ime+boce`) |

## Kako dodati trgovinu

1. Dodaj zapis u `DRINK_SHOPS` (`app/src/data/drinkShops.ts`).
2. `search` daj **samo** ako je endpoint pretrage provjeren (npr. WordPress
   `?s=`); inače `browse` po kategoriji. Pravilo je: bolje katalog nego
   izmišljen URL koji vraća 404.
3. `productHost` postavi ako scrape te trgovine puni `priceUrl` — app tada
   prepoznaje izravne linkove na proizvod i označava ih kao „izravno".
4. `npm test` (`src/lib/drinkShopLinks.test.ts` čuva pravila registra i
   redoslijed poveznica; `src/i18n/croatian.test.ts` čuva hrvatski tekst).

## Polje `shopHR`

`shopHR` u podacima o piću je **urednička napomena** o tome gdje se boca obično
nalazi (`allez.hr`, `Vrutak`, `Lidl`, `vinoteke`…), ne provjerena zaliha. U
detalju se prikazuje kao `orijentir — provjeri zalihu` osim kad ista trgovina
ima potvrđenu stranicu proizvoda. Lista želja i dalje grupira po tom polju
(`lib/shoppingPicks.ts`) — jedan odlazak u dućan = jedna grupa.
