# Current Architecture Audit

**Created:** 2025-02-08  
**Purpose:** Document existing agent workflow and validation for upgrade planning.

---

## Existing Agents/Roles

| Agent | Description | Entry Point | Output |
|-------|-------------|-------------|--------|
| **Orchestrator** | Single entry; classifies and delegates | `.cursor/rules/00_orchestrator_agent.mdc` (always loaded) | Routes to subagent |
| **Clinical Decision Support** | Clinical scenarios, differential, evidence | Orchestrator → CLINICAL | Scenario, assessment, recommendation |
| **Clinical Research Methodologist** | PICO, design, sample size, reporting | Orchestrator → METHODOLOGY | Protocol, analysis plan |
| **Code Quality Assurance** | RCPM review, code quality | Orchestrator → CODE_QA | Blocking/major/minor/positives |
| **Medical Data Science Coder** | Implementation, R/Python code | Orchestrator → CODE_IMPL | Code, docs, inputs/outputs |
| **Prompt Engineering Specialist** | CRAFT, prompts, RAG | Orchestrator → PROMPT_ENG | Context, task, format |
| **Rules & Roles Maintainer** | Audit rules, status | Orchestrator → RULES_MAINT | Audit report |
| **Statistical Analysis Expert** | Methods, results, assumptions | Orchestrator → STATISTICS | Outcome, method, 95% CI |
| **Academic Writing Specialist** | Manuscript, sections, refs | Orchestrator → WRITING | Prose, Vancouver refs |

- **Role files:** `30_system/behavior_rules/agents/*.md` (reference; not auto-loaded). Tier 3 in context-optimization.
- **Routing:** Keywords, file types (e.g. `.R`/`.Rmd` → STATISTICS), optional `30_system/behavior_rules/tools/agents/agent_auto_detection.R` / `.py`.
- **Predefined pipelines:** For full-workflow requests (e.g. analysis then writing, setup and validate, all figures), the Orchestrator uses **named pipelines** from `30_system/behavior_rules/22_pipeline_and_refinement.md` and `30_system/behavior_rules/23_figure_visualization_pipeline.md`. Pipelines define stages (Retrieve → Plan → Execute → Refine) and skill order. **REFINE** phase (self-assessment, Swiss Cheese when mandatory, AI-check for text) is required for critical outputs; see 22 and `30_system/behavior_rules/05_verification.md`. Figure workflow uses `30_system/SKILLS/SKILL_figure-pipeline.md`.

---

## Validation Mechanisms

| Type | Location | Scoring / Notes |
|------|----------|-----------------|
| **Swiss Cheese (executable)** | `40_operations/python/quality_validation/swiss_cheese.py` | 5 layers: pre-exec → monitored execution → post-validation → meta-review → self-assessment. `validate_with_swiss_cheese(task, executor)`. See `30_system/SKILLS/SKILL_swiss-cheese.md`. |
| **Swiss Cheese (conceptual 30_system/docs)** | `30_system/behavior_rules/05_verification.md` (4 layers), `30_system/behavior_rules/08_swiss_cheese_solution.md` (8 layers) | Reference documentation; executable wrapper in `40_operations/python/quality_validation/` |
| **Setup validation** | `.ai/validate_setup.R`, `.ai/validate_setup.py` | Project structure (folders, templates, paths, git) |
| **Writing iteration** | `30_system/behavior_rules/tools/writing/writing_workflow.R` | Iterates until AI score < 20%; uses `check_ai_score_fast.R` |
| **Self-assessment (Python)** | `40_operations/python/quality_validation/self_assessment.py` | `mandatory_self_assess(output, rubric, max_iterations)`; domain rubrics in `rubrics.py`. Called by Swiss Cheese Layer 5. |
| **Self-assessment (rules)** | `30_system/behavior_rules/01_general_rules.md`, `.cursor/rules/core-principles.mdc` | Minimum 9/10; aim 10/10. Use Python module or CLI `run_quality_validation.py` for programmatic iteration. |

---

## R / Automation

- **R scripts (stats only):** **`40_operations/R/`** at repo root is for statistics, hypothesis testing, simulation, modeling, and power analysis. `40_operations/R/00_paths.R`. Quality validation is **not** in R; see `40_operations/python/quality_validation/`.
- **Python scripts (writing, agents, setup):** `.ai/` (setup, validate_setup, detect_study_type), `30_system/behavior_rules/tools/` (writing, agents, check_ai_score). Writing and other tooling use Python; R is not used for writing.
- **Path convention:** Raw data path configurable via `path_raw_data` in `40_operations/R/00_paths.R` or when loading data; default `file.path(getwd(), "01_input", "data", "00_inbox/raw")`.

---

## File Structure Conventions

- **Cursor rules:** `.cursor/rules/*.mdc` (Tier 1 always; Tier 2 by glob).
- **Skills:** `30_system/SKILLS/SKILL_*.md`; loaded on-demand via `skills-auto-detect.mdc`.
- **Reference:** `30_system/behavior_rules/`, `20_knowledge/reference_library/` (Tier 3, reference only).
- **.agent/ (Context Engineering):** `task/` (PRDs, research), `system/` (architecture), `SOPs/` (procedures, errors), `README.md` (MANDATORY READ-FIRST), `MEMORY.md` (auto-progress). See archived `90_archive/ARCHIVE/planning_history/UPGRADE_PLAN.md` (historical).

---

## Self-Assessment Protocols

- **Rule-based:** Generate → Critique → Rate 1–10 → If <9 improve → Repeat (max 3) → Deliver. Rubric: Accuracy, Completeness, Clarity, Reproducibility, Clinical relevance.
- **Threshold:** Minimum 9/10 to proceed; aim 10/10 (unified across core-principles and 01_general_rules).
- **Automated (Python):** `40_operations/python/quality_validation/self_assessment.py` → `mandatory_self_assess(...)`. Swiss Cheese Layer 5 uses default legacy rubric or extend in code.

---

## Automation Scripts

- **Setup:** `.ai/setup_project.R`, `.ai/setup_project.py`; `.ai/setup_recovery.*`, `.ai/setup_learning.R`.
- **Validation:** `.ai/validate_setup.R`/`.py`.
- **Writing:** `30_system/behavior_rules/tools/writing/writing_workflow.py` (and legacy `.R` variants). Writing tooling is Python.
- **Agents:** `30_system/behavior_rules/tools/agents/agent_auto_detection.py`, `agent_activation_middleware` (Python preferred).
- **Tests:** `40_operations/tests/` (pytest; includes `test_quality_validation.py` for self-assessment / Swiss Cheese).

---

## Pain Points

- **Resolved:** Swiss Cheese and self-assessment in `40_operations/python/quality_validation/` (formerly R).
- `evaluate_rubric_domain()` uses statistics, writing, code, methodology checks in `rubrics.py`.
- No shared assumption-checker or reproducibility-validator R modules.
- No MCP configured in repo for literature/40_operations/R/references/data.

---

## Strengths

- Clear orchestrator + 8 subagents; Cursor rules + skills auto-detect.
- **Executable validation:** Swiss Cheese 5-layer wrapper and mandatory self-assessment in `40_operations/python/quality_validation/`.
- Writing pipeline with AI-score iteration (write → check → revise).
- Setup validation (structure, templates, paths).
- Rich behavior_rules and SKILLS; reporting guidelines (STROBE, CONSORT, PRISMA, etc.) in `.cursor/rules/`.

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
