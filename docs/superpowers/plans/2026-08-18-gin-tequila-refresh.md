# Gin + Tequila Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Obnoviti HR katalog i pairing note sloj za tekilu (prvo) i gin, koristeći postojeći scrape→Excel→JSON pipeline + W2 PDP obogativanje.

**Architecture:** Listing scrape (`scrape-*-catalog.py`) puni Excel MASTER; `excel-to-*-json.py` piše `app/src/data/*.json`; PDP scrape + merge skripte popunjavaju tagove i note; vitest gateovi štite minimalnu kvalitetu hintova.

**Tech Stack:** Python 3 (openpyxl, bs4, pagefetch optional), Vite/Vitest, postojeći `*_shared.py` heuristike.

## Global Constraints

- Nikad brisati drink `id` bez aliasa — koristi `meta: true` za duplikate/poklon setove.
- HR copy: `.cursor/rules/hr-copy-canon.mdc`.
- Ne fabricirati tasting note u scrape/merge skriptama.
- `curatedOpinion.ts` ne čita `drink.cigarHint` — hint je za UI karticu.
- CI: `cd app && npx tsc -b --noEmit && npm test`.
- Excel datoteke lokalne (gitignored); commit samo JSON + skripte + testovi.

**Spec:** `docs/superpowers/specs/2026-08-18-gin-tequila-refresh-design.md`

---

## Phase 1 — Tequila

### Task 1: Baseline snapshot + listing scrape

**Files:**
- Read: `app/scripts/scrape-tequila-catalog.py`, `app/scripts/build-tequila-excel.py`
- Output: `app/scripts/output/tequila_catalog_raw.json`, `app/scripts/output/baseline_refresh_20260818/tequilas.json`

**Interfaces:**
- Produces: `tequila_catalog_raw.json` — list of `{name, price_eur, shop, url, source}`

- [ ] **Step 1: Snapshot trenutnog kataloga**

```powershell
cd app/scripts
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
New-Item -ItemType Directory -Force -Path "output/baseline_refresh_$ts" | Out-Null
Copy-Item ../src/data/tequilas.json "output/baseline_refresh_$ts/tequilas.json"
```

- [ ] **Step 2: Listing scrape**

```powershell
cd app
python scripts/scrape-tequila-catalog.py
```

Expected: `scripts/output/tequila_catalog_raw.json` — više stavki nego srpanj 2026 (allez tequila-mezcal + ecuga).

- [ ] **Step 3: Regeneriraj Excel**

```powershell
python scripts/build-tequila-excel.py
```

Expected: `Tequila_Kolekcija_Checklist.xlsx` u korijenu repoa (lokalno).

- [ ] **Step 4: Brza provjera broja**

```powershell
python -c "import json; d=json.load(open('scripts/output/tequila_catalog_raw.json',encoding='utf-8')); print(len(d))"
```

Target: ≥ 40 raw SKU (prije filtriranja mixto/poklon).

---

### Task 2: Excel curation — MASTER + Serviranje + Cigare

**Files:**
- Modify (local Excel): `Tequila_Kolekcija_Checklist.xlsx`
- Reference: `app/scripts/tequila_shared.py` (`cigar_hint_for_style`, `detect_style_region`)
- Lookup: `docs/tequila-cigar-pairing-notes.md`

**Interfaces:**
- Consumes: `tequila_catalog_raw.json` via Excel sheets
- Produces: MASTER rows with scores; Serviranje sheet with `cigarHintHr` column

- [ ] **Step 1: MASTER Ocjene — uključi sve 100% agave sipping**

Pravila:
- Uključi: Don Julio, Patrón, Fortaleza, Casamigos, Herradura, Espolòn, Clase Azul (pairable premium), 1–2 mezcal (dim profil).
- Isključi: mixto, cocktail RTD, sol+limeta setovi, mini poklon bez solo boce.
- `qualityScore` ≥ 6.5 za pairable; < 6.5 → ne u MASTER ili `meta`.

- [ ] **Step 2: Katalog allez+ecuga — provjeri URL**

Svaki red: `priceUrl` mora biti product page, ne kategorija. `shop` mora odgovarati hostu URL-a.

- [ ] **Step 3: Serviranje + Cigare — cigarHint za top 12**

Referentni id-evi (proširi po potrebi):
- `tq-don-julio-blanco`, `tq-don-julio-reposado`, `tq-don-julio-anejo`, `tq-don-julio-1942`
- `tq-patron-silver`, `tq-patron-reposado`, `tq-patron-anejo`
- `tq-casamigos-reposado`, `tq-casamigos-anejo`, `tq-casamigos-mezcal`
- `tq-espolon-blanco`, `tq-clase-azul-reposado`

Svaki hint HR ≥ 80 znakova; finite glagoli (*traži*, *ide*, *nosi* — ne infinitivni lanac).

Primjer stilskog mosta (blanco):
> Svježa agava i citrus drže Connecticut ili kraću Habano — papar na pokrovu i papar u čaši se ne tuku nego pojačavaju.

- [ ] **Step 4: Ostale boce — stilski hint + 1 specifična rečenica**

Koristi `cigar_hint_for_style(style)` kao jezgro, dodaj jednu rečenicu o profilu (npr. „vanilija reposada nosi maduro kakao").

---

### Task 3: Export JSON + cleanup

**Files:**
- Modify: `app/src/data/tequilas.json`
- Run: `app/scripts/excel-to-tequila-json.py`

**Interfaces:**
- Produces: `tequilas.json` entries with `cigarHint`, `notes`, `serving`, `priceUrl`, `priceEUR`

- [ ] **Step 1: Export**

```powershell
cd app
python scripts/excel-to-tequila-json.py
```

- [ ] **Step 2: Post-export cleanup u JSON**

Ručno ili mala skripta:
- Duplikati iste boce (META referent + SKU varijanta) → `meta: true` na varijanti.
- Poklon setovi → `meta: true`, `pairable: false`.
- Uskladi `shopHR` s hostom `priceUrl`.
- Dodaj EN `notes.en` / `cigarHint.en` gdje HR postoji a EN prazan.

- [ ] **Step 3: Diff provjera**

```powershell
python -c "
import json
from pathlib import Path
old=json.loads(Path('scripts/output/baseline_refresh_20260818/tequilas.json').read_text(encoding='utf-8'))
new=json.loads(Path('src/data/tequilas.json').read_text(encoding='utf-8'))
print('old',len(old),'new',len(new))
print('removed ids', {d['id'] for d in old}-{d['id'] for d in new})
print('added ids', {d['id'] for d in new}-{d['id'] for d in old})
"
```

Expected: nema `removed ids` bez namjere (ako ima — dodaj alias ili vrati red).

---

### Task 4: W2 PDP enrichment (tequila)

**Files:**
- Run: `app/scripts/scrape-drink-product-pages.py`, `merge-drink-profile-enrichment.py`, `merge-drink-profiles.py`
- Optional: `sideprojects/pagefetch/examples/dump_url.py` for blocked URLs

- [ ] **Step 1: PDP scrape**

```powershell
cd app
python scripts/scrape-drink-product-pages.py --resume
# ako treba ograničiti: --limit 40
```

- [ ] **Step 2: Fallback pagefetch za prazne PDP**

Za svaki id u `drink_pdp_raw.json` gdje `text` < 200 znakova:

```powershell
cd sideprojects/pagefetch
python -m pagefetch "https://allez.hr/shop/..." --prefer auto -o ../../app/scripts/output/pdp_pagefetch/<id>.md
```

Ručno prebaci relevantni opis u pipeline ili proširi parser u `scrape-drink-product-pages.py`.

- [ ] **Step 3: Merge enrichment**

```powershell
cd app
python scripts/merge-drink-profile-enrichment.py --dry-run
python scripts/merge-drink-profile-enrichment.py
python scripts/merge-drink-profiles.py --category tequila --dry-run
python scripts/merge-drink-profiles.py --category tequila
```

- [ ] **Step 4: Provjera profileEstimated**

```powershell
python -c "
import json
d=json.load(open('src/data/tequilas.json',encoding='utf-8'))
pair=[x for x in d if x.get('pairable')]
est=sum(1 for x in pair if x.get('profileEstimated'))
hint=sum(1 for x in pair if (x.get('cigarHint') or {}).get('hr'))
print('pairable',len(pair),'estimated',est,'hintHR',hint)
"
```

Target: `estimated` ≤ 20% pairable; `hintHR` = 100% pairable.

---

### Task 5: Tequila catalog tests

**Files:**
- Create: `app/src/data/tequila.catalog.test.ts`
- Modify: `app/src/data/curatedNotes.test.ts` (dodaj TEQUILA_CURATED_IDS)

**Interfaces:**
- Produces: vitest gate za minimalnu duljinu hint/note

- [ ] **Step 1: Napiši test**

```typescript
// app/src/data/tequila.catalog.test.ts
import { describe, expect, it } from "vitest";
import type { Drink } from "../types";
import tequilasJson from "./tequilas.json";

const tequilas = tequilasJson as Drink[];

const TEQUILA_CURATED_IDS = [
  "tq-don-julio-blanco",
  "tq-don-julio-reposado",
  "tq-don-julio-anejo",
  "tq-don-julio-1942",
  "tq-patron-silver",
  "tq-patron-reposado",
  "tq-patron-anejo",
  "tq-casamigos-reposado",
  "tq-casamigos-anejo",
  "tq-casamigos-mezcal",
  "tq-espolon-blanco",
  "tq-clase-azul-reposado",
] as const;

describe("tequila catalog", () => {
  it("pairable boce imaju HR cigarHint i bilješku", () => {
    for (const t of tequilas.filter((d) => d.pairable && !d.meta)) {
      expect(t.cigarHint?.hr?.length ?? 0, t.id).toBeGreaterThanOrEqual(40);
      expect(t.notes?.hr?.length ?? 0, t.id).toBeGreaterThanOrEqual(40);
    }
  });

  it("referentni set ima punu HR+EN kopiju", () => {
    for (const id of TEQUILA_CURATED_IDS) {
      const t = tequilas.find((d) => d.id === id);
      expect(t, id).toBeDefined();
      expect(t!.notes.hr.length, id).toBeGreaterThanOrEqual(80);
      expect(t!.notes.en.length, id).toBeGreaterThanOrEqual(80);
      expect(t!.cigarHint?.hr?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(t!.cigarHint?.en?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(t!.profileEstimated, id).not.toBe(true);
    }
  });

  it("shopHR odgovara priceUrl hostu", () => {
    for (const t of tequilas) {
      const url = t.priceUrl;
      if (!url) continue;
      const host = new URL(url).hostname.replace(/^www\./, "");
      const shop = (t.shopHR ?? "").toLowerCase();
      if (shop.includes("allez")) expect(host).toContain("allez.hr");
      if (shop.includes("ecuga")) expect(host).toContain("ecuga.com");
    }
  });
});
```

- [ ] **Step 2: Pokreni testove**

```powershell
cd app
npm test -- tequila.catalog.test.ts
npx tsc -b --noEmit
```

Expected: PASS

- [ ] **Step 3: Commit (kad korisnik traži)**

```powershell
git add app/src/data/tequilas.json app/src/data/tequila.catalog.test.ts app/src/data/curatedNotes.test.ts
git commit --author="Agent AI <agent.ai@assistant.local>" -m "feat(drinks): refresh tequila catalog and pairing hints"
```

---

## Phase 2 — Gin

### Task 6: Gin listing + Excel refresh

**Files:**
- Run: `app/scripts/scrape-gin-catalog.py`, `app/scripts/build-gin-excel.py`
- Output: `app/scripts/output/gin_catalog_raw.json`

- [ ] **Step 1: Baseline snapshot** (isto kao Task 1, `gins.json`)
- [ ] **Step 2: `python scripts/scrape-gin-catalog.py`**
- [ ] **Step 3: `python scripts/build-gin-excel.py`**
- [ ] **Step 4: MASTER — proširi na pun allez listing; META za duplikate**

---

### Task 7: Gin hint de-templating

**Files:**
- Modify: `app/scripts/gin_shared.py` (`cigar_hint_for_style` — duže rečenice)
- Modify (Excel): `Gin_Kolekcija_Checklist.xlsx` Serviranje + Cigare
- Modify: `app/src/data/gins.json` via `excel-to-gin-json.py`

**Referentni gin id-evi (15):**
- `gin-monkey-47-schwarzwald-dry-gin-47-vol-0-5l`
- `gin-hendrick-s-gin-41-4-vol-0-7l`
- `gin-tanqueray-no-ten-47-3-vol-0-7l`
- `gin-the-botanist-islay-dry-gin-46-vol-0-7l`
- `gin-gin-mare-mediterranean-gin-42-7-vol-0-7l-u-poklo` (META varijanta — koristi referentnu non-gift SKU)
- `gin-plymouth-gin`
- `gin-sipsmith`
- `gin-nikka-coffey-gin-47-vol-0-7l`
- `gin-four-pillars-rare-dry-gin-41-8-vol-0-7l`
- `gin-old-pilot-s-dalmatian-dry-gin-45-vol-0-7l`
- `gin-dugave-gin`
- `gin-beefeater-24`
- `gin-aviation-gin`
- `gin-roku-gin-the-japanese-craft-gin-43-vol-0-7l-u-po`
- `gin-no-3-london-dry-gin-46-vol-0-7l-u-poklon-kutiji-` (META — referentna boca bez poklon kutije)

- [ ] **Step 1: Proširi `cigar_hint_for_style` na 2 rečenice po stilu**
- [ ] **Step 2: Excel hints za referentne boce (HR+EN, ≥ 80 znakova)**
- [ ] **Step 3: `python scripts/excel-to-gin-json.py`**
- [ ] **Step 4: Poklon/META cleanup — `pairable: false` na setovima**

---

### Task 8: Gin W2 + tests

**Files:**
- Create: `app/src/data/gin.catalog.test.ts`
- Modify: `app/src/data/curatedNotes.test.ts` (GIN_CURATED_IDS)

- [ ] **Step 1: PDP + merge** (isti redoslijed kao Task 4, `--category gin`)
- [ ] **Step 2: EN coverage** — svi pairable imaju `notes.en` i `cigarHint.en` ≥ 40
- [ ] **Step 3: `gin.catalog.test.ts`** — analogno tequila testu + assert unique hints ≥ 40
- [ ] **Step 4: `npm test && tsc`**

---

## Phase 3 — Club touch-up (optional)

### Task 9: Minimal sync check

**Files:**
- Read only: `app/src/data/club101.json`, `app/src/data/club.json`

- [ ] **Step 1:** Ako katalog ima ≥ 3 mezcal pairable — provjeri `d-tequila` već spominje mezcal (da — nema promjene).
- [ ] **Step 2:** Ako novi lokalni gin (Dugave, Old Pilot's) nije u club facts — dodaj **1** fact, ne rescrape.

---

## Verification checklist (kraj)

- [ ] `tequilas.json`: ≥ 35 pairable, 0 hintHR missing on pairable
- [ ] `gins.json`: ≥ 40 unique cigarHint HR, EN ≥ 90% pairable
- [ ] `npm test` green
- [ ] `npx tsc -b --noEmit` green
- [ ] Nema obrisanih drink id bez aliasa
- [ ] Club/bonton: netaknut ili ≤ 2 linije dopune
