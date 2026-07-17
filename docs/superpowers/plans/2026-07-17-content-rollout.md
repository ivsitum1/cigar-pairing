# Content Rollout + Shop-Link Trust — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ubaci rangirane uredničke inicijative iz `docs/superpowers/specs/2026-07-17-content-brainstorm.md` u Club/katalog kao čitljiv sadržaj, uz pouzdane shop linkove na Shopping/Gaps (bez lažnih „Kupi” URL-ova).

**Architecture:** Sadržaj ulazi kao JSON lekcije/eseji/bilješke (isti obrasci kao `club101.json` / `bonton.json` / `notes`+`cigarHint`), ne kao novi backend. Shop trust je runtime sloj (`drinkBuyLink`) + kasnije stroži pipeline match; bonton rukopis se ne rewrita — samo kutovi sakupljanja.

**Tech Stack:** Vite + React + TS, postojeći Club/`LessonBody`, vitest, lokalni JSON indeksi; Python pipeline samo za Task 1b (match prag).

## Global Constraints

- Uređivačka politika: deklaracija umjesto osude; ocjena unutar stila; sve pairable; različita pravila po kategoriji.
- Dvojezičnost: novi UI stringovi u `app/src/i18n/index.tsx` (hr+en); proza barem HR, EN paralel kad je spreman.
- Bez novih npm ovisnosti.
- Bonton: **ne** prepisivati `docs/bonton/mala-knjiga-pusackog-bontona.md` ni `bonton.json` u ovom planu — samo `docs/bonton/grill-inbox.md` za sirovinu.
- Testovi: `cd app && npm test`; build: `cd app && npm run build`.
- Commit poruke na engleskom.

## File map (nove / dirane jedinice)

| File | Responsibility |
|------|----------------|
| `app/src/lib/drinkBuyLink.ts` | Pouzdan buy vs search za pića |
| `app/src/data/lexicon.json` | Leksikon pairing jezika (inicijativa A) |
| `app/src/pages/LexiconPage.tsx` | Club view leksikona |
| `app/src/data/hrGuide.json` | HR vodič kupnje (B) |
| `app/src/pages/HrGuidePage.tsx` | Club view vodiča |
| `app/src/data/eveningArchetypes.json` | Večernji arhetipovi (D) |
| `app/src/pages/EveningArchetypesPage.tsx` | Club view arhetipova |
| `app/src/data/*.json` (katalog) | Valovi bilješki + `cigarHint` (C) |
| `app/src/data/club.json` | Nove činjenice/kviz (E) |
| `docs/bonton/grill-inbox.md` | Inbox za grill notebook (F) |
| `app/src/data/club101.json` | Gin/kava + predložak bilješke (G, H) |
| `app/scripts/whisky_shared.py` / `excel-to-json.py` | Stroži catalog match (1b) |

---

### Task 0: Shop-link trust (Gaps / DetailSheet) — DONE u kodu, potvrdi

**Files:**
- Create: `app/src/lib/drinkBuyLink.ts`
- Create: `app/src/lib/drinkBuyLink.test.ts`
- Modify: `app/src/components/DetailSheet.tsx` (koristi lib umjesto lokalne funkcije)

**Root cause (verified):** `priceUrl` često je HTTP 200 ali **krivi SKU** ili **kategorija** (`/katalog/`, `/vrsta/`) zbog fuzzy matcha (`find_catalog_url` / `find_best_catalog_match`, prag ≥2 tokena). Gaps otvara DetailSheet → „Gdje kupiti” je izgledalo pokvareno.

**Interfaces:**
- Produces: `drinkBuyLink(drink) → { href, label: "buy"|"search" }`, `urlMatchesDrinkName`, `isDrinkProductUrl`

- [x] **Step 1: Runtime safeguard** — odbij kategorije; zahtijevaj slug↔ime (brojevi godina, mid/long tokeni); zadrži shopHR↔domain pravilo.
- [x] **Step 2: Testovi** — Tributo≠Añejo 15, batch 4≠2, `/katalog/rum` → search; Hampden HLCF → buy.
- [ ] **Step 3: Ručna provjera**

```bash
cd app && npm test -- src/lib/drinkBuyLink.test.ts
# Očekivano: 9 passed
# U UI: Shopping → Praznine → otvori prijedlog → "Gdje kupiti" ili "Traži online" (nikad krivi SKU kao "Kupi")
```

- [ ] **Step 4: Commit** (ako još nije na grani)

```bash
git add app/src/lib/drinkBuyLink.ts app/src/lib/drinkBuyLink.test.ts app/src/components/DetailSheet.tsx
git commit -m "fix: reject mismatched drink buy URLs (gaps/detail)"
```

---

### Task 1b: Pipeline — stroži catalog match (sprečava reintrodukciju)

**Files:**
- Modify: `app/scripts/excel-to-json.py` (`find_catalog_url`)
- Modify: `app/scripts/whisky_shared.py` (`find_best_catalog_match`)
- Modify: `app/scripts/brandy_shared.py` (isto)
- Test: `app/scripts/test_brandy_shared.py` (proširi) ili novi `app/scripts/test_catalog_match.py`

**Interfaces:**
- Consumes: catalog entries `{name, url, tokens}`
- Produces: match only if score ≥ 3 **and** numeric age tokens in name ⊆ catalog name/url tokens; never return bare `/katalog/` or `/vrsta/` URLs

- [ ] **Step 1: Failing Python test**

```python
def test_rejects_category_and_wrong_sku():
    catalog = [
        {"name": "Havana Club Añejo 15", "url": "https://allez.hr/shop/svi-proizvodi/havana-club-gran-reserva-anejo-15-anos-40-vol-07l-u-poklon-kutiji", "tokens": match_tokens("Havana Club Anejo 15")},
        {"name": "Rum category", "url": "https://ecuga.com/katalog/rum", "tokens": match_tokens("rum")},
    ]
    assert find_best_catalog_match("Havana Club Tributo", catalog) is None
    assert find_best_catalog_match("Appleton Estate 15", catalog) is None
```

- [ ] **Step 2: Run test — expect FAIL**
- [ ] **Step 3: Implement stricter match + category URL filter**
- [ ] **Step 4: Run test — expect PASS**
- [ ] **Step 5: Commit**

```bash
git commit -m "fix(pipeline): tighten drink catalog URL matching"
```

Napomena: puna regeneracija Excela samo kad su lokalni `.xlsx` dostupni; inače runtime (Task 0) ostaje zaštita.

---

### Task 2: Inicijativa A — Leksikon pairing jezika

**Files:**
- Create: `app/src/data/lexicon.json`
- Create: `app/src/data/lexicon.test.ts`
- Create: `app/src/pages/LexiconPage.tsx` (reuse `LessonBody` + `BackButton` kao `BontonPage`)
- Modify: `app/src/pages/ClubPage.tsx` — teaser kartica
- Modify: `app/src/i18n/index.tsx` — `club.lexicon*` ključevi
- Modify: `app/src/store/route.ts` / Club nested nav (isti obrazac kao bonton/101)

**Data shape:**

```ts
{
  title: LocalizedText,
  intro: LocalizedText,
  entries: { id: string, title: LocalizedText, body: string }[] // body: \n\n + • katalog
}
```

**Entries (min 8, kanon iz brainstorma):** most; tijelo↔tijelo; snaga vs tijelo; trećine; obitelji nota; ritam; riječi za stol; mini vježbe.

- [ ] **Step 1: Failing test** — `lexicon.entries.length >= 8`, svaki `title.hr` i `body` neprazan
- [ ] **Step 2: Run — FAIL**
- [ ] **Step 3: Napiši `lexicon.json` (HR; EN paralel ili kratki EN)**
- [ ] **Step 4: `LexiconPage` + Club teaser + i18n**
- [ ] **Step 5: `npm test` PASS; commit**

```bash
git commit -m "feat(club): add pairing lexicon"
```

---

### Task 3: Inicijativa B — HR vodič kupnje

**Files:**
- Create: `app/src/data/hrGuide.json`
- Create: `app/src/data/hrGuide.test.ts`
- Create: `app/src/pages/HrGuidePage.tsx`
- Modify: `ClubPage.tsx`, `i18n/index.tsx`

**Sections (7):** zakon/praksa duhan; karta piće; karta duhan referentno; kako čitati cijenu/link u appu; prvi kit; sezona/zaliha; poklon.

**Tone:** praktičan; eksplicitno da „Kupi” znači pouzdan product URL, inače „Traži online”.

- [ ] **Step 1–5:** isto kao Task 2 (test → JSON → page → teaser → commit)

```bash
git commit -m "feat(club): add HR buying guide"
```

---

### Task 4: Inicijativa D — Večernji arhetipovi (6–8 eseja)

**Files:**
- Create: `app/src/data/eveningArchetypes.json`
- Create: `app/src/data/eveningArchetypes.test.ts`
- Create: `app/src/pages/EveningArchetypesPage.tsx`
- Modify: `ClubPage.tsx`, `i18n`

**Shape:** `{ id, title, body, optional styleTags[] }` — **stilovi**, ne konkretni SKU (izbjegava pokvarene shop linkove).

Primjeri arhetipova: Connecticut + amontillado; maduro + tawny; jamajka esteri + puniji wrapper; agricole + citrus; peat + jaka cubanka; espresso + kratka vitola.

- [ ] **Step 1–5:** test → JSON (≥6) → page → teaser → commit

```bash
git commit -m "feat(club): add evening pairing archetypes"
```

---

### Task 5: Inicijativa C — Val 1 bilješki + cigarHint (rum)

**Files:**
- Modify: `app/src/data/rums.json` (15–25 MASTER favorita)
- Optional script note in README: ručna kuracija, ne scrape prose
- Test: proširi `integrity.test.ts` ili novi `curatedNotes.test.ts` — odabrani id-jevi imaju `notes.hr.length >= 80` i `cigarHint.hr`

**Predložak bilješke:** 1 rečenica stil; 1 rečenica očekivanje; `cigarHint` most/kontrast; aditiv samo ako već postoji polje.

- [ ] **Step 1: Lista id-jeva** (npr. Hampden HLCF, Foursquare Detente, …) u testu kao konstanta
- [ ] **Step 2: FAIL dok bilješke prazne**
- [ ] **Step 3: Uredi JSON**
- [ ] **Step 4: PASS + commit**

```bash
git commit -m "content(rum): curated notes and cigarHint wave 1"
```

**Kasniji valovi (isti task pattern, zasebni commit):** whisky klasici → fortificirana vina → brandy/vinjak → cigare `profileEstimated` (HR marke).

---

### Task 6: Inicijativa E — Kviz/činjenice (degustacija, HR, gin/kava)

**Files:**
- Modify: `app/src/data/club.json`
- Modify: `app/src/data/club.test.ts` (min. brojevi + nova tema tag ako postoji)

- [ ] **Step 1:** Dodaj ≥8 činjenica + ≥8 kviz pitanja (degustacijski vokabular, HR shop/zakon, gin/kava mostovi)
- [ ] **Step 2:** `npm test` + commit

```bash
git commit -m "content(club): expand facts/quiz for tasting and HR context"
```

---

### Task 7: Inicijativa F — Bonton grill inbox (bez rewritea knjige)

**Files:**
- Create: `docs/bonton/grill-inbox.md`

**Sadržaj inboxa (predlošci, ne gotova poglavlja):**
- situacije stola (pitanja za gosta/domaćina)
- lokalni HR običaji (terasa, klub, restoran)
- citati / atribucije za provjeru
- „ne radi se o ukusu” vignette
- popis literature za kasniji grill (bez copy-paste)

- [ ] **Step 1:** Napiši inbox s ≥15 bullet sirovina
- [ ] **Step 2:** Commit only docs

```bash
git commit -m "docs(bonton): add grill notebook inbox for source collecting"
```

---

### Task 8: Inicijative G + H — Gin/kava 101 kut + predložak bilješke

**Files:**
- Modify: `app/src/data/club101.json` — 2–3 lekcije (gin pairing; kava/espresso most; `t-notebook` proširenje „kako bilježiti”)
- Modify: `app/src/data/club101.test.ts` ako broji lekcije po traci

- [ ] **Step 1:** FAIL ako nove id-jeve nema
- [ ] **Step 2:** Dodaj lekcije u postojećem `\n\n` + `•` formatu
- [ ] **Step 3:** PASS + commit

```bash
git commit -m "feat(club101): gin/coffee pairing corners and tasting-note template"
```

---

### Task 9: README + Club index copy

**Files:**
- Modify: `README.md` — inventar Club sadržaja; napomena o buy vs search; redoslijed content valova
- Modify: `ClubPage.tsx` teaser redoslijed: 101 → Leksikon → HR vodič → Arhetipovi → Bonton

- [ ] **Step 1:** Ažuriraj README sekciju Struktura / Club
- [ ] **Step 2:** `npm test && npm run build`
- [ ] **Step 3:** Commit

```bash
git commit -m "docs: document content rollout and trusted buy links"
```

---

## Redoslijed izvršenja (preporuka)

1. Task 0 potvrda (već u kodu) → 1b kad ima vremena za pipeline  
2. Task 2 (A) → Task 3 (B) → Task 4 (D) — brzi Club sloj  
3. Task 5 val 1 (C rum) paralelno s Task 6–7 (E/F)  
4. Task 8 (G/H) → Task 9  

## Spec coverage (brainstorm A–H)

| Inicijativa | Task |
|-------------|------|
| A Leksikon | 2 |
| B HR vodič | 3 (+ Task 0/1b trust) |
| C Bilješke | 5 (+ valovi) |
| D Arhetipovi | 4 |
| E Kviz/činjenice | 6 |
| F Grill inbox | 7 |
| G Gin/kava | 8 |
| H Predložak bilješke | 8 |

## Self-review

- Nema TBD placeholder koraka; svaki task ima file path i commit.
- Bonton rewrite namjerno isključen.
- Shop-link root cause dokumentiran; runtime prije pipeline regeneracije.
