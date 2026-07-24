# Plan: La Aroma del Caribe, HR dostupnost i loši opisi/prijevodi

**Datum:** 2026-07-24
**Status:** spreman za izvršenje (Cursor radi po planu, review sutra)
**Autor plana:** Claude (analiza kataloga)
**Grana plana:** `claude/karibea-product-analysis-fix-8wayr8` (samo ovaj dokument)

> **Svrha:** tri neovisna problema prijavljena iz aplikacije. Svaki ima **vlastitu
> granu** da se može zasebno pregledati i mergeati. Cursor izvršava zadatke redom;
> gdje je potrebna urednička odluka (P1) — **STANI i ostavi u review, ne pogađaj**.
> Sve komande se pokreću iz `app/` osim ako nije drugačije navedeno.

---

## Sažetak (što je dijagnosticirano)

| # | Problem | Uzrok | Opseg (izmjereno) |
|---|---------|-------|-------------------|
| **P1** | `La Aroma del Caribe` = ista cigara kao `La Aroma de Cuba`, drugi naziv za EU/HR | Dvije zasebne marke u katalogu za isti fizički proizvod | 5 linija (del Caribe) + 8 linija (de Cuba) |
| **P2** | Cigare se prikazuju uz HR filter, a nisu u HR trgovinama | `availabilityHR` je bio **hardkodiran** (`["The Humidor","Havana Shop"]`) bez provjere; `markets` uključuje `"HR"` na temelju toga | **96** cigara: `HR` u `markets` + `availabilityHR` postavljen, ali **nula** HR product linkova |
| **P3** | Neki HR opisi/prijevodi su nerazumljivi | `describe-lines.py` generira HR bilješku s **engleskim** predloškom (`wrapper`, `Note:`) i **neprevedenim** tagovima (`zacini`, `koza`); + par ružnih brand blurbova | **175** cigara s HR bilješkom koja sadrži `wrapper`/`Note:` |

**Kako mehanizam radi (za kontekst):**
- Filter regije (`Sve · HR · EU · USA`) filtrira po `cigar.markets` — vidi
  `app/src/data/index.ts:225` (`cigarInRegion`). `"HR"` u `markets` = prikaži uz HR filter.
- Za **market** unose (`catalogSource:"market"`) `markets` se izvodi iz stvarnih
  scrapanih ponuda (`build-market-cigars.py:456` — `set(cigar_links.keys()) | {"WW"}`).
  Ti su **pouzdani** (HR se pojavi samo ako postoji HR ponuda).
- Za **kurirane** unose (`catalogSource` prazan) `availabilityHR` i `markets` su
  ručno/seed postavljeni (`enrich-cigars.py`, `sync-hr-shops.py:393,395`) i **HR je
  često hardkodiran bez izvora** — to je korijen P2.

---

## Redoslijed i grane

Sve radne grane se granaju **od `master`** (ne od grane plana). Redoslijed:

1. **P3** (`fix/cigar-notes-i18n-cleanup`) — najniži rizik, čisto tekst; mergea se prvi.
2. **P2** (`fix/cigar-hr-availability-truth`) — mijenja koje se cigare vide uz HR filter.
3. **P1** (`fix/la-aroma-brand-unify`) — **urednička odluka**, radi se zadnji, ostaje u review.

Svaka grana: `git fetch origin master && git checkout -B <grana> origin/master`.
Na kraju svake: `cd app && npx tsc -b --noEmit && npm test && npm run build`, zatim
`git push -u origin <grana>` i otvori PR prema `master`. **Ne mergeati bez review-a.**

---

## P3 — Popravak HR bilješki i prijevoda

**Grana:** `fix/cigar-notes-i18n-cleanup`

### Korijen
`app/scripts/describe-lines.py` → `generate()` (linije 170–182) koristi **isti**
predložak za HR i EN:
```python
hr = f"{wrapper} wrapper ({country}); {STRENGTH_HR...}."   # "wrapper" je engleski!
hr += f" Note: {tags_hr}."                                  # "Note:" engleski + tags_hr = sirovi ASCII tagovi
```
Rezultat u podacima (stvarni primjer, `cig-villa-zamorano-bouquet`):
> `notes.hr`: „Habano **wrapper** (Honduras); blaga prema srednjoj. **Note: cedar, zacini, koza**.”

Ispravan generator već postoji: `build-market-cigars.py` → `market_note()` (linije
131–147) radi točan HR: `„… pokrov — … snage, … tijela. Okusi: cedrovina, začini, koža.”`
(mapira tagove kroz `_TAG_HR`, linija 124).

### Zadaci

**T3.1 — Popravi `describe-lines.py` da generira ispravan hrvatski.**
- U `generate()` HR grani: `wrapper` → `pokrov`, `Note:` → `Okusi:`, i prevedi tagove.
- Ponovno iskoristi mapu tagova iz `build-market-cigars.py` `_TAG_HR` (kopiraj ili
  importaj) da HR tagovi budu s dijakriticima (`zacini`→`začini`, `koza`→`koža`,
  `cedar`→`cedrovina`, `orasasti`→`orašasti tonovi`, …).
- HR predložak uskladi s `market_note` stilom: `"{country}, {wrapper} pokrov — {snaga} snage, {tijelo} tijela. Okusi: {tags_hr}."`
- EN ostaje kako jest (`wrapper`, `Notes of …`) — EN je bio ispravan.

**T3.2 — Regeneriraj pogođene bilješke.**
- `describe-lines.py` obrađuje samo filler/kratke EN bilješke (`FILLER`/`SHORT_EN`,
  linija 158–159). **175 pogođenih** ima duži HR string pa neće proći taj filter.
  Dodaj granu koja hvata i **postojeći engleski leak u HR**: regex
  `r"\bwrapper\b|Note:"` u `note_hr` → tretiraj kao „treba regenerirati”.
- Pokreni: `cd app && python scripts/describe-lines.py`.
- **Verifikacija (mora biti 0):**
  ```bash
  python -c "import json,re; d=json.load(open('src/data/cigars.json')); \
  print(sum(1 for c in d if re.search(r'\bwrapper\b|Note:', (c.get('notes') or {}).get('hr',''))))"
  ```

**T3.3 — Ručni pregled brand blurbova s doslovnim strojnim prijevodom.**
- `app/src/data/brands.json`. Poznati loš primjer:
  `Villa Zamorano.blurb.hr` = „Maya Selva **'veliki osnovni'** …” (doslovni prijevod
  „grand basic”, besmisleno na HR). Predloži: „Maya Selva – *veliki osnovni model*”
  ili preformuliraj bez te fraze.
- Prođi `brands.json` i traži druge doslovne kalkove (jednostavan trijaž: usporedi
  `blurb.hr` i `blurb.en`; gdje HR izgleda kao riječ-za-riječ EN → označi). Napravi
  **listu prijedloga** u opisu PR-a; mijenjaj samo očite (ne prepisuj rukopis bez potrebe).
- **Ne dirati** `describe-lines.py` `CURATED` blok (to su ručno pisane, dobre bilješke).

**T3.4 — Provjeri EN da nema obrnutog leaka** (regresija iz commita `65a86f8`).
```bash
python -c "import json,re; d=json.load(open('src/data/cigars.json')); \
bad=['zacini','koza','orasasti','cedrovina','kremasto']; \
print(sum(1 for c in d if any(w in (c.get('notes') or {}).get('en','').lower() for w in bad)))"
# mora biti 0
```

### Prihvatljivost P3
- Gornje dvije provjere = **0**.
- `describe-lines.py` je idempotentan (drugi run ne mijenja ništa: `git diff --stat` prazan).
- `npm test` zelen (posebno `src/data/cigars.data.test.ts`, `curatedNotes.test.ts`).
- U PR opis: lista promijenjenih brand blurbova + broj regeneriranih bilješki.

---

## P2 — HR dostupnost mora odgovarati stvarnim HR trgovinama

**Grana:** `fix/cigar-hr-availability-truth`

### Načelo
Cigara smije imati `"HR"` u `markets` (i time se prikazati uz HR filter) **samo ako je
stvarno u ponudi** The Humidor ili Havana Cigar Shop. Trenutno **96** kuriranih cigara
ima `HR` bez ijednog HR product linka — hardkodirano u seedu (`enrich-cigars.py`,
`sync-hr-shops.py:393,395`).

> **Napomena o online prodaji:** online prodaja duhana u HR nije dozvoljena, linkovi su
> referentni (README). „Dostupno u HR” ovdje znači *marka/linija je u katalogu HR
> trgovine*, ne da se kupuje online. Izvor istine = živi katalozi humidor.hr + havana.

### Zadaci

**T2.1 — Snimi živi HR katalog (snapshot, provjerljiv).**
- Postoji fetcher: `sync-hr-shops.py` (`fetch_havana_catalog`, `fetch_humidor_catalog`).
  Izvuci samo dohvat + spremi sirovi popis u `app/scripts/output/hr_catalog_snapshot.json`
  (git-ignoriran ako je velik; ali commitaj **izvedeni set** — vidi T2.2).
- Ako mreža u Cursor okruženju ne dohvaća shopove: **STANI** i javi u PR-u; alternativa
  je da korisnik pokrene fetch lokalno i commita snapshot. Ne izmišljati dostupnost.

**T2.2 — Napravi `reconcile-hr-availability.py` (novi, deterministički).**
- Ulaz: `hr_catalog_snapshot.json` (sirovi nazivi proizvoda + URL-ovi iz oba shopa).
- Izgradi set stvarno prisutnih `(brand, line)` koristeći **postojeće** matchere iz
  `sync-hr-shops.py` (`detect_brand`, `line_name_from_product`, `norm`) — ne pisati novi
  fuzzy matcher.
- Za svaku cigaru u `cigars.json`:
  - Ako **market** unos (`catalogSource:"market"`): **ne dirati** — njegov HR je već
    izveden iz stvarnih ponuda.
  - Ako **kurirani** unos: `availabilityHR` = presjek sa stvarno prisutnima. Ako se
    ne poklopi ni s jednom HR trgovinom → `availabilityHR = []` i **makni `"HR"` iz
    `markets`** (ostavi EU/USA/WW kako jesu).
  - Ako ima stvaran HR product URL (`regionLinks.HR` ili `priceUrl` na humidor/havana
    hostu) → **zadrži HR** bez obzira na fuzzy match (tvrdi dokaz).
- **Idempotentno:** svaki run daje isti rezultat iz istog snapshota (kao playbook §0).
- **Izlaz za review:** `app/scripts/output/hr_reconcile_report.json` — popis cigara kojima
  je HR **maknut** (brand, line, prijašnji `availabilityHR`) da korisnik može provjeriti
  false-negativce prije mergea.

**T2.3 — Provjera integriteta.**
- Nakon reconcile-a: nijedna cigara ne smije imati `"HR"` u `markets` bez ili (a) HR
  product linka ili (b) matcha u snapshotu.
  ```bash
  python -c "import json; d=json.load(open('src/data/cigars.json')); \
  bad=[c for c in d if 'HR' in c['markets'] and not (c.get('regionLinks') or {}).get('HR') \
  and not c.get('availabilityHR')]; print('HR bez ikakvog izvora:', len(bad))"
  # cilj: 0
  ```
- Provjeri da `cigarCountByRegion.HR` (`index.ts:230`) padne na realan broj i da
  `src/data/integrity.test.ts` prolazi (ako testira markets/availability — provjeriti).

**T2.4 — UI konzistentnost (bez izmišljanja).**
- `DetailSheet.tsx` prikazuje „Dostupnost” i „KUPNJA / HRVATSKA” sekcije iz `markets` +
  `cigarShopLinks`. Nakon T2.2 te sekcije automatski nestaju za cigare bez HR. Provjeriti
  ručno na 2–3 primjera (npr. `cig-ashton-vsg`, `cig-cao-flathead`) da se ne prikazuje
  prazna HR sekcija ni „provjeri cijenu” bez izvora.

### Prihvatljivost P2
- T2.3 provjera = 0; `hr_reconcile_report.json` priložen u PR (broj maknutih + popis).
- `npm test`, `tsc -b`, `build` zeleni.
- **Review gate:** korisnik prolazi `hr_reconcile_report.json` i potvrđuje da maknute
  cigare stvarno nisu u HR (spot-check 5–10). Tek onda merge.

---

## P1 — Objediniti La Aroma del Caribe / de Cuba (UREDNIČKA ODLUKA)

**Grana:** `fix/la-aroma-brand-unify` — **radi zadnji, ostavi u review, ne mergeati bez potvrde.**

### Činjenice
- `brands.json` već priznaje vezu:
  - `La Aroma de Cuba` = Ashtonova (US) marka, miješa Pepín García (Nikaragva), 2002.
  - `La Aroma del Caribe` = „EU naziv za Ashtonovu La Aroma de Cuba; Edición Especial kod My Father”.
- Isti fizički proizvod, dva imena po tržištu (US: *de Cuba*, EU/HR: *del Caribe*).
- U katalogu: **8** linija pod „de Cuba” (uklj. `Edición Especial #5`) + **5** linija
  „del Caribe” (`Edición Especial No. 1/2/4/5/60`). Djelomično se preklapaju (Edición Especial).

### Opcije (korisnik bira — NE odlučivati sam)
- **Opcija A (preporuka): jedna marka + oznaka tržišnog naziva.**
  Kanonski `La Aroma de Cuba`; dodaj `La Aroma del Caribe` kao **alias/tržišni naziv za
  EU/HR** (novo polje na brandu ili u `cigarIdAliases.json`/`renameBrand` mehanizmu).
  Del-Caribe Edición Especial linije mapiraj na de-Cuba ekvivalente gdje su iste; EU
  `regionLinks` se prenose. Rezultat: korisnik ne vidi dvije „iste” marke.
- **Opcija B: zadrži dvije marke, ali dodaj vidljivu unakrsnu napomenu** u obje blurbe i
  u `DetailSheet` (npr. „prodaje se kao *La Aroma de Cuba* u SAD-u”). Manje posla, ali
  duplikat ostaje u popisu marki.
- **Opcija C: del Caribe kao linija unutar de Cuba** (ako se tržišni nazivi žele u jednoj
  hijerarhiji). Najviše restrukturiranja `markets`/linkova — vjerojatno pretjerano.

### Zadaci (za odabranu opciju — pretpostavka A dok korisnik ne kaže drugačije)
**T1.1 — Istraži i mapiraj linije 1:1.**
- Napravi tablicu del Caribe ↔ de Cuba (koja je Edición Especial koja; koji wrapper/format).
  Provjeri protiv `HABANOS`/`renameBrand` konvencija (`app/scripts/` + `git log` za
  `renameBrand` iz commita `fafca5c`).
**T1.2 — Implementiraj spajanje kroz postojeći mehanizam.**
- Iskoristi **taksonomijski/rename** put koji već postoji (vidi `apply-taxonomy.py`,
  `cigarIdAliases.json`, commit `fafca5c` „renameBrand mappings”) umjesto ručnog editiranja
  `cigars.json` — tako ostaje deterministički i preživi regeneraciju.
- Sačuvaj EU `regionLinks` (del Caribe ima EU ponude) na objedinjenim unosima da se EU
  dostupnost ne izgubi.
**T1.3 — Ažuriraj `brands.json`** (ukloni ili preusmjeri `La Aroma del Caribe` po opciji).
**T1.4 — `cigarIdAliases.json`**: stari `cig-la-aroma-del-caribe-*` ID-jevi → novi, da
  deep-linkovi (`#/pairing/cigar/<id>`) i spremljena kolekcija u localStorage ne puknu.

### Prihvatljivost P1
- Nema dvije marke „La Aroma …” u `BRAND_INDEX` osim ako je odabrana Opcija B.
- EU dostupnost/linkovi sačuvani; stari ID-jevi aliasirani (nema mrtvih deep-linkova).
- `npm test` (posebno `taxonomyNav.test.ts`, `cigars.data.test.ts`, integrity) zelen.
- **Ostaje u review** dok korisnik ne potvrdi opciju i tablicu mapiranja iz T1.1.

---

## P4 — Revizija CIJELOG korpusa (isti problemi kod ostalih cigara)

**Grana:** `fix/cigar-corpus-audit`
**Radi se nakon P1–P3** (jer P1–P3 pokrivaju najgore poznate slučajeve); P4 je
sustavni sweep da se **isti razredi grešaka nađu i kod svih ostalih ~2395 cigara** i
svih marki. P1/P2/P3 su bili *primjeri* — pretpostavka je da problema ima šire.

> **Princip:** ne popravljati samo prijavljene stavke, nego **klasu problema** kroz cijeli
> `cigars.json` + `brands.json`. Sve što nije očito/deterministički → u **review report**,
> ne pogađati.

### T4.1 — Sweep duplih marki / tržišnih naziva (klasa P1)
La Aroma de Cuba/del Caribe vjerojatno nije jedini slučaj „ista cigara, dva imena po
tržištu” ili „ne-kubanski imenjak kubanske marke”.
- Generiraj kandidate: (a) marke sa sličnim korijenom naziva (npr. `Flor de …`,
  `San Cristóbal`, `Padrón`/`Padron`, `La Gloria …`), (b) ne-kubanski imenjaci Habanos
  marki (`(NW)`, „Non-Cuban”), (c) marke iste zemlje + istog blend/proizvođača u blurbu.
- Alat: skripta koja grupira po normaliziranom nazivu (`norm()` iz `sync-hr-shops.py`) i
  po proizvođaču spomenutom u `brands.json` blurbu; ispiši u `output/brand_dupe_candidates.json`.
- **Izlaz = lista kandidata za review**, ne automatski merge (svaki spoj je urednička
  odluka kao P1).

### T4.2 — Sweep dostupnosti kroz SVE regije (klasa P2)
P2 je gledao samo HR. Isti hardkod-rizik postoji za **EU i USA** kod kuriranih unosa.
- Za svaku regiju (`HR`, `EU`, `USA`) provjeri: ima li cigara `markets` unos bez ijednog
  odgovarajućeg `regionLinks[region]` **i** bez drugog dokaza (product URL na hostu te regije)?
- EU/USA izvor istine = scrapani `regionLinks` iz `build-market-cigars` pipelinea
  (CigarWorld / Holt's / Cigars Daily). Kurirani unosi bez tih linkova, a s regijom u
  `markets`, idu u report.
- Izlaz: `output/markets_audit_report.json` po regiji (koliko „bez izvora”, popis). Miči
  neutemeljene regije po istom pravilu kao T2.2; sporno → review.
- Provjeri i **obrnuto**: cigare koje IMAJU `regionLinks[region]` ali nemaju regiju u
  `markets` (izgubljena dostupnost).

### T4.3 — Sweep bilješki i prijevoda kroz cijeli korpus (klasa P3)
Prošire T3 provjere na sve moguće leakove i loše prijevode, u oba smjera:
- **HR polje sadrži engleski:** regex `\bwrapper\b|Note:|Notes of|mild|medium|full-bodied|
  spice\b|leather\b|smooth\b` u `notes.hr`.
- **EN polje sadrži hrvatski / neprevedene tagove:** `pokrov|snage|tijela|Okusi|zacini|
  koza|orasasti|cedrovina|kremasto|začini|koža` u `notes.en`.
- **Neprevedeni ASCII tagovi u `flavorTags`** koji se prikazuju bez mapiranja (usporedi s
  `_TAG_HR` i EN mapom; nađi tagove bez prijevoda u nekoj od mapa).
- **Strojni kalkovi u `brands.json` blurbovima:** heuristika „HR ≈ riječ-za-riječ EN”
  (podudaranje redoslijeda tokena, doslovni prijevodi idioma tipa „veliki osnovni”,
  „velika osnovna”). Ispiši par HR/EN za ručni trijaž u `output/blurb_translation_review.json`.
- **Prazne/šum bilješke:** `notes.hr`/`notes.en` prazni, „Sinkronizirano iz HR trgovina”,
  „Dostupno u HR”, ili identični HR==EN (znak da prijevod nije napravljen).
- **HTML/enkoding artefakti:** `&amp;`, `&quot;`, dvostruki razmaci, `#N` ostaci u
  `line`/`vitola`/`notes` (primjer: `7-20-4 | Hustler Five &amp; Dime`). Dekodiraj entitete.
- Regeneriraj kroz ispravljeni `describe-lines.py` (T3.1) gdje je moguće; ostalo (blurbovi,
  imena linija) u review.
- **Ciljne provjere = 0** za sve gornje regexe nakon popravka (dokumentiraj u PR-u).

### T4.4 — Ostale konzistentnosti (oportunistički, dok se već prolazi korpus)
- `country` vrijednosti: dosljedni HR nazivi (`Nikaragva`, ne `Nicaragua`; `Dominikanska
  Republika`, ne `Dominikana`) — `sync-hr-shops.py:385` npr. koristi „Dominikana”.
- `wrapper` `"—"` placeholderi na kuriranim unosima koji imaju stvaran wrapper drugdje.
- `smokeTimeMin`/`format` očiti outlieri (npr. 0 ili >180 min, ring izvan 30–80).
- Sve nalaze koji nisu očit auto-fix → `output/corpus_audit_findings.md` za review.

### Prihvatljivost P4
- Svi sweep-report fileovi priloženi u PR (`brand_dupe_candidates.json`,
  `markets_audit_report.json`, `blurb_translation_review.json`, `corpus_audit_findings.md`).
- Auto-popravljive klase (leak regexi, HTML entiteti, country normalizacija) = **0**
  preostalih; verifikacijski one-lineri u PR opisu.
- Uredničke odluke (dupli brendovi, sumnjiva dostupnost, prepisivanje blurbova) **ostaju
  u review** s jasnim popisom — ne mergeati te dijelove bez korisnikove potvrde.

---

## Novi problemi koji iskrsnu tijekom rada

Ako Cursor tijekom bilo kojeg zadatka naiđe na problem koji **nije** u ovom planu:
1. **Ako je očit, deterministički i niskorizičan** (npr. još jedan enkoding artefakt,
   očita greška u tipu podatka) — **sanira ga** u sklopu odgovarajuće grane i **zabilježi**
   u `output/corpus_audit_findings.md` (što je bilo, kako je popravljeno).
2. **Ako je urednički/dvosmislen ili mijenja što korisnik vidi** (spajanje marki, micanje
   dostupnosti, prepisivanje teksta) — **NE dira**, nego zapiše u findings s prijedlogom i
   ostavi za review.
3. Ako otkriće ruši pretpostavku ovog plana (npr. `markets` se negdje računa drukčije) —
   **STANI**, zapiši, i nastavi s ostalim zadacima koji nisu blokirani.

Cilj: nijedan nalaz se ne gubi. Findings datoteka je jedinstveni dnevnik za review sutra.

---

## Globalna verifikacija (svaka grana prije push-a)

```bash
cd app
npx tsc -b --noEmit          # lint gate
npm test                     # Vitest
npm run build                # tsc -b && vite build
```

Regeneracijske skripte moraju ostati **idempotentne** (drugi run → prazan `git diff`).
Ako neka provjera ne prolazi deterministički — **STANI i pitaj**, ne improviziraj podatke.

## Što review sutra provjerava (checklist za korisnika)
- [ ] **P3:** otvori par cigara koje su prije bile loše (Villa Zamorano Bouquet, Aganorsa
      Arsenio) — HR bilješka je čisti hrvatski, bez „wrapper”/„Note:”.
- [ ] **P2:** upali HR filter → prođi listu; `hr_reconcile_report.json` spot-check 5–10
      maknutih (jesu li stvarno odsutne iz HR trgovina).
- [ ] **P1:** potvrdi opciju (A/B/C) i tablicu mapiranja del Caribe ↔ de Cuba prije mergea.
- [ ] **P4:** prođi sweep-reporte — dupli brendovi (kandidati), dostupnost po EU/USA
      (bez izvora), lista blurbova za prijevod, `corpus_audit_findings.md`. Potvrdi
      uredničke odluke; auto-fix klase provjeri da su 0.
