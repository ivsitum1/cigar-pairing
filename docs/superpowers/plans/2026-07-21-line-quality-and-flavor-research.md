# Plan: recheck kvalitete linija + per-linija okusni/pairing profil — za Cursor

**Datum:** 2026-07-21
**Vlasnik izvršenja:** Cursor (web pristup + kuracija)
**Integracija:** Claude (deterministički engine `build-market-cigars.py`)
**Kontekst:** korpus je narastao na ~3200 cigara iz shop scrapea; profil (okusi/tijelo)
je uglavnom procjena. Korisnik je dao primjere (Ashton fragmentacija, Aging Room HR).
Claude je već popravio: HR dostupnost (cross-shop), pravu snagu iz shopa, per-vitola
linkove, opise iz atributa. Ostaje niže.

---

## DIO A — RECHECK kvalitete (kuracija kroz `line_map.json`)

Na temelju primjera pregledaj cijeli korpus i popravi kroz **`app/scripts/data/line_map.json`**
(ključ `"<Brend>::<raw linija>" -> "<kanonska linija>"`; engine konsolidira po (brend, linija)).

### A1. Fragmentacija „bare-vitola" linija (~220)
Primjer: `5 Vegas Churchill`, `5 Vegas Corona`, `5 Vegas Robusto` su zasebne „linije"
imenovane po formatu — trebaju biti JEDNA linija s više vitola.
- Popis (deterministički):
  ```
  cd app && python3 -c "import json,sys;sys.path.insert(0,'scripts');import importlib.util as u;s=u.spec_from_file_location('b','scripts/build-market-cigars.py');m=u.module_from_spec(s);s.loader.exec_module(m);V={m.slug(x) for x,_ in m.load_vitola_lexicon()[0]};d=json.load(open('src/data/cigars.json'));print('\n'.join(sorted(set(c['brand']+'::'+c['line'] for c in d if c.get('catalogSource')=='market' and m.slug(c['line']) in V))))"
  ```
- Za svaki: istraži pravu liniju (brand site / halfwheel / trgovina) i dodaj u
  `line_map.json` mapiranje `"<Brend>::<Vitola>" -> "<Prava linija>"`. Kad je brend
  jednolinijski, mapiraj sve njegove bare-vitola na tu jednu liniju → engine ih spoji
  u jednu cigaru s vitolama.
- Ako je linija stvarno nepoznata/dvosmislena → ostavi (ne izmišljaj).

### A2. Duplikati prema kuriranima
Market linija koja duplicira kuriranu liniju/vitolu (npr. Ashton „Churchill" vs
kurirani „Classic" s Churchill vitolom). Popis:
```
python3 -c "import json;d=json.load(open('app/src/data/cigars.json'));cur={(c['brand'].lower(),v['name'].lower()) for c in d if c.get('catalogSource')!='market' for v in c['vitolas']};print('\n'.join(f\"{c['brand']}::{c['line']}\" for c in d if c.get('catalogSource')=='market' and (c['brand'].lower(),c['line'].lower()) in cur))"
```
→ mapiraj u `line_map.json` na kuriranu liniju (spoji) ili preskoči ako je zaseban proizvod.

### A3. Redundancija imena vitole
Npr. linija „ESG" s vitolama „ESG Robusto/ESG Churchill" — vitola ponavlja liniju.
(Ovo je više engine stvar; prijavi popis, Claude će očistiti u normalizaciji.)

**Pravila A:** samo `line_map.json`. Ne diraj cigars.json/brands.json/engine. Za svaki
netrivijalni mapping upiši izvor u komentar/log. `npm test` mora ostati zelen.

---

## DIO B — Plan 2: per-linija okusni + pairing profil (glavni posao)

Cilj: prave okusne bilješke, tijelo, snaga i **pairing** za istaknute linije (ne
procjena). Novi dijeljeni file: **`app/scripts/data/line_notes.json`**:

```jsonc
"Perdomo::Lot 23": {
  "strength": 3, "body": 3,
  "flavorTags": ["cedar", "kava", "koza"],   // SAMO iz postojećeg rječnika tagova (vidi dolje)
  "note": { "hr": "1–2 rečenice okusa/karaktera", "en": "…" },
  "pairing": { "hr": "npr. srednji rum, bourbon; espresso", "en": "…" },
  "source": "https://…"
}
```

- **`flavorTags`**: SAMO iz poznatog vokabulara engine-a (da pairing radi i test prolazi).
  Popis dopuštenih tagova:
  ```
  cd app && python3 -c "import re;t=open('src/engine/rules.ts').read();import json;print(sorted(set(re.findall(r'\"([a-z-]+)\"',t))))"  # provjeri COMPLEMENTS/TAG_ALIASES
  ```
  (Ako treba nov tag, prijavi Claudeu da ga doda u `rules.ts` — NE koristi nepoznat tag.)
- **`strength`/`body`**: 1–5, iz pouzdanog izvora.
- **`pairing`**: kratko, konkretno (piće/kategorija), činjenično.
- **`source`**: obavezno.

### Prioritet (batch po prominentnosti)
Po broju cigara/linija u katalogu silazno. Batch 20–30 linija. Najpoznatiji brendovi prvo.

### Pravila B (protiv dezinformacija)
- Sve iz pouzdanih izvora (brand site, halfwheel, Cigar Aficionado, Cigar Journal). Citiraj `source`.
- Ako nema pouzdanih okusa → preskoči liniju (ostaje atributna procjena). NE izmišljaj.
- Ne kopiraj recenzije doslovno; kratko i činjenično.

---

## Integracija (Claude, kad Cursor pošalje batcheve)

- `line_map.json` → engine već konsolidira po (brend, linija) na sljedeći `--phase all`.
- `line_notes.json` → Claude dodaje merge korak u engine: kad linija ima `line_notes`,
  koristi prave `flavorTags`/`body`/`strength`/`note`/`pairing` umjesto procjene
  (i makne `profileEstimated` za tu liniju). Deterministički, idempotentno.
- Nakon svakog batcha: `npm test` + `tsc` + build; 1:1 brands; embargo 0.

## Ne diraj (Cursor)
`cigars.json`, `brands.json`, `build-market-cigars.py`, `types.ts`, komponente,
`vitola_lexicon.json`, `brand_dictionary.json`. **Samo** `line_map.json` (Dio A) i
`line_notes.json` (Dio B); `new_brands_draft.json` je zaseban plan (brend metapodaci).

## Definicija gotovog (po batchu)
- A: bare-vitola linije brenda konsolidirane / duplikati mapirani; 0 izmišljenih linija.
- B: istaknute linije imaju prave okuse/tijelo/snagu/pairing + `source`; 0 nepoznatih tagova.
