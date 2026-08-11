# NOTICE — licence i atribucije

Ovaj repo nije samo softver. Kod, urednički sadržaj i tuđi materijali imaju
različite licence, pa je ovo mjerodavna karta: **što je pod čim**.

Copyright © 2026 `ivsitum1` (ivsitum@gmail.com), osim gdje je drukčije
navedeno.

| Dio | Licenca | Datoteka |
|-----|---------|----------|
| Izvorni kod | **AGPL-3.0-only** | [`LICENSE`](LICENSE) |
| Sadržaj i podaci | **CC BY-NC-SA 4.0** | [`LICENSE-CONTENT`](LICENSE-CONTENT) |
| Materijali trećih strana | vlastite licence | popis niže |

---

## 1. Kod — GNU AGPL-3.0-only

Pokriva:

- `app/src/**` — **osim** `app/src/data/`
- `app/scripts/**` (Python pipeline, `build-world-outline.mjs`)
- `backend/**` (opcionalni FastAPI OCR servis)
- konfiguracije: `app/vite.config.ts`, `app/tsconfig*.json`, `app/eslint*`,
  Tailwind postava
- `.github/workflows/**`

AGPL je *copyleft s mrežnom klauzulom*: tko god ovaj kod (ili izvedeni rad)
ponudi korisnicima preko mreže — uključujući hostanje kao web aplikacije —
mora tim korisnicima učiniti dostupnim potpuni izvorni kod svoje verzije, pod
istom licencom. Zato podnožje aplikacije nosi vidljivu poveznicu na ovaj repo
(AGPLv3 §13).

## 2. Sadržaj i podaci — CC BY-NC-SA 4.0

Pokriva:

- `app/src/data/**/*.json` — indeksi cigara i pića, te urednički Club slojevi
  (`club101.json`, `lexicon.json`, `hrGuide.json`, `eveningArchetypes.json`,
  `bonton.json`, `club.json`, `clubSources.json`)
- `docs/**` — dokumentacija i uredničke bilješke
- `marketing/**`
- `README.md`, `AGENTS.md`

Smiješ dijeliti i prerađivati **uz atribuciju**, **nekomercijalno**, i uz
**dijeljenje pod istim uvjetima**. Nositelj autorskog prava nije vezan
vlastitom licencom i zadržava pravo isti sadržaj licencirati komercijalno pod
zasebnim uvjetima.

### 2.1. AGPL vrijedi za kod, ne za podatke

Ovo je namjerno i ne treba ostati dvosmisleno: datoteke u `app/src/data/` su
**zasebno djelo agregirano s programom**, a ne dio njegova izvornog koda. AGPL
grant ih ne pokriva. Fork smije kod koristiti i komercijalno (uz AGPL obveze),
ali **mora donijeti vlastite podatke** — indeksi cigara i pića iz ovog repoa ne
idu uz njega u komercijalnu upotrebu.

### 2.2. Pravo na bazu podataka (EU)

Neovisno o CC licenci, na kompilaciju indeksa primjenjuje se *sui generis*
pravo proizvođača baze podataka (Direktiva 96/9/EZ, u HR Zakon o autorskom
pravu i srodnim pravima). CC BY-NC-SA 4.0 to pravo izričito licencira pod istim
uvjetima — vidi Section 4 u [`LICENSE-CONTENT`](LICENSE-CONTENT).

## 3. Izvan obje licence — materijali trećih strana

Sljedeće **nije** naše i ne prenosi se ni AGPL-om ni CC licencom:

| Materijal | Nositelj / licenca |
|-----------|--------------------|
| `app/public/music/*` — *Night in Venice*, *No Frills Cumbia* | Kevin MacLeod (incompetech.com), **CC BY 4.0** — vidi [`app/public/music/CREDITS.md`](app/public/music/CREDITS.md) |
| Fontovi Manrope i Marcellus (`@fontsource-variable/manrope`, `@fontsource/marcellus`) | **SIL Open Font License 1.1** |
| Obris kopna u `app/src/data/world_outline.json` | izvedeno iz Natural Earth preko `world-atlas@2`, **public domain** — vidi zaglavlje [`app/scripts/build-world-outline.mjs`](app/scripts/build-world-outline.mjs) |
| npm i pip ovisnosti | vlastite licence (React/Vite/Tailwind/Vitest MIT; `tesseract.js` i `@paddleocr/paddleocr-js` Apache-2.0; FastAPI/uvicorn MIT; PaddleOCR Apache-2.0) |

Sve navedene licence su kompatibilne s AGPL-3.0 za ovu upotrebu (Apache-2.0 je
jednosmjerno kompatibilan s AGPLv3).

### 3.1. Nazivi, marke i cijene

Nazivi cigara, pića, marki i trgovina su **žigovi svojih vlasnika** i nisu
predmet nijedne licence iz ovog repoa. Aplikacija nije povezana ni s jednom
trgovinom ni markom. Cijene i dostupnost su prikupljene iz javnih izvora,
orijentacijske su i podložne promjeni.

### 3.2. Rukopis knjige

Rukopis *Gospodin za stolom / How to Be a Gentleman at the Table* i pripadajući
istraživački materijal **nisu** dio ove grane i **nisu** pokriveni nijednom
licencom iz ovog repoa. Sva prava pridržana. Rad na knjizi živi na zasebnim
granama; vidi [`docs/bonton/CROSSWALK.md`](docs/bonton/CROSSWALK.md).

---

## 4. Kako atribuirati

Za sadržaj pod CC BY-NC-SA 4.0:

> Podaci i tekstovi iz projekta *Cigar & Pairing*
> (https://github.com/ivsitum1/cigar-pairing), © ivsitum1,
> licencirano pod CC BY-NC-SA 4.0.

Za kod je dovoljno zadržati obavijesti o autorskom pravu i licenci te uz
izvedeni rad ponuditi izvorni kod, kako AGPL-3.0 traži.
