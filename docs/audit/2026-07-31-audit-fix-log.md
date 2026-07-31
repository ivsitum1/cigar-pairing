# Audit i popravci — 31.07.2026.

Evidencija promjena iz auditа repozitorija na `origin/master @ cb25c52`.
Svaki val je **zaseban commit** pa se može vratiti pojedinačno s
`git revert <sha>` bez diranja ostalih.

Baseline prije zahvata: `tsc` čist, **424 testa prolaze**, deploy zelen.

---

## Val 1 — tihi gubitak korisničkih podataka (ID-jevi pića)

### Nalaz

Kolekcija i dnevnik žive u `localStorage` na uređaju i drže **ID-jeve pića**.
Kad se zapis ukloni ili preimenuje, ništa ne preusmjeri stari ID:

- **Kolekcija** — `CollectionPage` filtrira `drinkById(id) != null`, pa stavka
  sa starim ID-em **tiho nestane iz sučelja**. Oznaka Imam, ocjena i bilješka
  ostanu u `localStorage`, ali su nedostupne.
- **Dnevnik** — umjesto imena pića prikaže se **goli ID**
  (`rum-flor-de-cana-12-18`).
- **Personalizacija** — `drinkById(j.drinkId)?.style` vrati `undefined`, pa
  ocijenjena večer prestane doprinositi profilu ukusa.

Cigare su od ovoga zaštićene (`cigarIdAliases.json` + `resolveCigarId` +
`canonicalCigarItemId`), **pića nisu imala ništa**.

Mjerenje kroz cijelu povijest `master` grane — **50 trajno nestalih ID-jeva**
kroz 5 događaja, dakle ponavljajući obrazac, ne jednokratni propust:

| commit | datoteka | nestalo |
|---|---|---|
| `4b868eb` | brandies | 4 |
| `1c4c7ed` | rums / whiskies / brandies | 26 / 2 / 6 |
| `6b9b10d` | rums | 12 |

> Napomena: sadržajno su te izmjene bile **poboljšanje** — nejasni skupni unosi
> („Flor de Cana 12/18", „Compagnie des Indes (razne)") zamijenjeni su
> konkretnim bocama. Problem nije katalog, nego što se korisnikov trag nije
> preselio s njima.

### Popravak

| Datoteka | Promjena |
|---|---|
| `app/src/data/drinkIdAliases.json` | **nova** — 50 mapiranja stari → aktualni ID |
| `app/src/data/drinkIdRegistry.json` | **nova** — 1013 ID-jeva ikad isporučenih |
| `app/src/data/index.ts` | `drinkById` prati aliase; novi `canonicalDrinkId` |
| `app/src/store/collection.ts` | `remapCollectionAliases` seli i ID-jeve pića (stavke + `journal.drinkId`) |
| `app/src/data/drinkIds.test.ts` | **nov** — 5 čuvara |
| `app/src/store/collection.test.ts` | +4 testa migracije |

**Pravilo mapiranja:** kombinirani unos `A / B` vodi na **prvu imenovanu
polovicu** (`Flor de Cana 12/18` → `rum-flor-de-cana-12`). Fragment bez marke
vodi na bocu iz koje je nastao (`rum-7` → `rum-banks-7-golden-age`).
19 mapiranja ručno je provjereno jer je automatsko podudaranje po imenu
promašilo — npr. `Bacardi 8 / 10 Gran Reserva` je pogodilo *Eminente Gran
Reserva 10* (tuđa marka), ispravljeno na `rum-bacardi-8`.

**Migracija ne briše ono što ne razumije:** nepoznat ID ostaje netaknut
(piće može biti privremeno izvan kataloga). Kad korisnik ima i stari i novi
zapis, stanja se spajaju bez gubitka — `owned/tried/wishlist` logičkim ILI,
ocjena = viša, bilješka = prva neprazna.

### Čuvar za ubuduće

`drinkIdRegistry.json` popisuje svaki ID koji je ikad isporučen. Test tvrdi da
se **svaki** od njih i danas razrješava. Ako netko ukloni piće bez aliasa, CI
pocrveni s uputom umjesto da korisnici tiho izgube podatke. Provjereno
simulacijom (uklonjen `rum-mount-gay-xo` → test pao s očekivanom porukom).

**Rezultat:** `tsc` čist, **433 testa prolaze** (424 + 9 novih).
