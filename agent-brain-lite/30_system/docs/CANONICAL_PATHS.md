# Kanonske putanje (agent rules)

**Svrha:** Jedno mjesto za D4 (navigacija). Sve skripte i dokumenti koji opisuju „gdje što leži” trebaju se slagati s ovim popisom.

---

## Korijen repozitorija

U daljnjem tekstu **repo root** = mapa koja sadrži `.cursor/`, `30_system/`, `40_operations/` (standalone brain) ili **`agent-rules/`** kad je brain ugniježđen u veći projekt.

| Sadržaj | Kanonska putanja | Napomena |
|---------|------------------|----------|
| Cursor pravila | `.cursor/rules/*.mdc` | Aktivna pravila za agenta |
| Ponašanje (referenca) | `30_system/behavior_rules/` | Ne učitavati direktno u kontekst osim kad treba dubina |
| Skills | `30_system/SKILLS/SKILL_*.md` + `30_system/SKILLS/registry.json` | Jedan izvor istine za registry |
| Brain Python skripte | `40_operations/scripts/` | `brain_health.py`, `skill_registry.py`, `run_quality_validation.py`, … |
| **Kvaliteta (self-assessment, Swiss Cheese)** | **`40_operations/python/quality_validation/`** | **Ne u R-u**; R je samo za statistiku |
| R statistika | `40_operations/R/` | Modeliranje, inferencija, simulacije, power; vidi `00_paths.R` |
| Dokumentacija sustava | `30_system/docs/` | INDEX: [README.md](README.md) |
| Kontekst agenta (projekt) | `.agent/` | MEMORY, task, handoff; uz puni projekt i `30_system/04_documentation/` |
| Faza / OTA kontekst (main, commit, log) | `30_system/04_documentation/context/` | Kanonski triplet `main.md`, `commit.md`, `log.md` (vidi `project_init.py`, `brain_health.py`) |
| Identitet / dugoročni čvorovi (brain repo) | `30_system/context/` | `user.md`, `soul.md`, `memory.md` (odvojeno od faze u `04_documentation/context/`) |
| Setup / init | `.ai/` | `setup_project`, `validate_setup`, … |

---

## Python: self-assessment i Swiss Cheese

| Modul | Putanja |
|-------|---------|
| Paket | `40_operations/python/quality_validation/` |
| Self-assessment | `quality_validation/self_assessment.py` → `mandatory_self_assess` |
| Swiss Cheese | `quality_validation/swiss_cheese.py` → `validate_with_swiss_cheese` |
| Domenske rubrike | `quality_validation/rubrics.py` |
| CLI | `40_operations/scripts/run_quality_validation.py` |

**PYTHONPATH:** dodaj `40_operations/python`, zatim:

```python
from quality_validation import mandatory_self_assess, validate_with_swiss_cheese
```

**CLI (bez PYTHONPATH):**

```bash
python 40_operations/scripts/run_quality_validation.py assess --text "..." --domain statistics
python 40_operations/scripts/run_quality_validation.py swiss --text "hello"
```

---

## R: samo statistika

| Datoteka | Putanja |
|----------|---------|
| Putanje za podatke | `40_operations/R/00_paths.R` |
| Napomena | `40_operations/R/validation/README.md` – redirect na Python |

---

## Testovi

| Stack | Putanja |
|-------|---------|
| pytest (brain, skripte, quality_validation) | `40_operations/tests/` |

---

## MCP (opcionalno)

| Svrha | Putanja |
|-------|---------|
| Ovisnost za MCP handoff poslužitelj | `40_operations/requirements-optional-mcp.txt` (`fastmcp`) |

Nakon `pip install -r 40_operations/requirements-optional-mcp.txt`, `brain_health.py` bi trebao prijaviti `mcp_deps: ok (fastmcp available)`.

---

## Legacy root → canonical (compatibility bridges)

Korijenski direktoriji s jednim `README.md` su **mostovi**; ne koristiti za nove reference.

| Legacy (root) | Kanonska putanja |
|---------------|------------------|
| `behavior_rules/` | `30_system/behavior_rules/` |
| `context/` | `30_system/context/` |
| `SKILLS/` | `30_system/SKILLS/` |
| `wiki/` | `20_knowledge/wiki/` |
| `reference_library/` | `20_knowledge/reference_library/` |
| `docs/` | `30_system/docs/` |
| `tests/` | `40_operations/tests/` |
| `R/` | `40_operations/R/` |
| `scripts/` | `40_operations/scripts/` |
| `logs/` | `40_operations/logs/` |
| `raw/` | `00_inbox/raw/` |
| `projects/` | `10_projects/projects/` |
| `shared-brand/` | `30_system/shared-brand/` |
| `ARCHIVE/` | `90_archive/ARCHIVE/` |
| `artifacts/` | `90_archive/artifacts/` |

**Još nije migrirano (pravi sadržaj u korijenu):** `outputs/`, `data/`, `books_rag/` (→ `memory_engine/`), korijenski `scripts/` (9 datoteka ako postoje izvan bridgea). Vidi backlog u `.agent/task/brain_health_audit_2026-06-17.md`.

---

## Test bootstrap (portabilno)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest 40_operations/tests -q
```

Ne oslanjati se na stroj-specifične putanje (npr. `.venv-ocr` s drugog računala). OCR vendor: `40_operations/requirements-ocr.txt`.

---

## Poveznice

- Ugniježđeni projekt i brain: [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md)
- Operativna procjena workspace-a: [WORKSPACE_SELF_ASSESSMENT.md](WORKSPACE_SELF_ASSESSMENT.md)
- Python README: `40_operations/python/README.md`

**Verzija:** 1.3 | **2026-06-17**
