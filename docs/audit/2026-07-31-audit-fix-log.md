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

---

## Val 2 — OCR bundle se učitavao svakom posjetitelju

### Nalaz

`vite.config.ts` je PaddleOCR/onnxruntime gurao u **imenovani** `manualChunks`
chunk. Imenovani chunk rastopi granicu dinamičkog importa: iako
`lib/ocrEngine.ts` koristi `await import("@paddleocr/paddleocr-js")`, entry je
dobio **statični** import i `<link rel="modulepreload">`:

```
dist/assets/index-*.js:  from"./ocr-paddle-*.js"
dist/index.html:         <link rel="modulepreload" href="…/ocr-paddle-*.js">
```

Chunk je **10,9 MB / 3,53 MB gzip** — povlačio ga je svaki posjetitelj, i onaj
koji OCR nikad ne otvori.

Raniji `558b4cd` je problem točno prepoznao, ali riješio krivu polovicu:
izbacio ga je iz **Workbox precachea**, dok je `modulepreload` ostao.

Uz to: `digestifs.json` (eager, preko `data/index.ts`) padao je u isti
`data-misc` bucket kao `dictionary`/`lexicon`/`hrGuide`/`eveningArchetypes`/
`clubSources` — sadržaj koji čita **samo lazy Club stranica**. Jedan eager
import povlačio je ~96 kB gzip klupskog teksta u prvo učitavanje.

### Popravak

`app/vite.config.ts`:

- OCR **izbačen iz `manualChunks`** → ostaje pravi lazy chunk iza `await import()`.
- Ime chunka zadržano preko **`output.chunkFileNames`** (koji ne utječe na graf),
  pa `globIgnores: ["**/ocr-paddle-*.js"]` i dalje pogađa.
- `digestifs` + alias/registar datoteke → `data-meta`; ostatak `data/*.json`
  vraća `undefined` pa ide uz svoju lazy stranicu.

### Izmjereno

| Prvo učitavanje (gzip) | prije | poslije |
|---|---|---|
| `ocr-paddle` | 3 526 kB | — (lazy) |
| `data-misc` | 113 kB | — (uz Club) |
| `data-meta` | 48 kB | 64 kB |
| `index` | 60 kB | 64 kB |
| ostalo (vendor, rums, whiskies, brandies, drinks-small, cigars) | 462 kB | 462 kB |
| **ukupno** | **4 210 kB** | **590 kB** |

**−3,62 MB gzip (−86 %).** Potvrđeno: `ocr-paddle` više nije u
`dist/index.html` preloadima ni u SW precache manifestu.

`tsc` čist, 433 testa prolaze.

---

## Val 3 — robusnost

### 3a. `parseHash` je rušio boot u bijeli ekran

`decodeURIComponent` baca `URIError` na neispravnom postotnom kodu (`%`,
`%E0%A4%A`). `parseHash` se zove na **module scopeu** (`route.ts:113`) i na
svaki `hashchange`, pa je iznimka išla neuhvaćena — bijeli ekran iz kojeg se
korisnik ne izvuče bez ručnog uređivanja URL-a. Dovoljno je da se podijeljeni
deep-link iskvari u chat aplikaciji.

**Popravak:** `safeDecode()` — neispravan segment ostaje sirov. Bolje izgubiti
deep-link nego cijeli app. `app/src/store/route.ts` + 2 testa.

### 3b. Nije postojao nijedan `ErrorBoundary`

Svaka greška u renderu ili odbijeni `import()` lazy stranice = prazan ekran.
Najizglednija putanja: PWA je `registerType: "prompt"`, korisnik ostaje na
starom service workeru, u međuvremenu izađe deploy, stari hashirani chunk
nestane s Pagesa → `ChunkLoadError`.

**Popravak:** `app/src/components/ErrorBoundary.tsx`

- razlikuje **zastarjeli chunk** ("izašla je nova verzija, osvježi") od opće
  greške;
- izričito kaže da su kolekcija i dnevnik na uređaju i nisu izgubljeni —
  korisnik to inače ne može znati;
- gumbi Osvježi / Natrag na početak;
- dvojezično **bez i18n konteksta**, da radi i kad padne sam provider.

Ugrađen na dva mjesta: u `main.tsx` oko `I18nProvider` (vanjska mreža) i u
`App.tsx` oko `<Suspense>` s `key={page}` — pad jedne stranice ne odnosi
navigaciju i promjena taba resetira granicu.

### 3c. Backend: path traversal kroz `cigar_id`

`band_service._SAFE_ID = ^[\w.@+-]+$` propuštao je `..`, pa je
`POST /band/reference` s `cigar_id=".."` pisao `<uuid>.jpg` i **`meta.json`**
razinu iznad `BAND_DIR` (potvrđeno reprodukcijom).

**Popravak:** `^(?!\.*$)(?!.*\.\.)[\w.@+-]+$` — točka **ostaje** dopuštena jer
je vitola-scoped ključ nosi (`cig-ashton-aged-maduro@maduro-no.30`), ali `..`
i sami `.`/`...` padaju. Uz to `is_relative_to(BAND_DIR)` kao druga brana.
`backend/tests/test_smoke.py` +2 testa (4 ukupno, prolaze).

**Rezultat vala:** `tsc` čist, **435 testova** (433 + 2), build prolazi,
backend 4/4.

---

## Val 4 — CI koji opet nešto znači

### Nalaz

`ci.yml` je imao `push: branches-ignore: [master]`, pa **izravni pushevi na
master nisu prolazili nikakvu provjeru** — a njih je 24 od zadnjih 30 commita.
Tako je slomljen `tsc` (`6ed059d`) stigao na master i oborio deploy; jedini
signal bio je crveni deploy run koji nitko ne gleda.

Uz to su **4 od 5 Python gateova padala** na čistom HEAD-u, pa je i PR put bio
crven — što je i objašnjavalo zaobilaženje.

### Popravak

**`apply-cigar-descriptions.py`** — nije pratio `cigarIdAliases.json`, pa je
svako spajanje linija (Asylum 13) ostavljalo kurirani opis da visi na starom
id-u. Dodan `resolve_id()` koji prati alias lanac, isto kao `resolveCigarId` u
appu. Time su se primijenila i 2 zaostala opisa (4 retka u `cigars.json`,
bez reformatiranja).

**`taxonomy-audit.py`** — prijavljivao `Cusano · 18 paired maduro` bez unosa u
taksonomiji. Provjerom se pokazalo da je to **tanki duplikat** od
`cig-cusano-18-maduro` (isti proizvod — URL-ovi su `cusano-18-paired-maduro-*`):
bez pokrova, veziva, punjenja i okusnih oznaka, s generičkom bilješkom i jednom
vitolom, dok canonical ima punu listu listova, prave bilješke i 4 vitole.

> Prije brisanja provjereno je nosi li duplikat išta jedinstveno. Jedini
> kandidat bio je Neptune URL za Churchill — a canonical ga je **već imao** u
> `regionLinks`. Dakle nula izgubljenih podataka. Uz to je dodan alias
> `cig-cusano-18-paired-maduro → cig-cusano-18-maduro`, pa se i korisnikova
> oznaka seli. Katalog: 2401 → 2400.

**`ci.yml`**:

- `push: branches: [master]` — master napokon prolazi provjeru;
- blokirajući gateovi: `tsc`, testovi, `taxonomy-audit`, `apply-cigar-descriptions`,
  `test_reconcile_hr`, `build`;
- **neblokirajuće** (`continue-on-error`): `apply-taxonomy --check` i
  `normalize-vitolas --check` — ~~nakupljeni drift, traže sadržajne odluke~~.
  > ⚠️ **Povučeno u Valu 5.** Ta je procjena bila kriva: brojka „239" je bila
  > iz druge skripte, `apply-taxonomy` je htio 3 bezopasne izmjene, a
  > `normalize-vitolas` je skrivao **brisanje jednog zapisa koji nije
  > duplikat**. Oba su od Vala 5 blokirajuća.
- nov `backend` job — servis dosad nije imao **nikakvu** CI pokrivenost.
  Instalira samo lagane ovisnosti (paddle/torch su neobavezni, servis ima stub
  put), pa smoke testovi uključujući path-traversal čuvar vrte se u sekundama.

**Rezultat:** blokirajući gateovi zeleni lokalno, `tsc` čist, 435 testova,
backend 4/4, build prolazi.

---

## Sažetak

| Val | Commit | Učinak |
|---|---|---|
| 1 | `28f0bae` | 50 ID-jeva pića više ne siroti korisničke oznake; registar + 9 testova |
| 2 | `e263752` | prvo učitavanje 4 210 → 590 kB gzip (**−3,62 MB**) |
| 3 | `89cbb05` | dva bijela ekrana zatvorena; backend traversal zatvoren |
| 4 | `f4d8462` | CI napokon pokriva master; 2 gatea popravljena, backend u CI-ju |
| 5 | `b7b9bf6` | zastarjela odluka o spajanju brisala je zapis koji nije duplikat; svih 5 gateova blokira |

### Namjerno nedirnuto

- **Age gate** — `VITE_AGE_GATE` postoji kao tip i komentar u `.env.example`
  („leave unset (gate ON)"), ali mehanizam nije nigdje implementiran. Treba
  odluka: implementirati ili maknuti obećanje iz dokumentacije.
- **`AGENTS.md`** još tvrdi „There is no backend"; `README.md` ne spominje
  backend, OCR ni CDN-ove (jsdelivr/HuggingFace/ModelScope) koje PWA gađa na
  prvi OCR. Brojke u `README.md` su zastarjele (155/273/98/2395 → 321/275/101/2400).
- **Backend**: nema ograničenja veličine uploada ni autentikacije, `Image.open`
  na nepouzdanim bajtovima vraća 500 umjesto 400, `/health` učitava CLIP model.
- **Pristupačnost**: 5 sheetova bez `role="dialog"`/Esc/focus trapa, `Meter`
  bez `aria-label`.
- **Perf**: `cycle` u `useMemo` deps reskorira 2400 cigara na svaki klik
  „Sljedeći prijedlog".

---

## Val 5 — dva „teška" gatea: smetalo je, i to više nego što se činilo

U Valu 4 ostavio sam `apply-taxonomy` i `normalize-vitolas` neblokirajuće uz
opasku da traže sadržajne odluke. Mjerenje je pokazalo da je ta procjena bila
kriva u oba smjera — jedan gate je bio bezopasan, drugi je skrivao **stvarni
gubitak podataka**.

### `apply-taxonomy` — bezopasan, bio je samo zaostatak

Brojka „239 line-mergeva" dolazila je iz **druge** skripte. Ovaj gate je htio
točno 3 izmjene, `input_records == output_records == 2400`, `aliases_added: 0`:

- `priceUrl` za `cig-cusano-18-double-connecticut` i `cig-cusano-18-maduro`;
- `cig-don-tomas-bundle`: `priceEUR` 2,8 → 3,6.

Zadnja je **ispravak, ne rizik**: zadana vitola te linije je Robusto @ 3,6 €
i app je već prikazivao 3,6 — pohranjeno polje je bilo zastarjelo (2,8 je bila
Rothschildova cijena). Primijenjeno.

### `normalize-vitolas` — skrivao je brisanje jedinog HR zapisa

„239 line_merges" je brojač **razmatranih**, ne primijenjenih odluka. Stvarni
učinak: **jedan** zapis bi nestao, 2400 → 2399.

Taj zapis je `cig-asylum-insidious-short`, i **nije duplikat**:

| | Insidious | Insidious Short |
|---|---|---|
| vitole | Short Corona 44×**142**mm, Robusto 50×127mm | Corona 44×**102**mm |
| cijena | — | **9,40 €** |
| HR | nema | **The Humidor** |

Spajanje bi obrisalo jedini HR-dostupan zapis s cijenom, a njegovu vitolu ne
bi ni prenijelo: odluka je nalagala preimenovanje `Corona` → `Short Corona`,
što se sudara s postojećom 44×142mm i tiho ispada kao duplikat. Rezultat bi
bio „Kupi" gumb na `Insidious` koji vodi na stranicu *Insidious Shorta* —
krivi proizvod uz prikazanu cijenu.

**Uzrok su dva izvora istine koja si proturječe:**

| izvor | datum | kaže |
|---|---|---|
| `line_merge_decisions.json` | 25.07. (`5541fa4`) | spoji Short u Insidious |
| `taxonomy/asylum.json` `keepSeparate` | 30.07. (`reviewedAt`, `status: done`) | drži ih odvojeno |

Novija urednička revizija je rekla „odvojeno", ali stara instrukcija nije
maknuta — i tiho je pobjeđivala, jer `apply_line_decisions` nikad nije
konzultirao `keepSeparate`.

### Popravak

1. **Uklonjena zastarjela odluka** o spajanju iz `line_merge_decisions.json`
   (281 → 280). Novija taksonomija je mjerodavna.
2. **Trajni čuvar** `assert_no_keep_separate_conflicts()` u
   `normalize-vitolas.py`: spajanje koje proturječi `keepSeparate` sada **pada
   glasno** umjesto da progura brisanje. Provjereno vraćanjem proturječja —
   skripta padne s imenom marke i uputom.
3. **`--check` više ne piše** u `scripts/output/` (ni `apply-taxonomy` ni
   `normalize-vitolas`). Prije su čitači prljali radno stablo u CI-ju.
4. **Oba gatea vraćena u blokirajuće** u `ci.yml`; `continue-on-error` maknut.

Provjera opsega prije zahvata: **61 marka** ima `keepSeparate` pravila i
**281 odluka** o spajanju — sukob je bio točno **1**. Dakle jedna zastarjela
instrukcija, ne sistemski drift.

**Rezultat:** svih **5 CI gateova zeleno**, `--check` ne prlja stablo, katalog
ostaje 2400 zapisa, `cig-asylum-insidious-short` netaknut (Corona 44×102mm,
9,40 €, The Humidor). `tsc` čist, 435 testova, build prolazi, backend 4/4.

---

## Val 6 — dokumentacija koja laže agentima

`AGENTS.md` je i dalje tvrdio **„There is no backend"** — datoteka koju svaki
sljedeći agent čita prvu. Uz `backend/` FastAPI servis u repou to je aktivno
zavaravanje, a ne samo zastarjelost. `README.md` nije spominjao ni backend ni
OCR ni CDN-ove, a brojke su odlutale kroz desetke regeneracija:
155/273/98/2395 dok je stvarno 321/275/101/**2400**.

### Popravak

**`AGENTS.md`** — točan opis: PWA je isporučeni proizvod, `backend/` i
`app/scripts/` su neobavezni i nisu dio deploya. Dodano i troje što bi
sljedećeg agenta inače koštalo istog istraživanja:

- svih 5 CI gateova nabrojano (i da su read-only);
- **ID se nikad ne briše bez aliasa** — s razlogom (localStorage) i mjestom;
- **`keepSeparate` nadjačava `line_merge_decisions.json`** — sukob prekida skriptu;
- **OCR bundle mora ostati lazy** — zašto `manualChunks` ime ruši lazy granicu.

**`README.md`** — osvježene brojke, dodan odjeljak o OCR-u (koji engine za što,
da je bundle lazy, da modeli idu s jsDelivr/HuggingFace/ModelScope i da app
**nije** offline-first za OCR modele) i o `backend/` servisu.

**`app/src/data/readmeCounts.test.ts`** — 9 testova veže README brojke uz
stvarne podatke. Brojke su odlutale jer ih ništa nije držalo; sad drži.

**Rezultat:** `tsc` čist, **444 testa** (435 + 9).
