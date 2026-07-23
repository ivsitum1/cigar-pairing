# Workspace Reconstruction Guide – agent rules (Brain)

**Purpose:** Detaljni pregled za rekonstrukciju ovog workspace-a od strane drugog Cursor agenta. Sadrži sve potrebne upute za kopiranje i implementaciju.

## Related Nodes

- [[README]]
- [[30_system/docs/README]]
- [[30_system/docs/GRAPH_CONNECTIVITY_MAP]]
- [[30_system/docs/AUTOMATION_INDEX]]
- [[.cursor/docs/INDEX]]
- [[UBIQUITOUS_LANGUAGE]]

**Version:** 1.1  
**Generated:** 2025-03-01 | **Tier budgets synced:** 2026-05-26 (see §10, `context-optimization.mdc` v3.2)

---

## 1. Sažetak i namjena

Ovaj workspace je **"brain"** (agent-rules) – sustav pravila, vještina i skripti za AI agente u Cursor IDE-u. Koristi se za kliničke/medicinske istraživačke projekte (statistika, pisanje, meta-analiza, validacija). Može postojati kao **standalone** (root = agent-rules) ili kao **subfolder** unutar projekta (brain + project layout).

**Ključni principi:**
- Orchestrator + 8 subagenta (delegiranje po domeni)
- Cursor rules (.mdc) – automatski aktivirani
- Skills (SKILL_*.md) – proceduralne upute, auto-detect po zadatku
- Pipelines – definirane sekvence (analysis→writing, setup→validate, meta-analysis, figure pipeline)
- Swiss Cheese – obavezna validacija kritičnih analiza
- Error Learning – greške se logiraju i promoviraju u 99_error_memory.mdc

---

## 2. Struktura direktorija (za rekonstrukciju)

```
agent-rules/                          # workspace root (ili subfolder "agent-rules" u projektu)
├── .agent/                           # Kontekst za agente (obavezno čitati)
│   ├── README.md                     # INDEX – što čitati kad
│   ├── MEMORY.md                     # Auto-progress log (max ~200 linija)
│   ├── handoff_log.jsonl             # Handoff povijest (from→to, done, next, 30_system/04_documentation/context)
│   ├── task/                         # PRD-ovi, research output
│   └── system/                       # Arhitektura, sheme
│
├── .cursor/                          # Cursor IDE integracija
│   ├── rules/                        # AKTIVNA PRAVILA (.mdc)
│   │   ├── 00_orchestrator_agent.mdc # Orchestrator – routing, delegiranje
│   │   ├── core-principles.mdc       # Fundamentalni zakoni, Swiss Cheese triggeri
│   │   ├── context-optimization.mdc  # Tier sustav, token budget
│   │   ├── skills-auto-detect.mdc    # Task → Skill mapiranje
│   │   ├── general-rules.mdc         # Komunikacija, epistemička iskrenost
│   │   ├── 99_error_memory.mdc       # Naučene greške (STATISTICS, R CODE, WRITING, METHODOLOGY)
│   │   ├── verification.mdc          # Swiss Cheese protokol
│   │   ├── statistics-test-selection.mdc
│   │   ├── writing-avoid-ai.mdc
│   │   ├── writing-manuscript-structure.mdc
│   │   ├── reporting-*.mdc           # strobe, consort, prisma, tripod-ai, stard, care, spirit, squire, cheers
│   │   ├── reporting-auto-detect.mdc
│   │   ├── visualization.mdc
│   │   ├── harness_tdd.mdc
│   │   ├── pipelines-summary.mdc
│   │   ├── discovery-pipeline.mdc
│   │   ├── 50_ml_mlops_standards.mdc
│   │   ├── 51_llm_agent_patterns.mdc
│   │   ├── 52_causal_inference.mdc
│   │   ├── 53_bayesian_workflow.mdc
│   │   └── 60_windows_file_types.mdc
│   ├── scripts/                      # Cursor-local scripts (handoff, error_ops)
│   │   ├── handoff_log.py
│   │   ├── error_ops.py
│   │   └── error_to_learning_bridge.py
│   ├── (see also 40_operations/scripts/ at repo root for brain_status, project_init, …)
│   ├── errors/
│   │   └── error_log.jsonl           # Log grešaka (format: id, ts, cat, sev, ctx, err, fix, promoted)
│   ├── mcp_servers/
│   │   ├── handoff_server.py         # MCP: log_handoff, detect_agent
│   │   └── requirements.txt          # fastmcp>=2.0.0
│   └── mcp.json                      # MCP server konfiguracija
│
├── 30_system/behavior_rules/                   # REFERENCA – agent NE čita za izvršavanje
│   ├── README.md                     # Pregled, migracija status
│   ├── 00_core_principles.md
│   ├── 01_general_rules.md
│   ├── 02_statistics.md
│   ├── 03_scientific_writing.md
│   ├── 04_visualization.md
│   ├── 05_verification.md
│   ├── 06_study_types.md
│   ├── 07_project_structure.md
│   ├── 08_swiss_cheese_solution.md
│   ├── 09_workflow_optimization.md
│   ├── 10_ai_writing_plagiarism.md
│   ├── 11_r_programming.md
│   ├── 12_machine_learning.md
│   ├── 13_agentic_workflow.md
│   ├── 14_learning_loop.md
│   ├── 15_agent_roles.md             # 8 subagenta (reference)
│   ├── 15b_agent_subagent_system.md
│   ├── 16_cursor_optimization.md
│   ├── 18_ml_production.md
│   ├── 19_llm_development.md
│   ├── 20_modern_causal_methods.md
│   ├── 21_publishing_workflow.md
│   ├── 22_pipeline_and_refinement.md # Pipelines 1–4, REFINE faza
│   ├── 23_figure_visualization_pipeline.md  # Pipeline 5
│   ├── agents/                       # Detaljne role definicije
│   ├── tools/                        # Python/R skripte (writing, agents, check_ai_score)
│   └── reference/
│       ├── skill_task_mapping.md
│       └── classification_hints.md
│
├── 30_system/SKILLS/                           # Proceduralne upute (load on-demand)
│   ├── SKILL_setup-project.md
│   ├── SKILL_validate-setup.md
│   ├── SKILL_meta-analysis.md
│   ├── SKILL_forest-plot.md
│   ├── SKILL_publication-bias.md
│   ├── SKILL_test-selection.md
│   ├── SKILL_manuscript-structure.md
│   ├── SKILL_avoid-ai-formulations.md
│   ├── SKILL_ai-detection.md
│   ├── SKILL_consort-checklist.md
│   ├── SKILL_prisma-checklist.md
│   ├── SKILL_strobe-checklist.md
│   ├── SKILL_bayesian-workflow.md
│   ├── SKILL_sensitivity-analysis.md
│   ├── SKILL_target-trial-emulation.md
│   ├── SKILL_grade-assessment.md
│   ├── SKILL_swiss-cheese.md
│   ├── SKILL_figure-pipeline.md
│   └── SKILL_document-conversion.md
│
├── 40_operations/scripts/                          # Brain skripte
│   ├── project_init.py               # Kreira project structure + symlink
│   ├── brain_status.py
│   ├── brain_audit.py
│   ├── brain_health.py
│   ├── brain_init.py
│   ├── context_sync.py
│   ├── memory_trim.py
│   ├── run_pipeline.py
│   ├── run_all_checks.ps1 / .sh
│   ├── worktree_add.ps1 / .sh
│   ├── worktree_cleanup.ps1 / .sh
│   ├── setup_mcp.ps1
│   ├── setup_git_and_push.ps1 / .sh
│   ├── pre-commit-hook.ps1 / .sh
│   ├── changelog_auto.py
│   └── document_conversion/
│
├── 30_system/docs/                             # Dokumentacija
│   ├── BRAIN_AND_PROJECT.md          # Brain vs project layout
│   ├── EXISTING_ARCHITECTURE.md
│   └── ...                             # Stari planovi: 90_archive/ARCHIVE/planning_history/
│
├── 20_knowledge/reference_library/                # Knjige, radovi, knowledge bases
├── 40_operations/
│   ├── R/                               # R samo statistika
│   │   ├── validation/README.md        # redirect na Python
│   │   └── 00_paths.R
│   ├── python/quality_validation/      # self-assessment, Swiss Cheese
│   └── scripts/                         # brain_health, run_quality_validation, …
│
├── .ai/                              # Setup, validate, detect scripts
├── 40_operations/tests/              # pytest testovi
└── 30_system/04_documentation/                 # Ako je agent-rules standalone
    └── context/
        ├── main.md
        ├── commit.md
        └── log.md
```

---

## 3. MCP konfiguracija (mcp.json)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-filesystem", "--root", "."],
      "description": "Access project files"
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-git"],
      "description": "Git operations"
    },
    "pubmed": {
      "command": "python",
      "args": [".cursor/mcp_servers/pubmed_server.py"],
      "env": {"NCBI_API_KEY": "${NCBI_API_KEY}", "NCBI_EMAIL": "${NCBI_EMAIL}"},
      "description": "PubMed search (local FastMCP; pip install -r .cursor/mcp_servers/requirements.txt)"
    },
    "handoff": {
      "command": "python",
      "args": [".cursor/mcp_servers/handoff_server.py"],
      "description": "Log handoffs; detect_agent for low-confidence classification"
    },
    "pdf": {
      "command": "npx",
      "args": ["-y", "@sylphx/pdf-reader-mcp"],
      "description": "Extract text from PDFs"
    }
  }
}
```

**Handoff MCP:** Zahtijeva `fastmcp>=2.0.0` u `.cursor/mcp_servers/requirements.txt`.

---

## 4. Orchestrator i subagenti

| Task Type | Subagent | Output |
|-----------|----------|--------|
| CLINICAL | Clinical Decision Support | Scenario, assessment, recommendation |
| METHODOLOGY | Clinical Research Methodologist | PICO, design, SAP, reporting |
| CODE_QA | Code Quality Assurance | RCPM: blocking/major/minor/positives |
| CODE_IMPL | Medical Data Science Coder | Code, docs, deps |
| PROMPT_ENG | Prompt Engineering Specialist | Context, CRAFT check |
| RULES_MAINT | Rules & Roles Maintainer | Audit, action items |
| STATISTICS | Statistical Analysis Expert | Method, result (95% CI), assumptions |
| WRITING | Academic Writing Specialist | Prose, Vancouver refs, no AI phrases |
| MIXED | Pipeline (npr. STATISTICS → WRITING) | Sekvencijalni handoff |

**Routing:** Keywords + file patterns (npr. `.R`/`.Rmd` → STATISTICS; manuscript → WRITING). Za nisku pouzdanost: MCP `detect_agent(prompt, files)` ili `python 30_system/behavior_rules/tools/agents/agent_auto_detection.py --prompt "..." --files "..." --json`.

---

## 5. Pipelines (22_pipeline_and_refinement.md)

| Pipeline | Stages | Subagents |
|----------|--------|-----------|
| 1: Analysis → Manuscript | RETRIEVE→PLAN→EXECUTE→VALIDATE→EXECUTE→REFINE | STATISTICS → WRITING |
| 2: Setup and validate | RETRIEVE→EXECUTE→VALIDATE | CODE_IMPL |
| 3: Meta-analysis | EXECUTE→VALIDATE | STATISTICS (SKILL_meta-analysis → forest-plot → publication-bias) |
| 4: Manuscript from scratch | PLAN→EXECUTE→VALIDATE→EXECUTE→REFINE | METHODOLOGY → STATISTICS → WRITING |
| 5: Figure/Visualization | Retrieve→Plan→Render→Refine | STATISTICS/CODE_IMPL; SKILL_figure-pipeline |

**REFINE:** Obavezan za kritične analize (primary outcome, meta pooled estimate, kraj analize, pre-publication). Self-assessment ≥9/10, Swiss Cheese kad primjenjivo.

---

## 6. Task → Skill mapiranje (skills-auto-detect.mdc)

| Task / keywords | Skill |
|-----------------|-------|
| Setup project, init | SKILL_setup-project |
| Meta-analysis, forest plot | SKILL_meta-analysis |
| Which test, Welch, test selection | SKILL_test-selection |
| Manuscript structure, IMRaD | SKILL_manuscript-structure |
| Avoid AI phrasing | SKILL_avoid-ai-formulations |
| CONSORT, RCT | SKILL_consort-checklist |
| PRISMA, systematic review | SKILL_prisma-checklist |
| STROBE, observational | SKILL_strobe-checklist |
| Bayesian, prior | SKILL_bayesian-workflow |
| Forest plot | SKILL_forest-plot |
| Publication bias, funnel | SKILL_publication-bias |
| Sensitivity analysis | SKILL_sensitivity-analysis |
| Target trial | SKILL_target-trial-emulation |
| Validate setup | SKILL_validate-setup |
| Swiss cheese, verification | SKILL_swiss-cheese |
| GRADE | SKILL_grade-assessment |
| AI detection, AI score | SKILL_ai-detection |
| Document conversion | SKILL_document-conversion |
| Obsidian / wiki / vault / PKM / wikilinks / Canvas / Bases | SKILL_obsidian-wiki-agent (`obsidian-wiki-agent`) |
| Figure pipeline, all figures | SKILL_figure-pipeline |

---

## 7. Error Learning Protocol

1. **Na korekciju:** ACKNOWLEDGE → FIX → APPEND u `.cursor/errors/error_log.jsonl`:
   ```json
   {"id":"E[N+1]","ts":"[ISO]","cat":"stats|code|writing|methodology|clinical","sev":"critical|high|medium|low","ctx":"[task]","err":"[what]","fix":"[how]","agent":"[who]","project":"[name]","tags":[],"promoted":false}
   ```
2. **Pattern check:** Ako ≥2 slične u istoj kategoriji → promoted:true → dodaj u `99_error_memory.mdc`.
3. **Triggeri:** "zapamti ovo" → odmah PROMOTE; "zaboravi E[ID]" → ukloni; "@audit errors" → `python .cursor/scripts/error_ops.py audit`.

**99_error_memory.mdc** – sekcije: STATISTICS, R CODE, WRITING, METHODOLOGY. Max 10 po kategoriji.

---

## 8. Project initialization (novi projekt)

1. Kreiraj project folder i kloniraj agent-rules:
   ```bash
   mkdir my-study && cd my-study
   git clone <repo> agent-rules
   ```
2. Pokreni:
   ```powershell
   python agent-rules/40_operations/scripts/project_init.py
   ```
   Ili `--no-symlink` ako symlink ne radi (Windows).
3. Otvori **project root** (my-study) u Cursoru, ne agent-rules.

** project_init.py** kreira: `01_input`, `02_analysis`, `03_output`, `04_documentation`, `05_version_control`, `.agent`, te main.md/commit.md/log.md u context.

---

## 9. Handoff format

```
[HANDOFF Subagent1 → Subagent2]
Completed: [1 rečenica]
Next: [1 rečenica]
Context: [≤50 tok]
```

**Obavezno:** Nakon HANDOFF bloka pozvati MCP `log_handoff` (ili `python .cursor/scripts/handoff_log.py append --from X --to Y --done "..." --next "..." --context "..."`).

---

## 10. Tier sustav (context-optimization.mdc v3.2)

**Authority:** `.cursor/rules/context-optimization.mdc` (overrides older totals in this guide).

| Tier | Sadržaj | Budget |
|------|---------|--------|
| Tier 0 (uvijek, 8× alwaysApply) | orchestrator, core-principles, 99_error_memory, context-optimization, general-rules, skills-auto-detect, agent-rules-readonly, 98_honesty_grounding_protocol | ~3000–3800 tok |
| Tier 1 (max 1 aktivna) | Statistics \| Writing \| Reporting | ~500–700 tok |
| Tier 2 (on demand) | 50_ml, 51_llm, 52_causal, 53_bayesian | ~600–900 tok |
| Tier 3 (on demand) | `30_system/SKILLS/*` via registry.json | per YAML `tokens`; **max 2** when `tier3_pairing` allows |

**Composite (rules + Tier 1 + Tier 3):** aim below ~8500 (one skill), below ~9500 (two paired). Overload: >5 active rules = WARN; >8 = STOP.

**Cursor setup:** [30_system/docs/CURSOR_RULES_SETUP.md](docs/CURSOR_RULES_SETUP.md) — avoid duplicate user-global rules.

---

## 11. Swiss Cheese (kada obavezno)

1. Primary outcome analysis  
2. Meta-analysis pooled estimate  
3. Kraj analize (prije Methods/Results teksta)  
4. Priprema za publikaciju  

**Resursi:** `verification.mdc`, `30_system/behavior_rules/05_verification.md`, `30_system/SKILLS/SKILL_swiss-cheese.md`, `40_operations/python/quality_validation/`.

---

## 12. Brain vs project layout

| Brain | Project |
|-------|---------|
| `.cursor/`, `40_operations/scripts/`, `30_system/behavior_rules/`, `30_system/SKILLS/` | `01_input/`, `02_analysis/`, `03_output/`, `30_system/04_documentation/` |
| Git: `git pull` u agent-rules | `.agent/` na project root |

Ako je project root = agent-rules (standalone), sve je u jednom mjestu; `30_system/04_documentation/context/` postoji u rootu.

---

## 13. Ključne skripte i njihova uloga

| Skripta | Svrha |
|---------|-------|
| `40_operations/scripts/project_init.py` | Kreira project structure, main/commit/log templates |
| `40_operations/scripts/brain_status.py` | Brzi status sustava |
| `40_operations/scripts/brain_audit.py` | Full audit (error_ops + bridge + status) |
| `40_operations/scripts/brain_health.py` | Health check (struktura, skripte, MCP) |
| `40_operations/scripts/context_sync.py --trim` | Trim MEMORY.md i log.md |
| `40_operations/scripts/memory_trim.py` | Trim MEMORY |
| `40_operations/scripts/run_pipeline.py` | Pokreće pipeline (--pipeline 1..5) |
| `.cursor/scripts/error_ops.py` | log_error, audit, promote |
| `.cursor/scripts/handoff_log.py` | Fallback handoff log |
| `30_system/behavior_rules/tools/agents/agent_auto_detection.py` | Detekcija subagenta iz prompta |

---

## 14. Brain naredbe (00_orchestrator_agent.mdc)

| User kaže | Akcija |
|-----------|--------|
| @brain status | `python 40_operations/scripts/brain_status.py` |
| @brain audit | `python 40_operations/scripts/brain_audit.py` |
| @brain health | `python 40_operations/scripts/brain_health.py` |
| @sync context | `python 40_operations/scripts/context_sync.py --trim` |
| @audit errors | `python .cursor/scripts/error_ops.py audit` |

---

## 15. Reporting guidelines (.cursor/rules/)

- reporting-strobe.mdc  
- reporting-consort.mdc  
- reporting-prisma.mdc  
- reporting-tripod-ai.mdc  
- reporting-stard.mdc  
- reporting-care.mdc  
- reporting-spirit.mdc  
- reporting-squire.mdc  
- reporting-cheers.mdc  
- reporting-auto-detect.mdc  

---

*Kraj dokumenta. Za rekonstrukciju: slijedi strukturu direktorija, kopiraj sadržaj pravila i SKILLS, konfiguriraj MCP, i pokreni project_init za novi projekt.*
