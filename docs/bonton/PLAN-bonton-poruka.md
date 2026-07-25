# PLAN — vodeća poruka bontona (app + knjiga)

> **Namjena:** ovaj dokument je izvršni plan za **Cursor agenta (lokalno)**. Sadrži točan
> tekst za copy-paste, mjesta izmjena, redoslijed i provjere. Ništa se ne pogađa —
> svi finalni stringovi su ispod.
>
> **Repo:** `ivsitum1/cigar-pairing` · **Grana za rad:** `claude/bonton-app-message-q4tx7n`
> **Agent-rules repo:** koristi se **samo kao pravila / referenca — NE mijenjati.**

---

## 1. Cilj (poruka koju šaljemo)

Bonton treba **voditi** ovom tezom, a ne samo je nagovještavati:

> **HR:** Prvo i najvažnije: uljudnost i pažnja. Ne postoji ispravno ili krivo — ako
> nekome nešto odgovara, a ne narušava tuđe uživanje, to je u redu.
>
> **EN:** First and above all: courtesy and care. There is no right or wrong — if
> something suits someone and does not spoil another's enjoyment, it is fine.

Ovo je **kanonska formulacija**. Koristi je doslovno gdje god plan traži „tezu".
Postojeći tekst ("Bonton nije policija ukusa", "nema 'prave' marke") ostaje — teza mu
je nadređena, ne zamjena.

## 2. Gdje poruka mora biti vidljiva

| # | Površina | Datoteka | Obavezno? |
|---|----------|----------|-----------|
| A | App: epigraf (landing bonton ekrana) | `app/src/data/bonton.json` → `epigraph` | ✅ obavezno |
| B | App: I. poglavlje "Duh bontona" | `app/src/data/bonton.json` → `b-spirit.body` | ✅ obavezno |
| C | App: teaser na Club kartici | `app/src/i18n/index.tsx` → `club.bontonTeaser` | ⭐ preporučeno |
| D | Knjiga (app-kanon): Epigraf + I. Duh bontona (HR i EN dio) | `docs/bonton/mala-knjiga-pusackog-bontona.md` | ✅ obavezno |
| E | Knjiga (puni rukopis HR): Epigraf + "Kako čitati" + gl. 1 | `docs/bonton/KAKO-BITI-GOSPODIN-ZA-STOLOM-DRAFT.md` | ✅ obavezno |
| F | Knjiga (puni rukopis EN): Epigraph + "How to read" + ch. 1 | `docs/bonton/HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md` | ✅ obavezno |

> **Napomena o duplikaciji:** epigraf (A) i preview I. poglavlja pojavljuju se na
> **istom** ekranu. Zato tezu stavljamo u **epigraf**, a u tijelo I. poglavlja kao
> **drugi odlomak** (ne prvu liniju) — tako `preview()` i dalje pokazuje "Bonton nije
> policija ukusa…", pa ista rečenica nije dvaput na ekranu.

---

## 3. Izmjene — točan tekst

### A. `app/src/data/bonton.json` → `epigraph`

**Zamijeni cijeli `epigraph` objekt:**

```json
  "epigraph": {
    "hr": "Prvo i najvažnije: uljudnost i pažnja. Ne postoji ispravno ili krivo — ako nekome nešto odgovara, a ne narušava tuđe uživanje, to je u redu. Po uzoru na klasične britanske knjige bontona: kratka pravila ljubaznosti za stol s cigarom i čašom.",
    "en": "First and above all: courtesy and care. There is no right or wrong — if something suits someone and does not spoil another's enjoyment, it is fine. In the spirit of classic British etiquette books: short rules of courtesy for a table with a cigar and a glass."
  },
```

### B. `app/src/data/bonton.json` → `b-spirit.body`

Umetni tezu kao **drugi odlomak** (odmah nakon prve rečenice, prije `Temelji`).
Praktično: u vrijednosti `body.hr` i `body.en` nakon `…dok ti uživaš.\n\n` ubaci
tezu + `\n\n`.

**Novi `body.hr` (početak — ostatak "Temelji…" ostaje nepromijenjen):**

```
Bonton nije policija ukusa. To je način na koji drugi lakše dišu dok ti uživaš.\n\nPrvo i najvažnije: uljudnost i pažnja. Ne postoji ispravno ili krivo — ako nekome nešto odgovara, a ne narušava tuđe uživanje, to je u redu.\n\nTemelji\n• Pažnja — …
```

**Novi `body.en` (početak):**

```
Manners are not the police of taste. They are how others can breathe easier while you enjoy yourself.\n\nFirst and above all: courtesy and care. There is no right or wrong — if something suits someone and does not spoil another's enjoyment, it is fine.\n\nFoundations\n• Attention — …
```

> ⚠️ Ne diraj `Temelji…` / `Foundations…` i `Zlatno pravilo` / `Golden rule` sekcije —
> one moraju ostati (test traži barem jednu sekciju po poglavlju).

### C. `app/src/i18n/index.tsx` → `club.bontonTeaser` (preporučeno)

**Zamijeni:**

```ts
  "club.bontonTeaser": {
    hr: "Mala knjiga manira za stol s cigarom i čašom — bez ispravnog i krivog, samo uljudnost i pažnja u jedanaest kratkih poglavlja.",
    en: "A short book of manners for the cigar-and-glass table — no right or wrong, just courtesy and care across eleven short chapters.",
  },
```

> Ako izvorni `en` string ima drukčiji tekst, zadrži isti stil; ključno je unijeti
> "no right or wrong / courtesy and care".

### D. `docs/bonton/mala-knjiga-pusackog-bontona.md`

Ovo je HR kanon + EN referenca u istoj datoteci. **Dvije izmjene po jeziku.**

**D1 — HR Epigraf** (odjeljak `## Epigraf`, oko lin. 10). Zamijeni odlomak:

```md
Prvo i najvažnije: uljudnost i pažnja. Ne postoji ispravno ili krivo — ako nekome nešto odgovara, a ne narušava tuđe uživanje, to je u redu.

Po uzoru na klasične britanske knjige bontona: kratka pravila ljubaznosti, napisana za stol s cigarom i čašom.
```

**D2 — HR "I. Duh bontona"** (oko lin. 18). Nakon rečenice
`Bonton nije policija ukusa. To je način da drugi udišu lakše dok ti uživaš.` umetni
novi odlomak:

```md
Prvo i najvažnije: uljudnost i pažnja. Ne postoji ispravno ili krivo — ako nekome nešto odgovara, a ne narušava tuđe uživanje, to je u redu.
```

**D3 — EN Epigraph** (odjeljak `## Epigraph`, oko lin. 281). Zamijeni odlomak:

```md
First and above all: courtesy and care. There is no right or wrong — if something suits someone and does not spoil another's enjoyment, it is fine.

In the spirit of classic British etiquette books: short rules of courtesy, written for a table with a cigar and a glass.
```

**D4 — EN "I. The spirit of manners"** (oko lin. 287). Nakon
`Manners are not the police of taste. They are how others can breathe easier while you enjoy yourself.` umetni:

```md
First and above all: courtesy and care. There is no right or wrong — if something suits someone and does not spoil another's enjoyment, it is fine.
```

### E. `docs/bonton/KAKO-BITI-GOSPODIN-ZA-STOLOM-DRAFT.md` (HR rukopis)

**E1 — Epigraf** (odjeljak `### Epigraf`, oko lin. 18–24). Dodaj tezu kao **prvi**
blockquote, iznad postojećih:

```md
> Prvo i najvažnije: uljudnost i pažnja. Ne postoji ispravno ili krivo — ako nekome nešto odgovara, a ne narušava tuđe uživanje, to je u redu.

> Bonton nije policija ukusa. To je način da drugi udišu lakše dok ti uživaš.

> Gospodin je osoba koja život drugih čini ugodnijim. — parafrazirano iz duha klasičnih vodiča uljudnosti
```

**E2 — "Kako čitati ovu knjigu"** (oko lin. 28). Trenutačno počinje
`Ovo nije ispit. Nema ocjena, nema „prave" marke, nema kazne za krivi rez.` — dodaj
rečenicu odmah iza nje, u istom odlomku:

```md
Ovo nije ispit. Nema ocjena, nema „prave” marke, nema kazne za krivi rez. Prvo i najvažnije jest uljudnost i pažnja: ne postoji ispravno ili krivo — ako nekome nešto odgovara, a ne narušava tuđe uživanje, to je u redu.
```

**E3 — gl. 1 "Što bonton nije"** (oko lin. 101–109). Kao završni odlomak sekcije dodaj:

```md
Ukratko: nema ispravnog ni krivog. Ako nekome nešto odgovara, a ne kvari tuđe uživanje, to je u redu — mjera je pažnja prema drugima, ne pravilnik.
```

### F. `docs/bonton/HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md` (EN rukopis)

**F1 — Epigraph** (odjeljak `### Epigraph`, oko lin. 24–30). Dodaj kao prvi blockquote:

```md
> First and above all: courtesy and care. There is no right or wrong — if something suits someone and does not spoil another's enjoyment, it is fine.

> Etiquette is not the police of taste. It is a way for others to breathe more easily while you enjoy yourself.

> A gentleman is a person who makes the lives of others more pleasant. — paraphrased from the spirit of the classic guides to courtesy
```

**F2 — "How to read this book"** (oko lin. 32). Prošири prvu rečenicu:

```md
This is not an exam. There are no grades, no "correct" brand, no penalty for a bad cut. First and above all it is courtesy and care: there is no right or wrong — if something suits someone and does not spoil another's enjoyment, it is fine.
```

**F3 — ch. 1 "What a gentleman at the table is"** (sekcija ekvivalentna "Što bonton nije").
Kao završni odlomak dodaj:

```md
In short: there is no right or wrong. If something suits someone and does not spoil another's enjoyment, it is fine — the measure is care for others, not a rulebook.
```

---

## 4. Redoslijed izvršenja

1. `git checkout claude/bonton-app-message-q4tx7n` (grana već postoji na remoteu; ako
   nije lokalno: `git fetch origin && git checkout -b claude/bonton-app-message-q4tx7n origin/claude/bonton-app-message-q4tx7n`).
2. Primijeni **A, B** (app JSON) — najkritičnije, jer test i UI ovise o njima.
3. Primijeni **C** (i18n), pa **D** (kanon md), pa **E, F** (rukopisi).
4. Provjere (dio 5).
5. Commit + push (dio 6).

## 5. Provjere (obavezno, iz `app/`)

```bash
cd app
npx tsc -b --noEmit      # typecheck / lint gate
npm test                 # Vitest — bonton.test.ts mora ostati zelen (11 poglavlja, sekcije)
npm run build            # opcionalno, potvrda buildabilnosti
```

Ručna provjera UI-ja (opcionalno): `npm run dev` → otvori
`http://localhost:5173/cigar-pairing/` → Klub → Bonton. Potvrdi:
- epigraf na vrhu prikazuje tezu (HR i EN, prebaci jezik);
- kartica I. poglavlja i dalje ima preview "Bonton nije policija ukusa…";
- otvaranjem I. poglavlja teza je vidljiva kao drugi odlomak.

## 6. Commit i push

```bash
git add app/src/data/bonton.json app/src/i18n/index.tsx \
        docs/bonton/mala-knjiga-pusackog-bontona.md \
        docs/bonton/KAKO-BITI-GOSPODIN-ZA-STOLOM-DRAFT.md \
        docs/bonton/HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md \
        docs/bonton/PLAN-bonton-poruka.md
git commit -m "bonton: vodeća poruka — uljudnost i pažnja, nema ispravnog/krivog (app + knjiga)"
git push -u origin claude/bonton-app-message-q4tx7n
```

> **PR:** ne otvaraj automatski osim ako korisnik zatraži. `master` se deploya na
> GitHub Pages, pa promjena ide u produkciju tek nakon mergea u `master`.

## 7. Napomene / ograničenja (iz projektnih pravila)

- **Ne** dirati `agent-rules` repo (samo referenca).
- Zadržati postojeći dvojezični ton (HR kanon, EN zrcalo); em-crta i epigramski ritam
  su namjerni.
- Ne uvoditi nove ovisnosti, ne mijenjati broj/ID-eve poglavlja (test to provjerava).
- Autorstvo/voice: inkluzivno (domaćin/gost), humor na snobizam a ne na početnika —
  teza to pojačava, ne proturječi joj.
