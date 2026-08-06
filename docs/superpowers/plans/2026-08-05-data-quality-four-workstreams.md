# Četiri toka čišćenja podataka — Implementation Plan

> **For agentic workers:** koraci su checkboxi (`- [ ]`). Svaki tok je nezavisan i
> može se raditi zasebno; unutar toka koraci idu redom. Prije i poslije svakog
> koraka pokreni `python3 scripts/data-quality-report.py` i usporedi brojku koju
> taj korak cilja.

**Kontekst:** app je nakon PR-a `claude/prices-brands-mismatch-6q2q35` dobio
jedinstven razrješivač cijene, ispravne marke pića i razlučivije sparivanje. Ono
što je ostalo **nije kod nego podaci** — engine je razlučiv koliko i ono što mu
damo. Ova četiri toka uklanjaju te limite.

**Mjerilo:** `app/scripts/data-quality-report.py` (samo čita, nikad ne piše).

---

## Polazno stanje (izmjereno 2026-08-05, cijeli katalog)

| | brojka | cilj |
|---|---|---|
| **W1** cigara bez `flavorTags` | 1355 / 3701 (36,6 %) | < 300 |
| **W1** wrapper `—` | 1415 | < 300 |
| **W1** ime linije izvedeno iz URL sluga | 1692 → **0** (metrika precizirana) | < 200 |
| **W1** najveći profilni bucket | 1355 (36,6 %) | < 15 % |
| **W2** boca u profilnim bucketima ≥ 5 | 440 / 930 (47,3 %) | < 15 % |
| **W3** cijena s oznakom datuma preuzimanja | 0 / 3427 | 100 % |
| **W4** imena pića sa sirovim repom scrapea | 78 / 930 | 0 |

Zašto to boli: 1355 cigara bez ijednog taga ima zadano tijelo 3 / snagu 3, pa im
engine **matematički mora** dati isti prijedlog. Isto s druge strane — 37 od 70
ginova ima identične tagove, tijelo i slatkoću.

---

## ⚠️ Gdje se što smije pokretati

Ovo je najvažnija stavka za predaju posla.

**Mrežna politika Claude Code okruženja blokira sve hostove trgovina.**
Provjereno 2026-08-05: `neptunecigar.com`, `humidor.hr`, `cigarworld.de`,
`havana-cigar-shop.com` — svi vraćaju `CONNECT tunnel failed, 403`.

| Okruženje | Što ide ovdje |
|---|---|
| **Claude Code (remote)** | Sve deterministično i offline: preslagivanje linija iz postojećih podataka, izvođenje prikaznih imena, shema + UI za svježinu cijena, testovi, CI gateovi, review |
| **Cursor (lokalno)** | **Svaki scrape.** W1 korak 2, W2 korak 2, W3 korak 3 |

Praktično: korake označene 🌐 **ne pokušavaj ovdje** — pripremi worklist i
merge-skriptu ovdje, a scrape pokreni na Cursoru pa vrati sirovi JSON u
`scripts/output/`.

---

## Globalna pravila (vrijede za sva četiri toka)

- **Nikad ne briši id cigare ili pića bez aliasa.** Kolekcije i dnevnik žive u
  `localStorage` i ključaju na te id-eve; obrisan id tiho osiroti korisnikove
  oznake. Nasljednik ide u `src/data/cigarIdAliases.json` /
  `drinkIdAliases.json`. Čuva `src/data/drinkIds.test.ts`.
- **Ne izmišljaj degustacijske note.** Tag smije doći iz teksta trgovine,
  proizvođača ili kuriranog istraživanja — nikad iz "zvuči kao Maduro".
  Kad je izvedeno heuristikom, `profileEstimated` ostaje `true`.
- **Ne diraj HR cijene i URL-ove** osim u W3, i ondje samo kroz postojeći
  `sync-hr-shops.py`.
- **Svi CI gateovi moraju ostati zeleni** poslije svakog koraka:
  ```
  cd app
  npx tsc -b --noEmit && npm test && npm run build
  python scripts/apply-taxonomy.py --check --skip-normalize
  python scripts/normalize-vitolas.py --check
  python scripts/taxonomy-audit.py --fail-on-new --check-only
  python scripts/apply-cigar-descriptions.py --check
  python scripts/derive-drink-brands.py --check
  python scripts/test_reconcile_hr.py
  ```
- **Jedan tok = jedan PR.** `cigars.json` je 5 MB; miješanje tokova daje diff
  koji se ne da pregledati.

---

# W1 — Profili cigara (najveći učinak)

**Nalaz:** nije "nedostaju tagovi" nego **dva sloja**. 1331 od 1355 zapisa bez
tagova ima `catalogSource: "market"`, ime linije izvedeno iz URL sluga
(`"xo 61 2 52"`, `"serie r no"`), wrapper `—` i note-šablonu *"linija iz trgovine
Neptune Cigar"*. To su **vitole jedne linije razbijene u zasebne "linije"**.

Dobra vijest: **1323 od 1355 ima Neptune Cigar product URL** — dakle postoji
izvor s notama, snagom i wrapper/binder/filler podacima.

`profile-cigars.py` **ne rješava ovo** — provjereno: svima dodijeli isti
generički habano profil, pa broj različitih profila padne umjesto da naraste.
Ne pokreći ga kao rješenje W1.

### Korak 1 — Preslagivanje razbijenih linija (offline, ovdje)

- [ ] Skripta `scripts/fold-market-vitolas.py`: grupiraj `catalogSource=="market"`
      zapise po `(brand, korijen linije bez dimenzija)`; polazna mjera: 113 grupa
      pokriva 306 zapisa — proširi pravilo dok pokriva > 1000
- [ ] Svaki član grupe postaje `vitola` u zapisu-nositelju (ime vitole iz
      `vitola` polja + dimenzije), a ne zaseban zapis
- [ ] **Za svaki spojeni id upiši alias u `cigarIdAliases.json`** — bez iznimke
- [ ] Ime linije: iz `scripts/data/taxonomy/*.json` kad postoji, inače Title
      Case korijena sluga; nikad ostavi malim slovima
- [x] `--check` varijanta (CI-safe, ne piše)
- [x] Provjera: `slug_line_names` pada, `total` pada, `npm test` zelen
  <!-- Metrika precizirana u fix/w1-slug-metric-refine: Title Case + model-broj
       + ordinali više se ne broje kao slugovi. Rezultat: 609 → 0 (PR #135
       je već počistio sve prave slugove). -->

### Korak 2 — 🌐 Neptune scrape (Cursor)

- [ ] `scripts/build-neptune-worklist.py` (ovdje): id + Neptune URL za svaki
      zapis bez tagova → `scripts/output/neptune_worklist.json`
- [ ] 🌐 `scripts/scrape-neptune-profiles.py` (Cursor): Playwright, chromium,
      pauza 1,5–2 s, jedna sesija; po stranici izvuci: opis, `Strength`,
      wrapper/binder/filler, zemlju → `scripts/output/neptune_raw.json`
- [ ] Sirovi JSON commitaj — da se merge može ponoviti bez ponovnog scrapea

### Korak 3 — Merge (offline, ovdje)

- [ ] `scripts/merge-neptune-profiles.py`: EN riječi trgovine → postojeći
      rječnik tagova (iskoristi inverz `describe-lines.TAG_EN`, isti pristup kao
      `merge-flavor-enrichment.py`)
- [ ] `strength`/`body` iz Neptuneove ocjene → `strengthFromShop: true`
- [ ] `profileEstimated: false` **samo** kad tagovi dolaze iz teksta trgovine
- [ ] Idempotentno po id-u; ne dira zapise koji već imaju tagove
- [ ] Provjera: `no_flavor_tags` < 300, `largest_profile_share_pct` < 15 %

**Gotovo kad:** najveći profilni bucket < 15 % kataloga i `npm test` zelen.

---

# W2 — Profili pića

**Nalaz:** 47 % boca sjedi u bucketima od ≥ 5 identičnih profila. Najgore:
ginovi (70 boca → 8 profila, najveći bucket 37) i konjaci (101 → 26, najveći 25).

**Vino je dokaz da se da:** 124 boce → 93 profila, nijedan bucket ≥ 5. Kopiraj
taj pristup.

### Korak 1 — Worklist po prioritetu (ovdje)

- [ ] `scripts/build-drink-profile-worklist.py`: boce u bucketima ≥ 5, sortirano
      po veličini bucketa → `scripts/output/drink_profile_worklist.json`
- [ ] Redoslijed rada: **gin → brandy → whisky → rum** (tequila je 7 boca, može
      ručno; vino i digestivi su gotovi)

### Korak 2 — 🌐 Izvor nota (Cursor)

- [ ] 🌐 Za svaku bocu iz worklista: `priceUrl` trgovine ili stranica
      proizvođača; izvuci degustacijske note → `scripts/output/drink_notes_raw.json`
- [ ] Gdje izvora nema, ostavi prazno — **ne popunjavaj napamet**

### Korak 3 — Merge + kalibracija (ovdje)

- [ ] Proširi rječnik tagova za botanicals (gin: `borovica`, `citrus`, `cvjetno`,
      `papar`, `korijen`, `anis`, `kamilica`) — postojećih 3 taga po ginu ne
      mogu razlikovati 70 boca
- [ ] `sweetness`/`body` po boci, ne po kategoriji
- [ ] Provjera: `in_buckets_ge_5_pct` < 15 %

**Gotovo kad:** nijedna kategorija nema bucket > 5 boca i `npm test` zelen.

---

# W3 — Svježina cijena (četvrta cijena)

**Nalaz:** u podacima **nema nijednog vremenskog žiga** (0 / 3427 cijena). App
zato ne može reći koliko je cijena stara — trenutna napomena
(`price.snapshotNote`) je poštena, ali neodređena.

Dodatni izvor razlike: `shop_common.py` ima **zakovane tečajeve**
(`USD_TO_EUR = 0.92`, `GBP_TO_EUR = 1.17`, `CHF_TO_EUR = 1.05`). Svaka USA
cijena je konverzija po tečaju koji nitko ne osvježava.

### Korak 1 — Shema (ovdje)

- [ ] `fetchedAt` (ISO datum) na `Vitola.regionLinks[*]`, `Cigar.regionLinks[*]`
      i uz `Vitola.priceEUR` — u `src/types.ts`
- [ ] `lib/cigarPrice.ts` prosljeđuje `fetchedAt` kroz `ResolvedPrice`
- [ ] Test: `fetchedAt` nikad u budućnosti, format `YYYY-MM-DD`

### Korak 2 — UI (ovdje)

- [ ] `price.snapshotNote` → konkretno: *"Cijena preuzeta {datum}."*
- [ ] Starije od 90 dana: vidljiva oznaka *"cijena je starija od 3 mjeseca"*
- [ ] Fallback na postojeći neodređeni tekst kad `fetchedAt` nedostaje

### Korak 3 — 🌐 Osvježi cijene (Cursor)

- [ ] 🌐 `python scripts/sync-hr-shops.py` (Humidor + Havana)
- [ ] 🌐 `python scripts/enrich-region-links.py` (EU/USA)
- [ ] Obje skripte upisuju `fetchedAt` za svaku cijenu koju dodirnu
- [ ] Tečajeve u `shop_common.py` osvježi **i upiši datum tečaja u komentar**
- [ ] Provjera: `with_fetched_at_pct` = 100 %

### Korak 4 — Održavanje

- [ ] Zabilježi u `AGENTS.md`: cijene se osvježavaju kvartalno, lokalno,
      koracima iz Koraka 3

**Gotovo kad:** svaka prikazana cijena nosi datum, a app kaže kad je zastarjela.

---

# W4 — Prikazna imena pića (najmanji, najbrži)

**Nalaz:** 78 od 930 imena nosi rep scrapea
(`"Rémy Martin XO EXTRA OLD Cognac Fine Champagne 40% Vol. 0,7l u poklon kutiji"`).
Nijedna boca ne koristi `nameLoc`, iako polje postoji i app ga već poštuje
(`lib/drinkName.ts` → `drinkNameLoc`).

**Ne mijenjaj `name`** — on je ključ za poklapanje sa slugovima trgovina
(`lib/drinkBuyLink.ts`) i za pretragu (`drinkNameHaystack`). Čisti se samo
prikaz.

### Koraci (svi offline, ovdje)

- [x] `scripts/derive-drink-display-names.py` po uzoru na
      `derive-drink-brands.py`: generira `src/data/drinkDisplayNames.json`,
      ručne ispravke idu u `scripts/data/drink_display_name_overrides.json`
- [x] Ponovi `TAIL` regex iz `derive-drink-brands.py` (jakost, volumen, poklon
      pakiranje) + dekodiraj HTML entitete (`&#039;` → `'`)
- [x] `--check` varijanta i **dodaj je u `.github/workflows/ci.yml`** uz ostale
      python gateove
- [x] `lib/drinkName.ts`: `drinkNameLoc` čita prikazno ime kad postoji
- [x] Test: nijedno prikazno ime ne sadrži `% Vol`, `u poklon kutiji`, `&#`
- [x] Provjera: `raw_scrape_tails` = 0
- [x] **Regresija koju moraš provjeriti:** `npx vitest run src/lib/drinkBuyLink.test.ts`
      — poklapanje sluga i dalje mora ići preko sirovog `name`

**Gotovo kad:** `raw_scrape_tails` = 0 i `drinkBuyLink` testovi zeleni.

---

## Redoslijed (ako se radi jedan po jedan)

1. **W4** — najmanji, offline, odmah vidljiv u UI-u; dobar zalet
2. **W3 koraci 1–2** — shema + UI, offline; korak 3 čeka Cursor
3. **W1** — najveći učinak na sparivanje, ali i najveći diff
4. **W2** — ovisi o dostupnosti izvora nota po boci

W1 i W2 se **ne smiju miješati u istom PR-u.**

## Predaja na Cursor

Ovaj plan, mjerilo (`scripts/data-quality-report.py`) i sve polazne brojke su u
repou — Cursor sesija ne mora ništa ponovno izvoditi. Otvori ovaj file, uzmi tok,
i kreni od prvog neoznačenog checkboxa.
