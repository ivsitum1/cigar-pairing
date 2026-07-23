# Workspace self-assessment (agent rules)

**Purpose:** Ponovljiva procjena kvalitete workspace-a (struktura, pravila, alati), ne pojedinačnog LLM odgovora. Za primjer jednokratne dubinske evaluacije vidi [WORKSPACE_EVALUATION.md](WORKSPACE_EVALUATION.md).

**Kada pokrenuti:** nakon većih promjena u pravilima/skills, prije release-a, mjesečno uz `@brain health`, ili kad ugniježđeni projekt mijenja putanje do „brain” foldera.

---

## 1. Prag uspjeha

- **Dimenzije 1–6:** svaka se ocjenjuje **1–10**. Cilj je **prosjek ≥ 8** i **nijedna dimenzija ispod 7** (inače planirati konkretne korake prije tretiranja workspace-a kao „spremnog”).
- **Izlaz agenta** (odvojeno od ove procjene): i dalje vrijedi prag **≥ 9/10** po `.cursor/rules/core-principles.mdc` i `general-rules.mdc` prije isporuke korisniku.

---

## 2. Dimenzije (1–10 svaka)

| ID | Dimenzija | Što provjeriti (indikatori) |
|----|-----------|-----------------------------|
| **D1** | **Accuracy / verifiability** | Zabrana fabrikacije i halucinacija eksplicitna u Tier 0; `verification.mdc` i Swiss Cheese dostupni; citati i fakti moraju biti provjerivi (nema „laganih” izuzetaka u pravilima). |
| **D2** | **Completeness** | `30_system/SKILLS/registry.json` usklađen s postojećim `SKILL_*.md`; pokriveni tipični pipelinei (orchestrator); reporting pravila (CONSORT, PRISMA, …) na mjestu ako ih projekt koristi. |
| **D3** | **Methodology / process** | REFINE i Swiss Cheese za kritične analize opisani; skill gap grana i error learning protokol jasni; learning loop / `99_error_memory.mdc` pod kontrolom (ne preko limita po kategoriji bez reviewa). |
| **D4** | **Clarity / navigability** | `30_system/docs/README.md`, INDEX-i, `.agent/README.md` (ako postoji) omogućuju brzo pronalaženje; nema kritičnih „mrtvih” putanja u dokumentima na koje se svakodnevno oslanjaš. |
| **D5** | **Naturalness / writing support** | Writing tier i `SKILL_avoid-ai-formulations` (ili ekvivalent) dostupni kad je kontekst manuskript. |
| **D6** | **Security / safety** | Nema oslanjanja na neprovjerene kliničke činjenice u pravilima kao na „istinu”; guardrails za destruktivne operacije; MCP i tajne (ako ih ima) nisu u repou. |

**Bodovanje (1–10):** 1 = ozbiljno nedostaje ili je kontradiktorno; 5 = funkcionalno ali s rupama; 8 = dobro za produkciju; 10 = izvrsno, redovito održavano.

---

## 3. Operativni checklist (da / ne)

Označi **Da** / **Ne** / **N/A**. Svako **Ne** zabilježi u „Akcije” ispod.

| # | Stavka |
|---|--------|
| O1 | `python 40_operations/scripts/brain_health.py` (ili `agent-rules/...` ako je brain podfolder) prolazi ili poznata odstupanja su dokumentirana. |
| O2 | Testovi koje održavaš (npr. brain, context_sync, skill_registry) prolaze iz očekivanog korijena projekta. |
| O3 | Putanje u orchestratoru / README za ugniježđeni repo (`agent-rules/` kao podfolder) odgovaraju načinu na koji ti pokrećeš skripte. |
| O4 | Python `40_operations/python/quality_validation/` dostupan; `python 40_operations/scripts/run_quality_validation.py swiss --text test` prolazi iz repo roota. |
| O5 | MCP konfiguracija (npr. `.cursor/mcp.json`) odgovara onome što stvarno koristiš; nema „sjenih” servera bez namjere. |
| O6 | Git stanje: nema neočekivanih necommitanih kritičnih promjena u pravilima prije označavanja verzije kao stabilne. **Iznimka:** tijekom planirane migracije O6 može biti **Ne** ako je ispunjen odjeljak **3a** ispod. |

---

## 3a. Prije commita (D6 – jačanje operativnog praga)

Pri velikom commitu (reorganizacija, nova stabla) prođi ovo prije `git commit`:

| # | Provjera |
|---|----------|
| S1 | **Tajne:** u diffu nema API ključeva, tokena, lozinki, privatnih URL-ova; `.cursor/mcp.json` i slične datoteke samo s placeholderima ili lokalnim putanjama koje su namjerne. |
| S2 | **PHI / osjetljivi podaci:** nisu uključeni u commit (npr. baze, exporti, pravi pacijentski identifikatori). |
| S3 | **Binarni artefakti:** `memory.db`, veliki cache, osobni worktree zapisi: provjeri `.gitignore`; commitaj samo ono što treba biti reproducibilno. |
| S4 | **Putanje:** README, orchestrator i R header komentari usklađeni s [CANONICAL_PATHS.md](CANONICAL_PATHS.md). |
| S5 | **Regresija:** `brain_health.py`, `skill_registry.py validate`, te `pytest 40_operations/tests/scripts/test_quality_validation.py` prolaze iz repo roota. |

Ako su S1–S5 zadovoljeni, migracija može imati „prljav” working tree, ali **D6 u procjeni ne pati** zbog samog necommitanog stanja.

---

## 3b. D4 – brzi kompas

- **Kanonske putanje:** [CANONICAL_PATHS.md](CANONICAL_PATHS.md)
- **Brain vs projekt:** [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md)
- **Indeks dokumenata:** [README.md](README.md) (ovaj folder)

---

## 4. Zapis procjene (kopiraj i popuni)

```text
Datum:              YYYY-MM-DD
Repo / branch:      
Git SHA (opcionalno):
Ocjenjivač:         

Dimenzije (1–10):
  D1 Accuracy:       
  D2 Completeness:   
  D3 Methodology:    
  D4 Clarity:        
  D5 Naturalness:    
  D6 Security:       
  Prosjek (D1–D6):   

Operativno: O1 … O6 (broj „Ne”): __

Sažetak (2–4 rečenice):
  

Akcije (prioritet):
  1. 
  2. 
```

---

## 5. Poveznice

- Kanonske putanje (D4): [CANONICAL_PATHS.md](CANONICAL_PATHS.md)
- Izlazna kvaliteta i iteracija u Pythonu: `40_operations/python/quality_validation/` → `mandatory_self_assess()` (vidi `run_quality_validation.py`)
- Višeslojna verifikacija: `SKILL_swiss-cheese.md`, `.cursor/rules/verification.mdc`
- Telemetrija učenja (opcionalno): [SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md](SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md)

---

**Verzija:** 1.2 | **Datum:** 2026-05-05
