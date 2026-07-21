# Playbook: Faza B/C — širenje kataloga (deterministički, identično za Claude i Cursor)

**Datum:** 2026-07-21
**Status:** spremno za izvršenje
**Preduvjet:** Faza A odrađena (`app/scripts/enrich-region-links.py`, `regionLinks`
na postojećih 514). Vidi `docs/superpowers/specs/2026-07-21-all-shops-catalog-scrape.md`.

> **Svrha:** ovaj dokument je izvor istine tako da **bilo koji agent (Claude ili
> Cursor) proizvede BAJT-IDENTIČAN `cigars.json`/`brands.json`**. Ako se ijedno
> pravilo ne može ispuniti deterministički — STANI i pitaj, ne improviziraj.

---

## AS-BUILT (Faza B GOTOVA — čitaj prije izvršenja)

Faza B je implementirana i integrirana (grana `claude/cigar-shop-links-filter-69lq6y`).
Skripta **`app/scripts/build-market-cigars.py`** je JEDINI writer (indent=2) i radi
sve u jednom prolazu — profiliranje je INLINE (uvozi `enrich` iz `profile-cigars.py`);
**NE pokreće se** zasebni `profile-cigars.py` ni `dedupe-data.py` za market unose.

Odstupanja od originalnog nacrta (namjerna, radi kvalitete/idempotentnosti):
- **Habanos marke se preskaču** (`HABANOS` set = kubanske marke iz `integrity.test.ts`);
  strane trgovine drže ne-kubanske imenjake → reason `habanos_brand_skip`.
- **Dup-gate = (brend, linija) vs kurirane** (ne trojka): market ne dira kurirane
  linije; poklapanje → reason `existing_line` (dodatne vitole kuriranih = kasnije).
- **Grupiranje po (brend, linija)** → jedna cigara s više vitola (interni dedupe;
  bez `dedupe-data.py`).
- Čišćenje linije: makni brend gdje god se pojavi, dimenzije, vitola-sinonime,
  zagrade/pakiranje/`by`/dangling `Gran`.
- Rezultat Faze B: **271 novih linija** (514 → 785), 0 embargo, 131/131 test, tsc+build ✓.

Komanda (Faza B, cijela, deterministički): `cd app && python scripts/build-market-cigars.py --phase b --check-input-sha && npm test && npx tsc -b`.
Reprodukcija je bajt-identična (idempotentno). Batchanje po brendu nije nužno jer je
gate strog; `--brands "A,B"` postoji za ciljano.

Ostatak dokumenta = originalni nacrt (referenca za Fazu C).

---

## 0. Zlatna pravila determinizma (OBAVEZNO)

1. **Idempotentna regeneracija.** Faza B/C skripta NE dopisuje inkrementalno. Svaki
   run: (a) učita bazni katalog (514 kuriranih + Faza A), (b) **ukloni sve prije
   generirane unose** (oni s `"catalogSource": "market"`), (c) regenerira ih iz nule
   iz zakovanog inputa, (d) merge + sort + zapis. Tko god zadnji pokrene skriptu →
   kanonska datoteka. Redoslijed pokretanja NE utječe na rezultat.
2. **Zakovani input:** `app/scripts/output/cigar_unified_catalog.json`, točno s grane
   `cursor/shop-raw-catalogs-d678` **@ commit `e251e0b`** (sha256 zabilježiti u
   skripti i provjeriti na startu; ako se ne poklapa — STANI). Datoteka je 26 MB i
   **gitignorirana**; dohvat: `git show cursor/shop-raw-catalogs-d678:app/scripts/output/cigar_unified_catalog.json > app/scripts/output/cigar_unified_catalog.json`.
3. **Zakovane konstante:** `USD_TO_EUR = 0.92`. Zaokruživanje: `round(x, 2)`.
   Nikakav live tečaj, nikakav random, nikakav `datetime.now()` u podacima.
4. **JSON zapis (svugdje):** `json.dumps(obj, ensure_ascii=False, indent=2) + "\n"`.
   UTF-8, LF završeci. Bez `sort_keys`.
5. **Sort cijelog `cigars.json`** nakon merge-a — zakovani ključ (Python):
   ```python
   import unicodedata, re
   def sortkey(c):
       def f(s):
           s = unicodedata.normalize("NFKD", s or "")
           s = "".join(ch for ch in s if not unicodedata.combining(ch))
           return s.casefold()
       return (f(c["brand"]), f(c["line"]), f(c["vitola"]), c["id"])
   cigars.sort(key=sortkey)
   ```
6. **Python 3.11+**, stabilan sort, bez paralelizma koji mijenja redoslijed.
7. **Kanonski uređuju se SAMO** `app/src/data/cigars.json` i `app/src/data/brands.json`
   kroz skriptu. Generirane unose NIKAD ne diraj ručno.

---

## 1. Koordinacija Claude ↔ Cursor

- Rade na **istoj grani** `claude/cigar-shop-links-filter-69lq6y` (ima Fazu A + filter).
- **Prije rada:** `git fetch && git pull --rebase`.
- **Jedan batch = jedan commit.** Batch redoslijed je fiksan (§9). Ne raditi dva
  ista batcha; provjeri `git log` prije starta.
- Zbog idempotentnosti (§0.1), ako oba pokrenu skriptu na istom stanju, `cigars.json`
  je identičan → nema konflikata sadržaja, samo eventualno git rebase.
- Nakon svakog batcha: `npm test` MORA biti zelen prije push-a.

---

## 2. Ulazni zapisi (iz unified kataloga)

`unified["cigars"]` = 9 336 zapisa. Relevantni za nas su **shop-only** (`inCatalog == false`):
- **2 513** imaju `brand` (svi mapirani na brend iz `brands.json`) → **Faza B**.
- **5 517** imaju `brand == null` → **Faza C**.

Polje po zapisu koje koristimo:
`name, brand, line, vitola, country, details{wrapper,binder,filler,origin,strength,
ringGauge,lengthIn,lengthCm,diameterCm,boxPressed,size}, offers[], regions/markets, sourceUrls`.

`offers[]` po ponudi: `sourceShopId, region, url, amount, currency, inStock,
packaging{type,count}, attributes{brand,vitola,dimensions}`.

---

## 3. Shema generirane cigare (točna polja)

Generirani `Cigar` MORA imati identična polja kao kurirani + markere:

```jsonc
{
  "id": "<vidi §5>",
  "brand": "<kanonski brend>",
  "line": "<kanonska linija, §4>",
  "vitola": "<kanonska vitola, §4>",
  "format": "<ring> x <lengthMM>mm" ,      // ili "—" ako nema oboje
  "country": "<hr naziv zemlje, §6>",
  "wrapper": "<details.wrapper ili '—'>",
  "strength": <1-5, iz profile-cigars.py>,
  "body": <1-5, iz profile-cigars.py>,
  "flavorTags": [<iz profile-cigars.py>],
  "profileEstimated": true,
  "catalogSource": "market",               // MARKER generiranog unosa
  "smokeTimeMin": <§7>,
  "priceEUR": null,                         // HR cijena; null za EU/USA-only
  "priceApprox": false,
  "availabilityHR": [],                     // prazno ako nije u HR trgovinama
  "notes": { "hr": "<§8>", "en": "<§8>" },
  "markets": [<§6, ukljucuje "WW">],
  "vitolas": [ { "name": "<vitola>", "format": "<ring x mm>", "smokeTimeMin": <§7>, "priceEUR": <HR cijena ili null>, "url": <HR product url ili null> } ],
  "regionLinks": { <§6> },
  "sourceUrls": [<sve product URL-ove iz offers, deduplicirano, sortirano>]
}
```

Redoslijed ključeva u zapisu: točno kao gore (radi stabilnog diffa).

---

## 4. Normalizacija brenda / linije / vitole (VRHUNSKA KVALITETA)

Cilj: čist `line` + `vitola`, ne sirovi „Black Gold Toro Box-Pressed".

### 4a. Brend
- Faza B: `brand` je već kanonski (poklapa se s `brands.json`). Koristi ga.
- Faza C: izvedi iz URL slug-a (Holt's `/all-cigar-brands/<slug>.html`; cigarworld/
  cigarsdaily prvi tokeni product slug-a) → mapiraj kroz **`app/scripts/data/brand_dictionary.json`**
  (novi, dijeljeni; slug → kanonski brend). Ako brend nije u rječniku → **HOLD** (§ quality gate).

### 4b. Linija i vitola — deterministički algoritam
Ulaz: `name` (bez brenda), `details.size`, `details.ringGauge`, dužina.
1. `base = name` bez vodećeg brenda (case-insensitive strip prefiksa brenda).
2. Izvuci **vitolu** = zadnji poklopljeni token iz **`app/scripts/data/vitola_lexicon.json`**
   (dijeljeni, fiksni popis kanonskih vitola + sinonima; vidi §4c). Primjeri:
   „Robusto", „Toro", „Corona", „Churchill", „Lancero", „Torpedo", „Belicoso",
   „Perfecto", „Petit Corona", „Double Corona", „Lonsdale", „Gordo", „Half Corona".
   Sufikse „Box-Pressed"/„Tubos"/„Maduro" tretiraj kao modifikatore (vidi §4d), ne dio vitole.
3. **Linija** = `base` minus prepoznata vitola i minus dimenzijski tokeni
   (`\d+\s*[xX]\s*\d+`, `\d+(\.\d+)?"`, `mm`, `cm`), trim, Title Case očuvavši
   postojeći capitalization brenda. Ako je linija prazna → linija = brend line default
   (npr. za jednolinijske brendove) ili `name` bez vitole.
4. **Mapiranje na POSTOJEĆU liniju** (Faza B): ako brend već ima linije u `cigars.json`,
   poklopi izvedenu liniju na najbližu postojeću preko **`app/scripts/data/line_map.json`**
   (dijeljeni override: `"<brand>::<raw line>" → "<canonical line>"`). Ako nema override i
   fuzzy match < prag → nova linija (dopušteno u Fazi B jer je brend poznat).

### 4c. `vitola_lexicon.json` (dijeljeni, fiksni)
Popis kanonskih vitola sa sinonimima i tipičnim ring/length rasponom (za validaciju).
Skripta ga učita; NE hardkodirati u kodu. Primjer unosa:
```json
{ "Robusto": {"syn": ["robusto"], "ring": [48,54], "lenMM": [114,140]},
  "Toro":    {"syn": ["toro"], "ring": [50,56], "lenMM": [140,165]},
  "Torpedo": {"syn": ["torpedo","belicoso","piramide","pyramid"], "ring": [50,56], "lenMM": [140,165]} }
```
Prvi build: agent generira lexicon iz distinctnih `details.size`/vitola tokena, zatim ga
**commita** — od tada je zajednički i fiksan.

### 4d. Modifikatori
`boxPressed` (iz `details.boxPressed` ili token „Box-Pressed") → ne mijenja vitolu, ide
u `notes`. Wrapper varijante („Maduro"/„Connecticut"/„Habano") ostaju **dio linije** samo
ako postojeća linija tako postoji (npr. „La Aroma de Cuba Connecticut"); inače u `notes`.

---

## 5. ID (deterministički)

```python
def slug(s):
    s = unicodedata.normalize("NFKD", s); s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower(); s = re.sub(r"[^a-z0-9]+", "-", s).strip("-"); return re.sub(r"-{2,}", "-", s)
cid = "cig-" + slug(f"{brand} {line} {vitola}")
```
Kolizija: ako `cid` već postoji (i nije isti dedupeKey), dodaj `-2`, `-3`… redom.
**Nikad** ne mijenjaj ID postojećih 514.

---

## 6. Regije, embargo, regionLinks

- `markets`: skup regija iz `offers[].region` + uvijek `"WW"`. Redoslijed fiksno
  `[m for m in ["HR","EU","USA","WW"] if m in set]`.
- **Embargo (tvrdo):** ako je zemlja kubanska (`country` sadrži `kub`/`cuba`) →
  ukloni `USA` iz `markets` i **ne** stvaraj `regionLinks.USA`.
- `regionLinks[region]` = najbolja ponuda po regiji (isti `best_offer` kao Faza A:
  `inStock` prvo, pa single/single_equiv pakiranje, pa najniža `amount`):
  `{ "shop": SHOP_LABEL[sourceShopId], "url": <url>, "priceEUR": <to_eur>, "priceApprox": <USD?> }`.
  HR regionLink samo ako postoji HR ponuda; HR cijena/URL ide i u `vitolas[0]`/`priceEUR`.
- `SHOP_LABEL` i `to_eur`/`best_offer`: identični kao u `enrich-region-links.py` (uvezi ih, ne kopiraj).

---

## 7. Vrijeme pušenja / format
- `format`: `f"{ring} x {lengthMM}mm"` (lengthMM = round(lengthIn*25.4) ili iz lengthCm/diameterCm);
  ako fali ring ILI dužina → `"—"`.
- `smokeTimeMin`: iz `details.burnTimeMin` ako postoji; inače deterministički iz dužine:
  `round(lengthMM/2.6)` clamp [20, 120]; ako nema dužine → 45.

---

## 8. Profil i bilješke
- **Profil** (`strength`, `body`, `wrapper`, `flavorTags`): pokreni postojeći
  `app/scripts/profile-cigars.py` NAD generiranim unosima (isti heuristik kao za
  postojeće `profileEstimated`). Ne izmišljati ručno.
- **notes** (kratko, dvojezično, deterministički šablon):
  `hr: "Iz kataloga {shopovi} — {brand} {line} {vitola}{, box-pressed}."`
  `en: "From the {shops} catalogue — {brand} {line} {vitola}{, box-pressed}."`
  Šablon je fiksan da diff bude stabilan.

---

## 9. Quality gate (admit / HOLD) — točni pragovi
Cigara ULAZI u katalog samo ako SVE vrijedi:
1. Kanonski **brend** (Faza B: uvijek; Faza C: mora biti u `brand_dictionary.json`).
2. Prepoznata **vitola** iz lexicona (ne „—").
3. **Format** nije „—" (ima ring i dužinu).
4. **≥1 `offers` s `amount != null`** (ima cijenu bar u jednoj regiji).
5. **Zemlja** poznata (`country` ili `details.origin` → mapirana na hr naziv).
Inače → zapis ide u `app/scripts/output/phase_hold.json` (s razlogom), NE u app.
Skripta na kraju ispiše: `{admitted, held, byReason}`.

---

## 10. Dedupe
- **Ključ** = `slug(brand)|slug(line)|ring|lenMM`.
- Unutar/preko shopova: spoji u jedan zapis (unija `offers`/`markets`, `regionLinks` po §6).
- **Protiv postojećih 514:** ako `id` kolizija ILI (isti brend+linija+vitola+ring±1+len±2mm)
  s postojećom → **NE dupliciraj**; umjesto toga (Faza B) dodaj kao **novu vitolu**
  postojećoj liniji (append u `vitolas[]` + `regionLinks` na razini cigare) i preskoči novi zapis.

---

## 11. Skripte (napisati; determinističke)
1. `app/scripts/build-market-cigars.py` — glavni orkestrator §0.1: čita unified +
   `cigars.json` (bazni, bez `catalogSource==market`), rječnike/lexicon/line_map,
   normalizira (§4–§10), quality gate (§9), zove profile logiku (§8), merge, sort (§0.5), zapis.
   Ima `--phase b|c|all` i `--check-input-sha`.
2. Dijeljeni podatkovni fajlovi (commitati, izvor istine za oba agenta):
   `app/scripts/data/brand_dictionary.json`, `vitola_lexicon.json`, `line_map.json`.
3. Reuse iz `enrich-region-links.py`: `to_eur`, `best_offer`, `SHOP_LABEL`, `is_cuban`
   (izdvojiti u `app/scripts/shop_common.py` i uvesti u obje skripte — bez copy-paste).

---

## 12. `brands.json` (Faza C)
Za svaki NOVI brend dodaj zapis `{ "country": <hr>, "founded": <godina|"—">, "blurb": {hr,en} }`.
Izvor: `details.origin` (zemlja) + kratki neutralni blurb (šablon ako nema kuriranog).
Guard: `cigars.data.test.ts` „brands 1:1" mora ostati zelen (svaki brend ima zapis, i obrnuto).
Faza C batch NE ulazi dok njegovi brendovi nisu u `brands.json`.

---

## 13. Testovi/guardovi (moraju ostati/postati zeleni)
Postojeći + novi u `app/src/data/cigars.data.test.ts` / `integrity.test.ts`:
- brands 1:1; markets poznata tržišta; **embargo** (nijedna kubanka + USA/regionLinks.USA);
- regionLinks host ↔ regija; EU/USA regionLink je `exact` u `cigarShopLinks`;
- **nema `null`/prazan `brand`/`line`/`vitola`**; `format` != prazan za `catalogSource==market`;
- svaki `catalogSource==market` ima `profileEstimated: true` i bar jednu vitolu;
- cijene: `priceEUR`/`regionLinks.*.priceEUR` > 0; USD konverzije nose `priceApprox`.
Naredba: `cd app && npm test` (mora 100% zeleno) + `npx tsc -b`.

---

## 14. Batch redoslijed (fiksno)
**Faza B** (postojeći brendovi), sortirano po broju novih vitola silazno; po batchu 3–5 brendova:
1. Utvrdi listu: `python build-market-cigars.py --phase b --list-brands` (ispiše brend→#novih, deterministički sort).
2. Batch B1 = prvih 5 brendova; B2 = sljedećih 5; … Svaki batch: run skripte (regeneracija
   svih B do tog batcha preko `--brands <lista>`), `npm test`, commit `Phase B batch N: <brendovi>`, push.
**Faza C** (novi brendovi): tek nakon B. Redoslijed batcheva = po `brand_dictionary.json`
frekvenciji silazno; svaki batch prvo doda `brands.json` zapise pa cigare.

---

## 15. Komande (točan redoslijed po batchu)
```bash
cd app
git pull --rebase
# input (ako fali): git show cursor/shop-raw-catalogs-d678:app/scripts/output/cigar_unified_catalog.json > app/scripts/output/cigar_unified_catalog.json
python scripts/build-market-cigars.py --phase b --brands "<batch lista>" --check-input-sha
python scripts/profile-cigars.py            # profil za nove
python scripts/dedupe-data.py               # zadnji, kao i inače
npm test && npx tsc -b
git add -A && git commit -m "Phase B batch N: <brendovi>" && git push -u origin <grana>
```

---

## 16. Definicija gotovog (po batchu)
- `cigars.json` narastao SAMO za kvalitetne unose (quality gate); HOLD zapisi u
  `phase_hold.json` s razlozima.
- 0 embargo prekršaja; brands 1:1; `npm test` + `tsc` zeleno.
- Isti input + isti batch parametri → **identičan** `cigars.json` bez obzira tko pokrene.
