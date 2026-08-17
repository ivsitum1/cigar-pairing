# Poklon u pet pitanja — Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking. Implement task-by-task; each task ends green (`tsc` + `npm test`).

**Goal:** Ship a guided gift finder (`#/shopping/gift`) that turns five plain-language answers into 2–3 concrete, priced, buyable gift suggestions — for someone who knows nothing about cigars.

**Architecture:** Pure client-side wizard over the existing catalog and pairing engine. No new scoring model: the five answers become *inputs* to `scorePairing` / `occasionAffinity` and *filters* over `CIGARS` / `DRINKS`. Answers live in component state only (not `localStorage`) — a gift is a one-off, not a saved preference.

**Tech Stack:** Vite + React + TypeScript, Vitest, existing `useI18n` / `LocalizedText`, `useMarket`, `Chip`/`SectionTitle` primitives, `LessonBody` for prose.

---

## Naming

**Feature name: „Poklon u pet pitanja" / "A gift in five questions".**
Nav/chip label: **„Poklon"** — single noun, matching `Sparivanje · Katalozi · Kolekcija · Kupnja · Klub`.

Rejected alternatives, for the record:
- **„Pet pitanja"** — names the mechanism, sits nicely next to „Klub 101" and „Bonton", but hides *what* it does at the exact moment a new user is scanning for help.
- **„Darovnik"** — coinage; reads legalistic in Croatian (too close to *darovnica*, a deed of gift).
- **„Vodič za poklon"** — accurate but limp, and „vodič" is already spoken for by `hrGuide`.

---

## Global constraints

- **Full bilingualism (hr/en) from day one** on every question, option, and result string.
- **Never invent a price.** Only recommend items whose price is actually recorded (see *Data reality* below).
- **HR: online tobacco sales are illegal.** Any cigar result in the HR market shows the indicative price plus `shop.legalNote` and an in-store call to action — never a buy button.
- **No new pairing weights.** If a result needs a reason, it comes from `pairingBlurb` / `curatedPairingOpinion`, not from prose invented here.
- **"Ne znam" is a first-class answer on every question.** The flow must produce a good gift for someone who can answer only Q2 (budget). This is the single most important design rule — a gift buyer is by definition uninformed.
- No new route page hierarchy: reuse `shopping` page with a sub-view, mirroring `ClubView`.

---

## Data reality (measured 2026-08-16, do not re-derive by guessing)

| Fact | Number | Consequence for the design |
|------|--------|----------------------------|
| Cigars with a price on any vitola | **344 / 3313 (10%)** | Budget filtering over the *full* cigar catalog is impossible. The gift pool is these 344. |
| Priced cigar vitolas by band | 108 under 10 €, 393 at 10–20 €, 110 at 20–40 €, 96 over 40 € | All four budget bands are servable for cigars. |
| Priced cigars by strength (1–5) | 9 / 77 / 156 / 83 / 19 | Strength question is servable; band 1 is thin, so „blago" must accept strength ≤ 2. |
| Priced cigars available in HR | 339 of 344 | HR market is the strong case; EU 206, USA 165. |
| Whiskies with a price | **224 / 274 (82%)** | Drinks are the reliable half of the flow. |
| Whisky price bands | 17 under 25 €, 131 at 25–60 €, 55 at 60–120 €, 21 over 120 € | Band boundaries below are chosen to match this distribution, not round numbers. |

**The asymmetry is the design problem.** Drinks are priced, cigars mostly are not. Do not paper over it: the gift pool for cigars is explicitly the priced subset, and the UI says so once, quietly („prikazujemo samo ono čemu znamo cijenu").

---

## The five questions

Each question maps to a concrete engine input. A question that cannot be mapped does not belong in the flow.

### Q1 — „Za koga je?" / "Who is it for?"
| Option | Maps to |
|--------|---------|
| Puši cigare redovito | Full cigar pool; allow strength 4–5; allow collector formats |
| Tek je počeo / probao par puta | Cap cigar strength ≤ 3; prefer robusto/corona over gordo/lancero (`cigarShapes`) |
| Ne puši — poklon je piće | Drop cigars entirely; drinks + glassware only |
| Ne znam | Treat as beginner (safest default), and say so in the result |

### Q2 — „Koliko želiš potrošiti?" / "Budget"
Bands `do 25 € · 25–60 € · 60–120 € · 120 € +`, chosen to match the measured whisky distribution.
Maps to: `cigarLinePrice(c, market).price` and `drink.priceEUR` midpoint. **Hard filter, never soft** — a gift over budget is a failed recommendation. If a band yields nothing for the chosen category, fall back one band *down* and label it („ispod tvog raspona jer u njemu nema ničega vrijednog").

### Q3 — „Što voli piti?" / "What do they drink?"
Options: Viski · Rum · Konjak/brandy · Vino · Ne znam.
Maps to `DrinkCategory`. „Ne znam" → rank across all categories by `qualityScore` within budget, which is exactly what `segmentPicks` already does.

### Q4 — „Jače ili blaže?" / "Bolder or gentler?"
Options: Blago i glatko · Srednje · Jako i puno · Ne znam.
Maps to cigar `strength` (≤2 / 3 / ≥4) and drink `body`. „Ne znam" → 3 / medium, the catalog's densest band.

### Q5 — „Kakav poklon?" / "What shape of gift?"
| Option | Assembles |
|--------|-----------|
| Jedna dobra boca | Top `qualityScore` drink in budget ∩ category |
| Cigara i piće za jednu večer | **The pairing case** — pick cigar in budget, then `pairDrinksForCigar`, take the top scorer that also fits the remaining budget |
| Set za početnika | Cutter + lighter + 2–3 mild cigars; accessory links already exist in `club101.json` `tracks.accessories[].shopLinks` |
| Nešto za policu | Highest `qualityScore` in the top budget band; `lineup` items surface here |

---

## Result design

Show **two or three** options, never one (a single suggestion reads as an oracle) and never five (that is the catalog again). Each result card carries:

1. Name + photo-less brand mark (`BrandMark`) — consistent with `DrinkRow` / `CigarRow`.
2. **Price, always, with its market** — `formatPrice` + `MarketFilter` semantics.
3. **One sentence of why**, sourced from the engine: `pairingBlurb` for pairings, `curatedPairingOpinion` when a curated one exists, otherwise the drink's own `notes`.
4. Where to buy: existing shop-link resolution. HR + cigar → `shop.legalNote`, in-store only.
5. „Zamijeni" — reroll that one card without redoing the questionnaire.

Closing row: „Počni ispočetka" and „Otvori u katalogu" (deep link via existing `CatalogFocus`).

---

## File map

| File | Responsibility |
|------|----------------|
| `app/src/lib/giftFinder.ts` | Pure: answers → candidate set → ranked picks. All logic, no JSX |
| `app/src/lib/giftFinder.test.ts` | Every answer combination yields ≥2 priced results; budget is never exceeded |
| `app/src/data/giftQuestions.json` | The five questions + options, bilingual |
| `app/src/data/giftQuestions.test.ts` | Schema, bilingual completeness, option ids match the `GiftAnswers` union |
| `app/src/pages/GiftPage.tsx` | Wizard UI (one question per step, back/forward) + results |
| `app/src/pages/ShoppingPage.tsx` | Entry card |
| `app/src/pages/ClubPage.tsx` | Secondary entry teaser |
| `app/src/store/route.ts` (+ `.test.ts`) | `ShoppingView = "shopping" \| "gift"`, hash round-trip |
| `app/src/i18n/index.tsx` | `gift.*` strings |
| `README.md` | Feature note |

---

### Task 1 — Route + question data + schema test
- [ ] `ShoppingView` in `route.ts`, `#/shopping/gift` round-trips in `route.test.ts`
- [ ] `giftQuestions.json` with all five questions, bilingual, every option carrying a stable `id`
- [ ] `giftQuestions.test.ts`: both languages non-empty; every question has an „ne znam" option

### Task 2 — `giftFinder.ts` (the whole brain, headless)
- [ ] `GiftAnswers` type; `findGifts(answers, market): GiftPick[]`
- [ ] Budget is a hard filter; documented fallback-one-band-down with a `fellBack` flag on the result
- [ ] Cigar pool restricted to priced entries, with a comment pointing at the 10% measurement
- [ ] Pairing option routed through `pairDrinksForCigar` — **no new scoring**
- [ ] Tests: exhaustive sweep over all answer combinations (4×4×5×4×4 = 1280) asserting ≥2 results and no over-budget pick

### Task 3 — `GiftPage.tsx` wizard + results
- [ ] One question per step, progress dots, back button, answers in component state
- [ ] Result cards per *Result design*; „Zamijeni" rerolls one card
- [ ] HR + cigar → legal note, no buy button

### Task 4 — Entry points, i18n, README
- [ ] Shopping entry card + Club teaser
- [ ] All `gift.*` strings in both languages; `croatian.test.ts` stays green
- [ ] README note next to the whisky filter entry

---

## Risks / open decisions

1. **The 10% cigar price coverage is the whole risk.** If the gift pool of 344 feels thin in use, the fix is upstream (scrape more prices), not a softer budget filter. Do not "solve" it by recommending unpriced cigars.
2. **Q5 „Set za početnika" depends on accessory shop links** that currently live inside `club101.json` lesson cards. If that coupling feels wrong, lift them to their own `accessories.json` first — but that is a separate change, not part of this one.
3. **Two or three results?** Recommend three when the budget band is wide (60–120 €, 120 €+), two when it is narrow — otherwise the low band repeats itself.
4. **Not doing:** saving gift results, sharing them, or a "gift history". A gift is a one-off; `localStorage` stays for collection and diary.

---

## Revizija 2026-08-17 — prag slaganja, susjedna kategorija, prazan upitnik

Tri pravila dodana nakon prvog kruga korištenja. Sva tri žive u `giftFinder.ts`;
UI ih samo prikazuje.

### 1. Kombinacija mora prijeći 80 %

`MIN_PAIRING_SCORE = 80` na prikaznoj skali sparivanja (isti broj koji korisnik
vidi kao postotak). Prije toga je kartica „Cigara i piće" uzimala prvi par koji
stane u budžet — izmjereno na cijelom katalogu, četvrtina prijedloga bila je
ispod 50 % (najgori 23 %). Kombinacija koja ne ide gori je poklon od dvije
zasebne stvari koje idu.

Posljedica: jačinu para nosi **cigara** (odgovor „kakav je navečer"), a piće
bira engine. Dvostruki filter po jačini izbacivao je upravo one parove koje
pravilo `body-match` najbolje ocjenjuje.

### 2. Nula pogodaka → susjedna kategorija, pa tek onda budžet i oblik

`CATEGORY_NEIGHBOURS` (whisky → brandy → rum → vino; bačvom zrele žestice su
međusobno najbliže, vino sjedi uz brandy). Ljestvica popuštanja u
`buildAttempts`, od najmanjeg ustupka prema najvećem:

1. sve točno kako je rečeno,
2. susjedna kategorija pića — **isti budžet, ista jačina**,
3. isto to s niže police (nikad skuplje od odgovora),
4. drugi oblik poklona (kombinacija → cigara i boca zasebno).

Zamjena kategorije ide prije spuštanja cijene: budžet je korisnikovo tvrdo
ograničenje, kategorija je pretpostavka o tuđem ukusu. Svaki ustupak nosi
oznaku na kartici (`swappedFromCategory`, `fellBackBudget`, `droppedPairing`).

### 3. Svih pet „ne znam"

Presjek praznih filtera davao je nasumičan rezultat (izmjereno: kombinacija na
39 % i boca gina). Taj slučaj sada hvata `isBlankGiftAnswers` i zamjenjuje ga
jednim namjerno odabranim profilom (`SAFE_DEFAULT_ANSWERS`):

- pristupačan format (corona/robusto) i snaga do 3,
- srednja jačina — sredina ljestvice, ondje je najviše parova iznad praga,
- 20–40 €,
- samo klasične kategorije u čaši (`CLASSIC_GIFT_CATEGORIES`) — bez gina, kave
  i digestiva kad ne znamo što osoba pije,
- **tri različite stvari** (kombinacija, boca, cigara), s bocom ispred cigare:
  ne znamo ni puši li osoba, a boca radi u oba slučaja.

Kartice nose `safeDefault` pa UI objašnjava zašto je izbor takav i poziva na
odgovor na bilo koje pitanje.

### Mjereno nakon izmjene (HR, svih 1600 kombinacija odgovora)

| | prije | poslije |
|---|---|---|
| kombinacija ispod 80 % | 460 od 552 | 0 od 2132 |
| kombinacija bez ijednog prijedloga | 6 | 0 |
| prosječno slaganje predloženog para | ≈54 % (procjena iz histograma) | 84,2 % |

Proturječni odgovori (npr. „tek je na početku" + „voli jače stvari") više ne
daju prazan presjek: strop primatelja pobjeđuje, ali se traži najjače unutar
njega (`cigarStrengthRange`).
