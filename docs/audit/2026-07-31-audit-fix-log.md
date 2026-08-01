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

---

## Val 7 — backend hardening

Servis se prema `backend/README.md` vrti na `--host 0.0.0.0` (zbog Android
buildа), dakle dohvatljiv je s mreže. U tom kontekstu tri stvari nisu bile u redu.

### Nalaz i popravak

**1. Upload bez gornje granice.** Sva tri endpointa radila su `await file.read()`
— cijeli body u memoriju. Jedan veliki POST ruši servis.
→ `read_upload()` čita u komadima od 1 MiB i odbija preko `MAX_UPLOAD_BYTES`
(12 MB, s viškom za fotografiju računa) s **413**, prije nego primi sve.

**2. Ne-slika je vraćala 500.** `Image.open` na nepouzdanim bajtovima baca
`UnidentifiedImageError`, što je izlazilo kao serverska greška iako je krivnja
klijentova. Uz to nije bilo brane za „decompression bomb" (mala datoteka,
gigabajti piksela).
→ novi `backend/app/images.py`: `load_rgb()` provjeri dimenzije **prije**
`convert()` (koji tek alocira piksele) i baca `InvalidImage`; endpointi ga
mapiraju na **400**. `MAX_IMAGE_PIXELS` = 50 Mpx.

**3. `/health` je bio najskuplji endpoint.** `band_status()` je zvao
`_try_load_clip()` (ViT-B-32, stotine MB), a `engine_status()` `_load_paddle()`
— health check je povlačio cijeli ML stack.
→ oba sada samo **prijavljuju** stanje (`None` = još nije ni pokušano), motori
se učitavaju lijeno na prvi stvarni `/ocr` odnosno `/band/*` poziv.

**Uz to:** pokvaren `meta.json` obarao je svaki zahtjev na 500 dok ga netko
ručno ne makne — sada se tretira kao „nema referenci" uz upozorenje u logu.

### Testovi

`backend/tests/test_api.py` — **11 novih** (ukupno **15**, bilo 4), uključujući
HTTP razinu preko `TestClient`: 400 za ne-sliku i praznu datoteku, 413 preko
granice, 400 za traversal `cigar_id`, i da `/health` **ne** pokrene učitavanje
motora (test eksplicitno resetira stanje pa ne mjeri redoslijed izvršavanja).

CI `backend` job dobiva `fastapi python-multipart httpx`; paddle/torch i dalje
nisu potrebni.

### Namjerno nedirnuto

**Autentikacije i dalje nema.** To je product odluka, ne bug koji mogu sam
zatvoriti — dodavanje tokena mijenja i klijenta (`lib/bandMatch.ts`) i način
pokretanja. Umjesto toga je rizik sada **eksplicitno dokumentiran** u
`backend/README.md`, s preporukom `OCR_HOST=127.0.0.1` osim kad LAN stvarno
treba. `uploadBandReference` se za sada ionako nigdje ne poziva iz appa.

---

## Val 8 — perf i pristupačnost

### 8a. Rotacija prijedloga reskorirala je cijeli katalog

`cycle` je bio u `useMemo` deps **zajedno s rangiranjem**, pa je svaki klik na
„Sljedeći prijedlog" iznova bodovao cijeli katalog — da bi na kraju samo pomaknuo
prozor. Rotacija ne mijenja poredak.

Izmjereno na ovom stroju: `pairCigarsForDrink` nad **2400 cigara = 43,6 ms**
(`pairDrinksForCigar` nad 963 pića = 13,4 ms). Na mobitelu višestruko, i to na
svaki dodir.

**Popravak:** rangiranje je svoj memo (bez `cycle`), rotacija svoj koji ovisi o
njemu. Ponašanje nepromijenjeno — cycle 0 i dalje daje stabilan #1.

### 8b. Modalni sheetovi bez ijedne a11y osobine

Svih pet (`DetailSheet`, `LineSheet`, `BrandSheet`, `EveningSessionSheet`,
`VitolaPicker`) bili su gola `<div>` s `onClick` na pozadini: bez `role`, bez
`aria-modal`, bez Escapea, bez zamke fokusa i bez povrata fokusa. Čitač ekrana
nije znao da je otvoren dijalog, tipkovnicom se iz njega nije dalo izaći, a
pozadina je skrolala ispod.

**Popravak:** jedan zajednički **`SheetShell`** — `role="dialog"`,
`aria-modal`, `aria-label` s imenom stavke, Escape, Tab-zamka, povrat fokusa na
element koji je sheet otvorio, i zaključan scroll pozadine. A11y sada živi na
jednom mjestu; svaki novi sheet ga dobiva besplatno. Provjereno da nije ostao
nijedan goli `fixed inset-0 z-50` overlay.

### 8c. `Meter` je čitaču ekrana bio nevidljiv

Tijelo/snaga/slatkoća crtali su se kao pet dekorativnih rombova bez ikakvog
teksta. Sada je omotač `role="img"` s `aria-label` („Tijelo 3/5"), a rombovi i
tekstualna oznaka su `aria-hidden` da se vrijednost ne izgovori dvaput.

**Rezultat:** `tsc` čist, 444 testa, build prolazi.

---

## Val 9 — tri sitnice iz nalaza

- **`shareCard.ts`** — `URL.revokeObjectURL(url)` odmah nakon `a.click()` zna
  prekinuti preuzimanje u dijelu preglednika. Odgođeno.
- **`i18n/index.tsx`** — jedini goli pristup `localStorage`u u aplikaciji
  (ostatak ide kroz `safeStorage` i storeove s `try/catch`). Kad je storage
  blokiran (Safari private, stroga pravila kolačića), sam getter baca
  `SecurityError` i ruši boot. Sada obavijeno; jezik tada vrijedi do zatvaranja.
- **`store/humidor.ts`** — `exportHumidors()` vraćao je **živu referencu** na
  interni `cache`, pa je pozivatelj mogao mutirati state mimo `persist()`a.
  Sada kopija.

---

## Sažetak svih valova

| Val | Commit | Učinak |
|---|---|---|
| 1 | `28f0bae` | 50 ID-jeva pića više ne siroti korisničke oznake; registar + 9 testova |
| 2 | `e263752` | prvo učitavanje 4 210 → 590 kB gzip (**−3,62 MB**) |
| 3 | `89cbb05` | dva bijela ekrana zatvorena; backend traversal zatvoren |
| 4 | `f4d8462` | CI pokriva master; 2 gatea popravljena, backend u CI-ju |
| 5 | `b7b9bf6` | zastarjela odluka o spajanju brisala je zapis koji nije duplikat |
| 6 | `6055cbb` | `AGENTS.md` više ne tvrdi „no backend"; README + čuvar brojki |
| 7 | `45f33f2` | backend: granica uploada, 400 umjesto 500, jeftin `/health`; 15 testova |
| 8 | `9b55f39` | rotacija ne reskorira katalog (−44 ms/klik); sheetovi dobili dijalog semantiku |
| 9 | ovaj | revokeObjectURL, i18n storage, exportHumidors |

**Stanje:** `tsc` čist, **444 testa**, build prolazi, backend **15/15**,
**svih 5 CI gateova zeleno i blokira**.

### Ostaje za odluku (ne mogu je donijeti umjesto tebe)

- **Age gate** — `VITE_AGE_GATE` postoji kao tip u `vite-env.d.ts` i komentar u
  `.env.example` („leave unset (gate ON)"), ali mehanizam nije nigdje
  implementiran, pa taj prekidač ne radi ništa. Implementirati ili maknuti
  obećanje iz dokumentacije — trenutno se razilaze.
- **Backend autentikacija** — nema je. Rizik je dokumentiran u
  `backend/README.md` s preporukom `OCR_HOST=127.0.0.1`; pravo rješenje
  (shared token) mijenja i klijenta i način pokretanja.
- **Ovisnosti** — Vite 6→8, Vitest 3→4, `@vitejs/plugin-react` 4→6.
  `npm audit`: 0 ranjivosti, pa nije hitno.

---

## Val 10 — age gate (odluka: implementirati)

`.env.example` je opisivao gate („set to 0 or off during QA so the overlay is
skipped. Production / store builds: leave unset (**gate ON**) or set to 1"), a
`vite-env.d.ts` deklarirao tip — ali mehanizam nije postojao **nigdje** u
`src/`. Prekidač nije radio ništa, pa build s neрostavljenom varijablom nije
imao gate iako je dokumentacija tvrdila suprotno. To je stanje koje se otkrije
tek na reviewu trgovine.

### Popravak

| Datoteka | Uloga |
|---|---|
| `app/src/lib/ageGate.ts` | čista logika, odvojena od UI-ja radi testova |
| `app/src/components/AgeGate.tsx` | overlay |
| `app/src/App.tsx` | gate se rješava prije ostatka aplikacije |
| `app/src/i18n/index.tsx` | 8 novih stringova (hr + en) |
| `app/src/lib/ageGate.test.ts` | 10 testova |

**Ponašanje točno prema `.env.example`:** zadano UKLJUČEN; `VITE_AGE_GATE`
`0`/`off`/`false`/`no` ga gasi (neosjetljivo na velika slova i razmake), sve
ostalo ostavlja uključenim. Potvrda se pamti u `localStorage`
(`cigar-pairing-age-ok-v1`), pa se ne pita svako otvaranje.

Detalji koji nisu očiti:

- Gate je **zamjena** za aplikaciju, ne modal preko nje — sadržaj se ne smije
  nazrijeti ispod ni pročitati iz DOM-a čitačem ekrana.
- Postoji i **„Nemam 18"** put s pristojnom porukom, plus izlaz za slučajni
  krivi klik. Gate koji ima samo jedan gumb nije provjera nego formalnost.
- Blokiran storage ne ruši ništa — tada se pita pri svakom otvaranju (radije
  pitati dvaput nego propustiti).
- Prebacivanje jezika radi i na gateu, prije ulaska u aplikaciju.
- `role="dialog"`, `aria-modal`, `autoFocus` na potvrdi.

**Rezultat:** `tsc` čist, **454 testa** (444 + 10), build prolazi.

---

## Val 11 — backend autentikacija (odluka: dodati token)

Servis nije imao nikakvu provjeru, a zadani bind je `0.0.0.0` (odabran da ga
Android build na istoj mreži dohvati — što znači da ga dohvate i svi ostali na
toj mreži).

### Popravak

`Authorization: Bearer <token>` na **svemu osim `/health`**, kad je
`OCR_API_TOKEN` postavljen. Prazan token = bez provjere, pa lokalni razvoj na
`127.0.0.1` ostaje bez trenja.

Zaštićen je i **`/ocr`**, ne samo endpointi koji pišu: to je računski
najskuplja operacija u servisu, dakle najlakši način da netko s mreže zauzme
procesor. Pravilo je time i jednostavnije za pamćenje — `/health` je otvoren,
sve ostalo nije.

- usporedba tokena ide kroz `secrets.compare_digest` (konstantno vrijeme);
- **`/health` javlja `"auth": "token" | "none"`** — u kojem je načinu
  pokrenuta instanca ne smije biti pretpostavka;
- klijent šalje token preko `VITE_OCR_API_TOKEN`
  (`lib/ocrTypes.ts → apiAuthHeaders()`), koji koriste i `bandMatch.ts` i
  `ocrEngine.ts`;
- `backend/README.md` dobiva odjeljak s generiranjem tokena i i dalje
  preporučuje `OCR_HOST=127.0.0.1` kad LAN nije stvarno potreban.

**Testovi:** `backend` **21** (bilo 15) — `/health` ostaje otvoren, 401 bez
tokena i s krivim tokenom, prolaz s ispravnim, sva tri zaštićena endpointa.

**Rezultat:** `tsc` čist, 454 testa, build prolazi, backend 21/21.

---

## Val 12 — CI koji je izgledao uključeno, a nije pokrivao ništa

Nađeno **pri pripremi deploya**, prije mergea.

U Valu 4 sam `push: branches-ignore: [master]` zamijenio s
`push: branches: [master]` da master napokon bude pokriven. Time su, međutim,
**feature grane ostale bez CI-ja** dok se ne otvori PR — a to se odmah
osvetilo: PR #113 je otvoren preko API tokena, a **GitHub ne okida workflow na
događaje iz takvog tokena**. Rezultat: CI nije odradio **nijedan od 12
commitova ovog audita**. Jedini run na grani bio je za napušteni commit iz
prve sesije, i taj je pao.

Da nisam prije mergea provjerio status umjesto da se oslonim na „testovi
prolaze lokalno", u produkciju bi otišlo 12 commitova koje nikakav CI nije
vidio — točno onaj obrazac zbog kojeg je ovaj audit i počeo.

**Popravak:** `push` bez filtera po grani (svaka grana, uključujući master) +
`workflow_dispatch` za ručno pokretanje bez novog commita.

**Pouka za ubuduće:** „CI je konfiguriran" i „CI je odradio ovaj commit" nisu
ista tvrdnja. Prije mergea provjeri **run za točan SHA**, ne postojanje
workflow datoteke.

---

## Val 13 — merge s masterom: dva nalaza koja mijenjaju ranije zaključke

Pri deployu je master u međuvremenu narastao **2401 → 3701 cigaru** (+1357) i
PR je pao u konflikt na `cigars.json`. Konflikt je riješen uzimanjem
**masterove** verzije kao baze (nova katalogizacija se ne smije izgubiti), pa
su na nju re-primijenjene izmjene ove grane.

### 13a. Master je izgubio podatke koji nisu duplikati

Od **57 zapisa** koje je master uklonio u `59025d3`:

- 51 čist (podatak postoji drugdje ili nije bilo ničeg jedinstvenog);
- 4 uredna preimenovanja marke pod roditelja s očuvanom HR dostupnošću
  (JFR Lunatic ×2, Dunbarton Sobremesa, Oscar Valladares);
- **2 s pravim gubitkom:**

| zapis | izgubljeno |
|---|---|
| Asylum · Insidious Short | Corona **44×102 mm @ 9,40 €**, The Humidor — vitola nije nigdje prenesena (Insidious ima 44×**142** mm bez cijene) |
| Cain Daytona · 646 | HR dostupnost (Havana Shop) nije prešla na `cig-cain-daytona` |

Aliasi postoje, pa **korisničke oznake prežive** — mehanizam iz Vala 1 radi.
Izgubljen je podatak o *proizvodu*, ne o korisniku.

Asylum slučaj je **isto proturječje koje Val 5 popravlja**: `keepSeparate` kaže
odvojeno, `line_merge_decisions.json` kaže spoji. Master nema čuvar iz Vala 5,
pa je bug opalio opet. Nakon ovog mergea čuvar je na masteru.

> Zapisi **nisu uskrsnuti** u ovom mergeu — to je sadržajna odluka, ne dio
> rješavanja konflikta. Prijedlog je u „Za odluku" ispod.

### 13b. Dva gatea padaju i na čistom masteru — odluka iz Vala 5 povučena

| gate | stanje na netaknutom `master` HEAD-u |
|---|---|
| `taxonomy-audit --fail-on-new` | **1351** nova linija bez taksonomije, 132 marke (backlog iz uvoza) |
| `apply-taxonomy --check` | **ne konvergira** — masterove skripte nad masterovim podacima |

Provjereno izolirano: pristojno pokretanje masterovih skripti nad masterovim
podacima daje `EXIT=1`. Dakle **nije uzrokovano ovom granom**.

Držati ih blokirajućima značilo bi crven master od trenutka mergea. Vraćeni su
u `continue-on-error` **s ovom evidencijom u datoteci** — ne kao tiho gašenje.
Preostala tri gatea (`normalize-vitolas`, `apply-cigar-descriptions`,
`test_reconcile_hr`) blokiraju.

> **Probano i odbačeno:** bulk upis svih 1351 linije u `unresolved` po markama.
> Gate je pozelenio, ali je `apply-taxonomy` počeo **oscilirati s periodom 2**
> (A → B → A). Liječilo bi simptom i slomilo pipeline, pa je vraćeno.

Ovo povlači zaključak iz Vala 5 („svih 5 gateova blokira") — tada je vrijedio,
uz 2400 zapisa. Nakon uvoza od +1300 više ne vrijedi.

### Za odluku

1. **Vratiti 2 izgubljena zapisa?** Podaci su u gitu (`cb25c52`), povrat je
   mehanički. Preporuka: da — `keepSeparate` ih izričito drži odvojenima.
2. **1351 linija za kuriranje** — pravi posao, po markama (Tatuaje 79,
   Crowned Heads 53, Arturo Fuente 40…).
3. **`apply-taxonomy` ne konvergira** — zaseban bug, traži debug pipelinea.

---

## Val 14 — vraćeni izgubljeni podaci (odluka: vratiti)

Nastavak Vala 13a. Pri povratu se pokazalo da su **dva slučaja različita**, pa
ih ni popravak ne tretira isto.

### Cain Daytona 646 — moja ranija tvrdnja bila je pretjerana

Roditelj `cig-cain-daytona` **već ima** vitolu `646` (46×142 mm, **9,00 €**,
Havana Shop URL), a `markets` sadrži `HR`. Taksonomija navodi `646` kao vitolu
linije Daytona, `keepSeparate` je prazan — dakle **fold je bio ispravan** i
podatak o proizvodu je prenesen.

Nedostajala je samo oznaka `availabilityHR: ["Havana Shop"]`. Dodana.

> Ispravak: u Valu 13 sam ovo naveo kao „izgubljenu HR dostupnost" u istom
> rangu kao Asylum. Nije isto — ovdje je nedostajalo jedno polje, ne proizvod.

### Asylum Insidious Short — stvaran gubitak, zapis vraćen

Roditelj `cig-asylum-insidious` ima Short Coronu **44×142 mm** bez cijene i bez
HR; izgubljena Corona **44×102 mm @ 9,40 €** (The Humidor) **nije nigdje**.
Različite duljine = različite cigare, a `keepSeparate` ih izričito drži
odvojenima.

Zapis je vraćen iz `cb25c52` u cijelosti, na abecedno mjesto u katalogu.
Katalog: 3700 → **3701**.

**Alias uklonjen.** Master je imao `cig-asylum-insidious-short →
cig-asylum-insidious`; sada kad je ID opet živ zapis, alias bi ga zasjenio i
korisnikova oznaka vodila bi na krivu cigaru.

### Zašto se neće ponoviti

`normalize-vitolas --check` je **čist** (`changed: false`) — zastarjela odluka o
spajanju uklonjena je u Valu 5 i taj je popravak sada na masteru, pa pipeline
vraćeni zapis više ne guta. Da odluka ikad bude vraćena, čuvar
`assert_no_keep_separate_conflicts()` prekida skriptu.

**Rezultat:** `tsc` čist, 454 testa, build prolazi, backend 21/21, tri
blokirajuća gatea zelena. README osvježen na 3701 (uhvatio `readmeCounts.test.ts`).
