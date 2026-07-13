# Neutralne ocjene i deklaracija dodataka + vino u pairingu — plan implementacije

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** App postaje neutralan i informativan — ni "anti-aditiv" ni navijački. Sve
što ima dodatke ostaje (i vraća se) na popis, s jasnom činjeničnom deklaracijom
*što je dodano* i s neovisnom ocjenom kvalitete unutar vlastitog stila. Don Papa
i Bumbu se razdvajaju u zasebne zapise s maksimalno informacija (izmjerene
vrijednosti šećera, ABV, EU klasifikacija). Za whisky i konjak/brandy pišu se
neutralna objašnjenja *drugačijih pravila* (što je zakonski dopušteno dodati).
Dodaje se nova kategorija **vino** u pairing, po istom principu punoće (body).

**Architecture:** Sve ostaje klijentski, bez novih ovisnosti. Podaci u
`src/data/*.json`; ton i pairable-status se mijenjaju izravno u JSON-ima, a
neutralne izmjene se dokumentiraju u override tablici
(`scripts/neutral_overrides.json` + `scripts/apply-neutral-overrides.py`) da se
mogu ponovno primijeniti nakon eventualne regeneracije iz Excela. Vino je nova
`DrinkCategory` — engine radi bez izmjena logike (body/sweetness/tagovi), samo
se proširuju `WRAPPER_AFFINITY` stilovi i UI tabovi.

**Tech Stack:** React 19 + Vite + TS + Tailwind, vitest. Bez novih npm ovisnosti.

## Načela neutralnosti (uređivačka politika)

1. **Deklaracija, ne osuda.** `additiveStatus`/`additiveDetail` navode *što* je
   dodano i *koliko* (izmjereno g/L gdje postoji javni izvor: Systembolaget,
   hidrometrijska mjerenja, lab testovi), s izvorom u `additiveSource`.
2. **Ocjena unutar stila.** `qualityScore` je neovisna procjena kvalitete
   *unutar vlastite kategorije/stila* (agregat javnih ocjena i recenzija) —
   dodaci se ne kažnjavaju u ocjeni, nego se transparentno deklariraju.
3. **Sve je pairable.** Engine ocjenjuje spoj po tijelu/slatkoći/okusima;
   korisnik bira. Nema "ne za cigaru" — umjesto toga engine pošteno objasni
   kad se profili ne slažu.
4. **Bez vrijednosnih etiketa** u podacima i UI-ju: briše se "jeftini",
   "precijenjeno", "ne za cigaru", "purist" i sl.; zamjenjuje činjeničnim
   opisima ("rum za miješanje", "slađen/aromatiziran profil").
5. **Različita pravila po kategoriji** — neutralno objašnjeno u appu:
   - **Rum (EU):** smije imati do 20 g/L dodanog šećera i zvati se "rum"
     (Uredba EU 2019/787); iznad toga je "spirit drink". Mjerenja se navode.
   - **Whisky (EU/Scotch):** zabranjeno doslađivanje i aromatiziranje; dopušten
     samo karamel E150a za boju (+ voda). Aromatizirane varijante (JD Honey…)
     zakonski nisu whisky nego liker/spirit drink — navodi se bez osude.
   - **Konjak/Armagnac:** tradicionalno dopušteni šećer, E150a i boisé
     (infuzija hrastovih strugotina), ukupno do 4% obskuracije (~15 g/L),
     bez obveze deklaracije na etiketi.
   - **Gin:** London Dry ne smije ništa dodati nakon destilacije (šećer
     ≤0,1 g/L); ostali ginovi smiju (sladili/aromatizirani se deklariraju).
   - **Vino:** sulfiti su standard vinarstva; fortificirana vina (porto,
     sherry…) imaju dodani vinski destilat — deklarira se neutralno.

## Global Constraints

- Komentari u kodu na hrvatskom, kratki, u stilu postojećeg koda.
- Bez novih npm ovisnosti. Testovi: `cd app && npm test`; build `npm run build`.
- Dvojezičnost: svaki novi UI string u `i18n/index.tsx` (hr + en); podaci
  `notes` barem hr.
- Cijene: HR tržište; gdje nema točne cijene → `priceApprox: true` + raspon.
- Commit poruke engleski, s Co-Authored-By trailerom kao u povijesti.

---

### Task 1: Neutralni ton — i18n i UI

**Files:** `app/src/i18n/index.tsx`, `app/src/components/cards.tsx`,
`app/src/components/DetailSheet.tsx`, `app/src/pages/CatalogPage.tsx`

- [ ] `STYLE_LABELS`: maknuti "(ne za cigaru)" iz `spiced`, `liqueur`,
      `flavored`; neutralna imena ("Spiced / aromatiziran", "Liker",
      "Aromatiziran").
- [ ] `ADDITIVE_LABELS`: dodati `fortified` (Fortificirano). Postojeće etikete
      ostaju (činjenične su).
- [ ] Novi i18n blok `additiveRules.<category>` (rum/whisky/brandy/gin/wine) —
      neutralan tekst pravila po kategoriji (gore navedena načela br. 5).
- [ ] `rate.qualityWhat` → nova formulacija: "Neovisna procjena kvalitete
      (1–10) unutar vlastitog stila — agregat javnih ocjena i recenzija.
      Dodaci se ne kažnjavaju u ocjeni, nego se zasebno deklariraju."
- [ ] `cards.tsx` `DrinkRow`: prikaz `additiveStatus` za **sve** kategorije
      (ne samo rum).
- [ ] `DetailSheet.tsx` `DrinkDetails`: ispod retka "Aditivi" prikazati mali
      info tekst `additiveRules.<drink.category>`.
- [ ] `CatalogPage.tsx`: chip "Samo čisti (bez aditiva)" dostupan na svim
      drink tabovima osim kave.

### Task 2: Neutralizacija podataka + Don Papa & Bumbu

**Files:** `app/src/data/rums.json`, `app/src/data/whiskies.json`,
`app/src/data/brandies.json`, `scripts/neutral_overrides.json`,
`scripts/apply-neutral-overrides.py`

- [ ] Override tablica po `id`: novi `notes.hr/en`, `additiveDetail`,
      `additiveSource`, `qualityScore`, `pairable: true`, `region` (gdje je
      bio vrijednosni tekst poput "PRECIJENJENO/slazeno").
- [ ] Svi rum zapisi `pairable: false` → `true`; note bez "ne za cigaru",
      "jeftini", "mixer" pežorativa; qualityScore rekalibriran unutar stila
      (spiced/liker ocjenjivan kao spiced/liker, ne kao sipping rum).
- [ ] **Don Papa**: razdvojiti kombinirani zapis na "Don Papa 7" i "Don Papa
      Baroko"; podaci: ABV 40%, lab mjerenja ~29 g/L šećera + 2,4 g/L
      glicerola + vanilin ~360 mg/L (izvor: objavljeni lab/hidrometrijski
      testovi), HR cijena i link (allez.hr), opis profila (vanilija, suho
      voće, desertni stil), serviranje, EU napomena (>20 g/L → "spirit
      drink" na EU etiketi gdje vrijedi).
- [ ] **Bumbu**: razdvojiti na "Bumbu Original" (Systembolaget ~51 g/L šećera;
      EU boca 40%, US 35%) i "Bumbu XO" (~19 g/L; Panama solera baza), HR
      cijene/linkovi, profil (vanilija, karamela, banana), serviranje.
- [ ] Whisky: ispraviti krive copy-paste bilješke za JD Apple/Honey/Honey
      Liqueur i Teeling Pineapple; `pairable: true`; neutralno "aromatizirani
      liker na bazi whiskeyja — EU: spirit drink"; realna ocjena unutar stila.
- [ ] Brandy/whisky `additiveDetail` provjeriti da su činjenični (E150a,
      boisé, chill-filtracija) — bez promjene značenja.
- [ ] `apply-neutral-overrides.py`: idempotentno primjenjuje overrides na
      JSON-e (za slučaj regeneracije iz Excela).

### Task 3: Vino — podaci

**Files:** `app/src/data/wines.json` (novo), `app/src/types.ts`,
`app/src/data/index.ts`, `app/src/i18n/index.tsx`

- [ ] `types.ts`: `DrinkCategory` += `"wine"`.
- [ ] `wines.json`: ~45–55 zapisa, kategorije po punoći:
  - fortificirana (porto ruby/LBV/tawny 10&20/vintage; sherry fino/
    amontillado/oloroso/PX; madeira; prošek) — klasika uz cigaru,
  - puna crna (Dingač, Plavac Mali, Babić, Amarone, Barolo, Brunello, Rioja
    Gran Reserva, Primitivo/Zinfandel, Cabernet, Malbec, Syrah),
  - srednja crna (Chianti Classico, Pinot Noir, Merlot, Teran, Frankovka),
  - bijela (Graševina, Pošip, Malvazija, Chardonnay barrique, Riesling),
  - pjenušava (Champagne brut, Prosecco) i desertna (Tokaji, Sauternes,
    Muškat momjanski).
- [ ] Sva polja kao `Drink`: body/sweetness 1–5, `flavorTags` iz postojećeg
      rječnika, HR cijene (Vivat, Miva, Vrutak, Vinoteka, Konzum; verificirane
      točke: Graham's 10 tawny ~36 €, 20 Y.O. ~64 €, Sandeman 20 ~56 €;
      ostalo `priceApprox`), `qualityScore` (agregat javnih ocjena),
      `additiveStatus` (`clean` / `fortified` / `sweetened`) s neutralnim
      detaljem, `serving.best` (temperatura/čaša), notes hr+en.
- [ ] `STYLE_LABELS` za nove stilove vina; `cat.wine` u i18n.
- [ ] `data/index.ts`: import + `DRINKS.wine` + `ALL_DRINKS`.

### Task 4: Vino — engine i UI

**Files:** `app/src/engine/rules.ts`, `app/src/pages/PairingPage.tsx`,
`app/src/pages/CatalogPage.tsx`, `app/src/pages/CollectionPage.tsx`

- [ ] `rules.ts` `WRAPPER_AFFINITY`: connecticut += pjenušci/svježa bijela;
      maduro += porto ruby/PX/oloroso/amarone/primitivo; habano += puna crna,
      tawny, amontillado. Body princip radi bez izmjena — vino ocjenjujemo
      istim pravilima punoće.
- [ ] `PairingPage.tsx`: `SUGGEST_CATEGORIES` += `wine` (cigara → najbolji
      prijedlog i iz vina).
- [ ] `CatalogPage.tsx`: `TABS` += `wine`.
- [ ] `CollectionPage.tsx`: tekst kategorija dopuniti.

### Task 5: Testovi, README, deploy

- [ ] `npm test` — integrity testovi pokrivaju i vino (ALL_DRINKS).
- [ ] Dodati data test: nijedan zapis nema pežorativne izraze
      ("ne za cigaru", "jeftini", "precijenjen"…) u `notes`/`region`;
      svi zapisi `pairable: true` osim eksplicitne iznimke (nema ih).
- [ ] README: novi broj indeksa (+ vino), opis uređivačke politike
      neutralnosti (gornja načela, skraćeno).
- [ ] Build + commit + push na `claude/beverage-neutral-ratings-yrmnvi`.
