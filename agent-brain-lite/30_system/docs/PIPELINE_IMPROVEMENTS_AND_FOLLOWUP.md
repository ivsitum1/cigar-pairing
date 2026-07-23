# Dopuna evaluacije workspace-a – Pipeline i prijedlozi za napredak

**Datum:** 2026-03-16  
**Nadopuna:** [WORKSPACE_EVALUATION.md](WORKSPACE_EVALUATION.md) (84/100)

---

## Sažetak

Pregled cijelog workspace-a potvrdio je da su Pipelines 1–6 i 7A/7B dobro definirani u dokumentima, ali postoje **nedovršeni spojevi** (CLI, putanje, varijante) i **konzistentnost putanja**. U nastavku su konkretni prijedlozi za dovršetak i napredak.

---

## 1. Pipeline – dovršetak i nedostaci

### 1.1 run_pipeline.py ne podržava Pipeline 7A/7B

- **Stanje:** `40_operations/scripts/run_pipeline.py` ima `choices=["1","2","3","4","5","6"]`; Pipeline 7 i 7B nisu uključeni.
- **Orchestrator:** U `00_orchestrator_agent.mdc` navedeno je „CLI: `python 40_operations/scripts/run_pipeline.py --pipeline 1 --context "..."`“ i tablica s 7A/7B, ali skripta ih ne izlaže.
- **Prijedlog:** Proširiti `run_pipeline.py`:
  - Dodati opcije `"7"` (7A – Discovery MVP) i `"7B"` (full Discovery).
  - Za `--pipeline 7`: generirati prompt koji referencira `30_system/behavior_rules/24_discovery_pipeline.md`.
  - Za `--pipeline 7B`: referenca na `30_system/behavior_rules/26_discovery_superpipeline.md` i `25_capability_registry.md`.

### 1.2 Pipeline 6 – varijanta za systematic review bez meta-analize

- **Stanje:** U `22_pipeline_and_refinement.md` (oko redaka 92–93) navedeno je: „Systematic review variant: Skip ANALYZE stage if no quantitative synthesis…“
- **Prijedlog:** U orchestratoru u tablici Pipeline Triggers dodati kratku napomenu ili pod-trigger, npr. „systematic review only“ / „narrative synthesis only“ → Pipeline 6 bez ANALYZE. Opcionalno: jedan kratki odlomak u `22_pipeline_and_refinement.md` pod „Pipeline 6 – varijante“ (SR bez MA, SR s MA).

### 1.3 Pipeline 5 – metodološki dijagrami (flowchart, arhitektura)

- **Stanje:** `23_figure_visualization_pipeline.md` navodi „Future: External Diagram Service“ za flowcharts i metodološke dijagrame.
- **Prijedlog:** Ili (a) dodati jedan eksplicitni korak u Pipeline 5: „Ako su potrebni samo metodološki dijagrami (bez podataka), koristi [Mermaid / PlantUML / opis u markdown] dok eksterni servis nije povezan“, ili (b) u istom dokumentu zadržati „Future“ ali dodati jednu konkretnu preporuku (npr. Mermaid u R Markdown / Quarto) kao privremeno rješenje.

### 1.4 LearningRecorder – puna putanja za ingest_learning_block

- **Stanje:** U `26_discovery_superpipeline.md` (korak 45) i `25_capability_registry.md` navedeno je samo `ingest_learning_block.py`; u `24_discovery_pipeline.md` i `14_learning_loop.md` korištena je puna putanja `30_system/behavior_rules/tools/ingest_learning_block.py`.
- **Prijedlog:** U 26 i 25 zamijeniti s `30_system/behavior_rules/tools/ingest_learning_block.py` radi konzistentnosti i rada kada je agent-rules podfolder.

---

## 2. Putanje i konzistentnost (prema WORKSPACE_EVALUATION)

### 2.1 Brain skripte kada je agent-rules podfolder

- **Stanje:** U orchestratoru (Brain Commands) navedeno je `python 40_operations/scripts/brain_status.py` itd. Kada je workspace root projekt koji sadrži `agent-rules/`, te skripte su u `agent-rules/40_operations/scripts/`.
- **Prijedlog:** U `00_orchestrator_agent.mdc` u tablici Brain Commands dodati napomenu: „Ako je agent-rules podfolder u projektu, pokretati iz korijena projekta: `python agent-rules/40_operations/scripts/brain_status.py` (ili `cd agent-rules` pa `python 40_operations/scripts/brain_status.py`).“ Isto u `40_operations/scripts/README.md` u retku za Brain status/audit/health: „When project contains agent-rules as subfolder, use `python agent-rules/40_operations/scripts/brain_status.py` from project root.“

### 2.2 Jedno mjesto za .ai vs .agent

- **Stanje:** WORKSPACE_EVALUATION već preporučuje jasnu definiciju. Pregled potvrdio: `.ai/` se koristi za setup (setup_project, validate_setup, detect_study_type); `.agent/` za kontekst (task, MEMORY, handoff, dreaming).
- **Prijedlog:** U glavni `README.md` u odjeljku Project structure (ili na početku) dodati 2–3 rečenice: „**.agent/** je indeks konteksta agenta (task/, MEMORY.md, handoff_log, dreaming). **.ai/** sadrži skripte za inicijalizaciju projekta i detekciju tipa studije (setup_project, validate_setup, detect_study_type).“

### 2.3 40_operations/R/validation putanje kada je brain podfolder

- **Stanje:** `core-principles.mdc` i `verification.mdc` referenciraju Python `40_operations/python/quality_validation/`. Kada je brain u `agent-rules/`, korijen repoa za pokretanje skripti je unutar tog stabla.
- **Prijedlog:** U `30_system/docs/BRAIN_AND_PROJECT.md` dodati kratku napomenu: „R skripte (npr. 40_operations/R/validation/*) pozivaju se s putanjom relativnom na korijen projekta u kojem se nalazi 40_operations/R/. Ako je brain u podfolderu: `agent-rules/40_operations/R/validation/...`.“

---

## 3. Ostali prijedlozi (srednji / niski prioritet)

### 3.1 30_system/SKILLS/evals – kako pokrenuti evaluaciju

- **Stanje:** WORKSPACE_EVALUATION predlaže kratki opis u `30_system/SKILLS/evals/README.md`. U `40_operations/scripts/README.md` već postoji Skill eval runner i Generate evals.
- **Prijedlog:** U `30_system/SKILLS/evals/README.md` dodati 2–3 rečenice: npr. „Pokretanje evaluacije: s korijena projekta `python 40_operations/scripts/skill_eval_runner.py --skill-id <id>`. Generiranje evals: `python 40_operations/scripts/generate_evals_from_skill.py --skill-id <id>`. Vidi `30_system/docs/SKILL_OPTIMIZATION_AGENT.md`.“

### 3.2 99_error_memory – trim po kategoriji

- **Stanje:** Pravilo: „Max entries per category: 10.“
- **Prijedlog:** Povremeno (npr. uz brain_audit ili mjesečno) pregledati broj unosa po kategoriji i skratiti ako prelazi 10.

### 3.3 Zastarjele reference na .ai za writing/agent alate

- **Stanje:** U `30_system/behavior_rules/CHANGELOG.md`, `30_system/behavior_rules/VERSION.md` i drugim arhivskim dokumentima i dalje se spominju `.ai/writing_workflow`, `.ai/agent_auto_detection` itd. Stvarna lokacija: `30_system/behavior_rules/tools/` (writing, agents).
- **Prijedlog:** U VERSION.md i CHANGELOG.md na vrhu dodati napomenu: „Tools for writing and agents moved to 30_system/behavior_rules/tools/; .ai/ retained for setup/validate/detect only.“ Pojedinačne zamjene putanja u CHANGELOG mogu se raditi postepeno.

---

## 4. Što je već u redu

- **15_agent_roles.md:** Već koristi ispravne putanje `30_system/behavior_rules/tools/agents/agent_auto_detection.R` i `.py`.
- **ingest_learning_block.py:** Postoji u `30_system/behavior_rules/tools/ingest_learning_block.py`; referenciran u 14_learning_loop i 24.
- **Pipeline dokumenti:** 22, 23, 24, 25, 26 međusobno su usklađeni i referencirani u orchestratoru.
- **SKILLS registry i figure-pipeline:** Registry.json i SKILL_figure-pipeline.md postoje; Pipeline 5 je u skills-auto-detect i 23.
- **Reference:** classification_hints.md i skill_task_mapping.md postoje u 30_system/behavior_rules/reference/.

---

## 5. Prioritetizirani popis akcija

| # | Akcija | Prioritet | Datoteke |
|---|--------|-----------|----------|
| 1 | Proširiti run_pipeline.py na 7 i 7B | Visoki | 40_operations/scripts/run_pipeline.py |
| 2 | U orchestrator dodati napomenu za brain skripte (agent-rules podfolder) | Visoki | .cursor/rules/00_orchestrator_agent.mdc |
| 3 | U README definirati .agent vs .ai u jednom odjeljku | Visoki | README.md |
| 4 | U 26 i 25 staviti punu putanju ingest_learning_block.py | Srednji | 30_system/behavior_rules/26_*.md, 25_*.md |
| 5 | U 40_operations/scripts/README dodati napomenu za brain_* kada je brain podfolder | Srednji | 40_operations/scripts/README.md |
| 6 | U BRAIN_AND_PROJECT dodati napomenu za 40_operations/R/validation putanje | Srednji | 30_system/docs/BRAIN_AND_PROJECT.md |
| 7 | Pipeline 6: kratka varijanta „SR without MA“ u 22 ili orchestrator | Niski | 22_pipeline_and_refinement.md, 00_orchestrator_agent.mdc |
| 8 | Pipeline 5: jedna preporuka za metodološke dijagrame (npr. Mermaid) | Niski | 23_figure_visualization_pipeline.md |
| 9 | 30_system/SKILLS/evals/README: kako pokrenuti eval | Niski | 30_system/SKILLS/evals/README.md |
| 10 | VERSION/CHANGELOG napomena o premještaju tools | Niski | 30_system/behavior_rules/VERSION.md, CHANGELOG.md |

---

**Zaključak:** Workspace je konzistentan i spreman za uporabu; ocjena 84/100 ostaje opravdana. Dovršetak Pipeline 7 u CLI, jasnoća putanja kada je brain podfolder i jedinstvena definicija .ai/.agent najviše doprinose napretku bez promjene arhitekture.
