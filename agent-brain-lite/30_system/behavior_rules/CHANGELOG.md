# Changelog

All notable changes to the Behavior Rules System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.7.1] - 2026-07-03

### Changed
- `reasoning-discipline` v1.1: aligned slice taxonomy to canonical source (S3=alternative hypotheses, S5=named bias/fallacy checklist, S6=causal & decision hygiene); STANDARD tier now runs slices 1,2,5,7 (adds explicit bias checklist). Kept split format and repo error-learning loop.

## [3.7] - 2026-07-03

### Added
- **`reasoning-discipline.mdc`** (Tier 0 gate, ~300 tok) + **`reasoning-discipline-extended.mdc`** (on-demand): 8-slice Swiss Cheese reasoning protocol with Slice 0 proportionality gate (LIGHT/STANDARD/FULL). Philosophy/logic distilled into imperative checks; error learning wired to `error_log.jsonl` → `99_error_memory.mdc` § REASONING.
- `99_error_memory.mdc`: new REASONING category (empty, promotion target).

### Changed
- `context-optimization.mdc`: Tier 0 kernel budget ~3300–4100 tok (reasoning gate added); `reasoning-discipline-extended` listed in Tier 2.
- `30_system/claude.md`: reasoning-discipline pointer in Anti-Hallucination section.

### Fixed
- Restored string literals corrupted by context path migration (27 occurrences, 16 files: handoff JSONL key, memory query defaults, classifier keywords, writing synonyms, reference-doc prose).
- Repaired UTF-8-as-cp1252 mojibake in `MEMORY.md`, `20_modern_causal_methods.md`, `CHANGELOG_AUTO.md`, `SKILL_target-trial-emulation.md`.

## [3.6.1] - 2026-06-28

### Changed
- Generic hostname-conflict handling (`hostname_conflict_files.py`); removed machine-brand references from docs and tooling
- Renamed `SETUP_R_ANALYSIS.md`, `BOOKS_RAG_GPU_RUNBOOK.md`; deleted legacy hostname archive folder
- `cleanup_machine_variants.py`, `workspace_optimization_check.py`, `track_versions.py` use generic detection

## [3.6] - 2026-06-28

### Added
- Cursor hygiene `.mdc` files: `study-types`, `coding-standards-r`, `output-format-standards`, `learning-loop`, `writing-avoid-ai-extended`, `skills-auto-detect-extended`, `orchestrator-skill-gap`, `orchestrator-skilllens`
- Root `LICENSE` (MIT), `GITHUB_BRANCH_PROTECTION.md`, `ERROR_MEMORY_SOP.md`, `90_archive/error_memory_archive.md`

### Changed
- Token budget canonical Tier 0 `~3000–3800 tok`; slim `skills-auto-detect` + `writing-avoid-ai` core; orchestrator split; README/index hub split; 58 `.mdc` count

## [Unreleased]

### Added
- **Cursor hygiene migration (v3.6):** `study-types.mdc`, `coding-standards-r.mdc`, `output-format-standards.mdc`, `learning-loop.mdc`, `writing-avoid-ai-extended.mdc`, `skills-auto-detect-extended.mdc`, `orchestrator-skill-gap.mdc`, `orchestrator-skilllens.mdc`, root `LICENSE` (MIT), `GITHUB_BRANCH_PROTECTION.md`, `ERROR_MEMORY_SOP.md`, `90_archive/error_memory_archive.md`.
- **`30_system/claude_extended.md`** — Workflow extensions split from Tier 0 `claude.md` (load on demand).
- **`.cursor/rules/learning-loop-triggers.mdc`** — Automatic LEARNING_BLOCK emit triggers; referenced from orchestrator ERROR LEARNING protocol.
- **`40_operations/scripts/check_version_sync.py`** — Pre-commit warning when `.mdc` files change without staged `VERSION.md`.
- **`30_system/context/user.template.md`** — Template for user-specific context (fork-friendly).
- **`30_system/claude.md` Tier 0 kernel** — Self-contained operating instructions for Claude outside Cursor IDE.
- **`.cursor/rules/coding-discipline.mdc`** — Four Karpathy-style coding principles. Intended not to overlap with `core-principles.mdc` (safety/accuracy), `python_r_code_always.mdc` (reproducibility/paths), or `harness_tdd.mdc` (testing); each layer addresses a different aspect of discipline.
- **`.cursor/docs/SKILL_CREATION_GUIDE.md`** — Skill-creation guide adapted to this repo’s `30_system/SKILLS/` system (`registry.json`, `skills-auto-detect.mdc`, pipeline tables), rather than the Claude Code plugin format (not relevant here).
- **Skills (phase 1 integration):** `SKILL_r-statistics.md`, `SKILL_statsmodels-python.md`, `SKILL_nonacademic-writer.md`; registry entries and tier-3 pairing rules for non-academic vs manuscript skills.
- **Reference bundles:** `30_system/SKILLS/reference/kdense/`, `reference/scientific_thinking/`, `r_statistics_coding.md`, `r_statistics_packages.md`, `ecc_mle_workflow_snippets.md`.
- **Eval coverage (41/41 skills):** New `evals/*.json` for cohort/manuscript, engineering (grill-me → ralph-loop), scholarly loop, stats stack, Obsidian wiki, EDA, create-skill; agent-seeded `*_outputs.json` for offline regression (no external LLM API).
- **Eval tooling:** `40_operations/scripts/lint_skill_evals.py`, `seed_agent_eval_outputs.py`; expanded `run_all_skill_evals.py` (lint phase, UTF-8 on Windows, optional `--live`).
- **Obsidian hubs:** `Engineering skill loop.md`, `Scholarly skill loop.md`, `Statistics skill stack.md`, `Non-academic writing skill.md`; wiki index/log updates.
- **Task notes:** `.agent/task/skill_auto_detect_smoke.md`, `skill_integration_phase2_backlog.md`.

### Changed
- **Token budget canonical:** Tier 0 bundle `~3000–3800 tok` in `context-optimization.mdc`; orchestrator slice `~2200–2700 tok`.
- **`writing-avoid-ai.mdc`** — Split to core (~800 tok) + `writing-avoid-ai-extended.mdc` (on-demand).
- **`skills-auto-detect.mdc`** (v3.0) — Slim Tier 0 pointer (~150 tok); extended tables in `skills-auto-detect-extended.mdc`; `target-trial-emulation` shortcut.
- **`00_orchestrator_agent.mdc`** — Skill gap and SkillLens detail moved to on-demand `.mdc` files.
- **`pipeline-refinement.mdc`** — Pointer to `pipelines-summary.mdc` (deduplicated pipeline list).
- **`README.md` / `index.md`** — Split roles (GitHub docs vs Obsidian hub); **58** `.mdc` count; MIT license.
- **Manuscript QC stack** — Self-assessment threshold ≥ 9/10 in `58_manuscript_agent_protocol.md`, `SKILL_manuscript-writing.md`, `manuscript_pre_output_checklist.md`, `21_publishing_workflow.md`, eval `manuscript-writing.json`.
- **`agentic-workflow-guardrails.mdc`** (v1.1) — Task/plan globs; error classification LEVEL 1–4; orchestrator step 6 cross-ref.
- **`learning-loop-triggers.mdc`** — Error trigger references guardrails, not inactive `01_general_rules.md`.
- **`30_system/claude.md`** — Tier 0 kernel only; extended protocols pointer.
- **`user.template.md`** — Markdown format aligned with `user.md`.
- **`check_version_sync.py` + pre-commit** — Covers `behavior_rules/*.md` in addition to `.mdc`.
- **`general-rules.mdc`** (v1.2) — Conversational mode merged from Tier 0; **`55_conversational_cognition.mdc`** → thin on-demand pointer.
- **`context-optimization.mdc`** (v3.4) — Tier 0 token estimate without always-on 55.
- **`99_error_memory.mdc`** — `CODE (R-specific)` rename; removed duplicate `## CODE` section.
- **`.cursorrules`** — BLANK confidence thresholds; self-assessment aligned to 9/10 (72/80 iterate); context budget for non-Cursor environments.
- **`.cursor/rules/00_orchestrator_agent.mdc`** (v1.6) — MIXED request tie-breaking; learning loop emit reference.
- **`.cursor/rules/context-optimization.mdc`** (v3.3) — Skill–Rule conflict resolution under AUTHORITY.
- **`01_general_rules.md`** (v1.1) — STATUS header, ⚡ canonical markers, user context pointer (no hardcoded KBC/projects).
- **`13_agentic_workflow.md`** — Quality gate self-assessment ≥ 9/10.
- **`27_rule_maintenance.md`** — Recurring-error eval case step; VERSION staging note for `.mdc` changes.
- **`.pre-commit-config.yaml`** — `version-bump-check` hook.
- **`30_system/context/user.md`** — Enriched with institution, projects, methods from migrated rules content.
- **`.cursor/rules/writing-avoid-ai.mdc`** — New section **Writing Meta-Principles** (Think Before Writing, Precision First, Surgical Revision, Argument-Driven Execution) placed immediately before **Integration with Other Rules**. Not a new file: these principles underpin the existing concrete rules in the same file.
- **`30_system/SKILLS/registry.json`** — Zip-sourced skills wired; disambiguation and triggers for R vs statsmodels vs non-academic writer.
- **Routing docs:** `skill_task_mapping.md`, `classification_hints.md`, `SKILLS_INDEX.md`, `22_pipeline_and_refinement.md` (Pipelines 8–9, blog ad hoc); `skills-auto-detect.mdc`, orchestrator token-budget pointer.
- **Multiple `SKILL_*.md`** — Cross-links, reference_files, and alignment with restored reference paths (test-selection, meta-analysis, scholarly/engineering loops).
- **`40_operations/scripts/run_all_skill_evals.py`** — Full-registry batch with lint gate; documents agent-only eval path per `SKILL_OPTIMIZATION_AGENT.md`.

*Skill integration phase 1 + offline eval regression; 2026-05-16.*

*Integration work recorded from Claude Code session; 2026-04-19.*

## [3.3] - 2026-04-10

### Added
- **`27_rule_maintenance.md`** — Protocol for proposing, reviewing, versioning, and deprecating `behavior_rules` files.
- **`28_external_integration.md`** — Retry and fallback behavior when external MCPs (PubMed, filesystem, etc.) fail during discovery pipelines.

### Changed
- **`00_core_principles.md`** — Conflict resolution between rules; confidence declaration framework (canonical source).
- **`01_general_rules.md`** — Confidence and self-assessment deduplicated; pointers to `00_core_principles.md` and `13_agentic_workflow.md`.
- **`02_statistics.md`** — Survival tests, effect-size table, Bayesian decision rule, clustered/hierarchical data (ICC, mixed models).
- **`03_scientific_writing.md`** — Context rule for jargon vs clarity by IMRaD section.
- **`04_visualization.md`** — Mandatory colorblind check (`colorblindr::cvd_grid`); font specifications.
- **`05_verification.md`** — 8-layer Swiss Cheese cross-reference to `08_swiss_cheese_solution.md` (replaces inline 4-layer diagram).
- **`06_study_types.md`** — Hybrid designs (nested case-control, case-cohort).
- **`09_workflow_optimization.md`** — Workflow dependency map; Workflows 2–4 and 8 shortened to cross-references (`02`, `03`, `10`, `21`).
- **`11_r_programming.md`** — Native pipe `|>` default; `%>%` when `.` placeholder needed.
- **`12_machine_learning.md`** — Clinical interpretability (SHAP); when classical statistics beats ML.
- **`13_agentic_workflow.md`** — Self-assessment protocol pointer; loop detection; timeout rules.
- **`15_agent_roles.md`** — Collaboration/orchestration deduplicated; pointer to `15b` and `22`.
- **`18_ml_production.md`** — Scope note: validation methodology in `12_machine_learning.md`.
- **`20_modern_causal_methods.md`** — PS method decision algorithm (ATT/ATE, IPTW, TMLE, MSM).
- **`21_publishing_workflow.md`** — Desk rejection risk factors and presubmission inquiry template.
- **`22_pipeline_and_refinement.md`** — Pipeline 7 stage detail deduplicated to `24`/`26`/`25`.
- **`24_discovery_pipeline.md`** — LEARNING_BLOCK format deduplicated to `14_learning_loop.md`.
- **`26_discovery_superpipeline.md`** — Red Team tie-breaking rule.
- **Follow-up (verification):** `track_versions.py check` now passes — `**Version:**` footers added to core files and agent/tool `.md` that lacked them; hostname-conflict filenames excluded from mandatory version check; `24_discovery_pipeline.md` REFINE bullets no longer say “see below” for LEARNING_BLOCK; `.cursor/rules/general-rules.mdc` points to `00_core_principles.md` for canonical confidence.
- **Follow-up (versions):** `12_machine_learning.md` bumped to **2.1**; `10_ai_writing_plagiarism.md` footer aligned to **3.0**; `README.md` system **3.3**; `track_versions.py` now parses only `**Version:**` (avoids `R version: 4.3.0`), skips `VERSION.md` self-scan and hostname-conflict clones, prefers `**Last updated:**` over `**Created:**`, and regenerates `VERSION.md` with supplementary `.py` / `.ai` tables.

## [3.2] - 2025-01-27

### Added
- **NEW:** Integrated Writing Workflow with AI Score Check
  - Real-time banned words and AI phrase checking (`.ai/writing_realtime_check.py/R`)
  - Automatic text revision engine (`.ai/writing_auto_revise.py/R`)
  - Real-time feedback system (`.ai/writing_feedback.py/R`)
  - Complete writing workflow (`.ai/writing_workflow.py/R`)
  - Fast AI score checking (`.ai/check_ai_score_fast.py/R`)
  - Advanced AI detection methods (`.ai/ai_detection_advanced.py`)
    - BERT-based detection
    - Gradient Boosting models
    - Ensemble methods (Logistic Regression, Naive Bayes, Random Forest, LightGBM)
    - N-gram models (unigram, bigram)
    - RADAR-inspired robust detection
- **NEW:** Workflow 7: Integrated Writing with AI Check in `09_workflow_optimization.md`
- **ENHANCED:** `check_ai_plagiarism.py` with `check_ai_score_only()` function
- **ENHANCED:** `check_ai_plagiarism.py` with advanced detection methods integration
- **ENHANCED:** `agent_activation_middleware.R` with automatic writing workflow integration

### Changed
- **ENHANCED:** `10_ai_writing_plagiarism.md` (v2.0 → v3.0)
  - Added "Integrated Writing Workflow" section
  - Added "Advanced AI Detection Methods" section
  - Documented real-time checking and automatic iteration
- **ENHANCED:** `agents/08_academic_writing_specialist.md` (v1.0 → v2.0)
  - Added "Integrated Writing Workflow" section
  - Documented automatic AI score checking
  - Documented real-time feedback integration
- **ENHANCED:** `09_workflow_optimization.md` (v2.0 → v3.0)
  - Added "Workflow 7: Integrated Writing with AI Check"
  - Documented complete workflow steps and components
- **ENHANCED:** `tools/check_ai_plagiarism.py` (v1.0 → v2.0)
  - Added `check_ai_score_only()` function for fast checking
  - Integrated advanced detection methods (BERT, Gradient Boosting, Ensemble, N-grams, Robust)
  - Added support for new tool flags: `bert`, `gradient_boosting`, `ensemble`, `ngram`, `robust`, `combined_advanced`
- **ENHANCED:** `.ai/agent_activation_middleware.R` (v1.0 → v2.0)
  - Added automatic writing workflow integration for Academic Writing Specialist
  - Added `enable_writing_workflow` parameter
  - Automatic loading of writing workflow modules

### Technical Details
- Writing workflow automatically iterates until AI score < 20% or max iterations (5) reached
- Real-time checking provides immediate feedback during writing
- Auto-revision engine fixes banned words, AI phrases, and sentence patterns
- Advanced detection methods improve accuracy and robustness
- Full integration with agent activation system

## [3.1] - 2025-01-27

### Added
- **NEW:** Agent auto-detection system (`.ai/agent_auto_detection.R` and `.py`)
  - Automatic agent detection from user prompts
  - Keyword and file pattern matching
  - Confidence scoring (0-1 scale)
  - Integration with Cursor chat system
- **NEW:** Setup validation system (`.ai/validate_setup.R` and `.py`)
  - Project structure validation
  - Template files validation
  - R scripts syntax checking
  - Path validation in scripts
  - Git setup validation
  - Dependencies checking
- **NEW:** Study type auto-detection (`.ai/detect_study_type.R` and `.py`)
  - Automatic study type detection from project name
  - File pattern analysis
  - Confidence scoring
  - Study-specific folder generation (PRISMA, CONSORT, STROBE)
- **NEW:** Error recovery system (`.ai/setup_recovery.R` and `.py`)
  - Checkpoint creation before setup
  - Rollback functionality
  - Error fix suggestions
  - Automatic recovery on failure
- **NEW:** Learning integration (`.ai/setup_learning.R`)
  - Setup event logging
  - Pattern learning from previous setups
  - User preference tracking
  - Structure adaptation based on history
- **NEW:** Agent activation middleware (`.ai/agent_activation_middleware.R`)
  - Automatic agent activation based on context
  - Context scanning for triggers
  - Agent rules loading
  - Activation confirmation system

### Changed
- **ENHANCED:** `.ai/setup_project.R` (v1.0 → v3.1)
  - Added pre-flight checks
  - Integrated study type auto-detection
  - Added checkpoint creation
  - Integrated learning logging
  - Added automatic validation
  - Added error recovery wrapper
  - Added study-specific folder creation
- **ENHANCED:** `.ai/setup_project.py` (v1.0 → v3.1)

> **Note:** Writing i agent tools koji su ovdje referencirani pod `.ai/` (npr. `writing_workflow`, `agent_auto_detection`, `check_ai_score_fast`) u aktualnoj verziji repozitorija nalaze se u `30_system/behavior_rules/tools/`. `.ai/` je zadržan za setup i validacijske skripte, a ove povijesne unose treba čitati s tom migracijom na umu.
  - Same enhancements as R version
  - Added argparse for command-line options
  - Enhanced error handling
- **ENHANCED:** `30_system/behavior_rules/15_agent_roles.md` (v2.0 → v2.1)
  - Added AUTO-DETECTION IMPLEMENTATION section
  - Documented agent activation middleware
  - Added prompt → agent mapping examples
- **ENHANCED:** `30_system/behavior_rules/09_workflow_optimization.md` (v1.0 → v2.0)
  - Added Enhanced Setup Workflow section
  - Documented all new components
  - Added workflow diagrams
- **ENHANCED:** `30_system/behavior_rules/tools/learning_loop.py` (v1.0 → v1.1)
  - Added `setup_workflow` to AGENT_DOMAINS
  - Added setup-specific learning domains

### Fixed
- Improved error handling in setup scripts
- Better cross-platform compatibility (Windows/Linux/Mac)
- Enhanced validation reporting

## [3.0] - 2025-01-11

### Added
- **NEW:** Core principles file (00_core_principles.md)
  - Fundamental priority order (ACCURACY > SPEED > CONVENIENCE)
  - Fundamental laws (never hallucinate, never fabricate, etc.)
  - Mandatory self-assessment threshold (9/10 minimum)
  - Quality gates checklist
  - Always loaded (~200 tokens)
- **NEW:** Context optimization file (17_context_optimization.md) — *later removed; active version is `.cursor/rules/context-optimization.mdc`*
  - 3-tier hierarchical loading architecture
  - Context budget allocation
  - Rule priority hierarchy
  - On-demand loading triggers
  - Overload response protocol
  - Always loaded (~150 tokens)
- **NEW:** Medical Data Science Laboratory knowledge base
  - Complete 17-layer methodological framework
  - Reference only (not loaded into 30_system/context)
  - Located in `20_knowledge/reference_library/statistics/knowledge_bases/medical_data_science_laboratory.md`
- **NEW:** Digital Twin Blueprint knowledge base
  - ICU/clinical research digital twin architecture
  - 7-layer architecture, validation levels, counterfactual engine
  - Reference only (not loaded into 30_system/context)
  - Located in `20_knowledge/reference_library/statistics/knowledge_bases/digital_twin_blueprint.md`

### Changed
- **ENHANCED:** 02_statistics.md (v1.0 → v2.0)
  - Added complete statistical workflow protocol (Steps 0-11, mandatory)
  - Added FlexPlot-first exploration protocol
  - Added distribution auto-check function
  - Added bootstrap workflow for effect sizes and CI
  - Added MICE workflow for missing data
- **ENHANCED:** 05_verification.md (v2.0 → v3.0)
  - Added 4-layer Swiss Cheese Defense Architecture diagram
  - Increased mandatory self-assessment threshold from ≥8/10 to ≥9/10
  - Added quality metrics and thresholds
  - Enhanced with structured architecture from SCIENTIFIC_AGENT_RULES.md
- **ENHANCED:** 10_ai_writing_plagiarism.md (v1.0 → v2.0)
  - Added complete banned words/phrases list (mandatory elimination)
  - Added banned sentence patterns (negation reframes, rule of three, etc.)
  - Added natural writing variation rules (sentence length, paragraph length, opening words)
  - Added scientific text specific guidelines (academic/research writing standards)
- **ENHANCED:** 11_r_programming.md (v1.0 → v2.0)
  - Added complete R statistical workflow protocol (Steps 0-11, mandatory)
  - Added FlexPlot integration patterns
  - Added model selection decision tree
  - Added output requirements checklist
- **ENHANCED:** 12_machine_learning.md (v1.0 → v2.0)
  - Added digital twin architecture (7 layers)
  - Added counterfactual engine requirements
  - Added validation levels for digital twins (5 levels)
  - Added digital twin vs ML model comparison
  - Added failure modes and minimal viable digital twin
- **ENHANCED:** 15_agent_roles.md (v1.2 → v2.0)
  - Added auto-detection protocol for agent activation
  - Added trigger-based agent selection (file types, keywords)
  - Added agent handoff protocol (context brief, max 50 tokens)
- **ENHANCED:** 16_cursor_optimization.md (v1.0 → v2.0)
  - Added Cursor rules generator meta-pattern
  - Added auto-generation of project-specific rules
  - Added context overload detection and response protocol
  - Added quick commands system (/plan, /check, /agent, /rules, /optimize)
  - Added context budget management
- **ENHANCED:** modern_statistical_literature_2024_2025.md
  - Added verification status and implementation maturity section
  - Added evaluation criteria (theoretical soundness, inferential validity, implementation maturity, clinical realism)
  - Added status indicators for each method (experimental, mature, production-ready, etc.)

### Architecture Improvements
- Implemented 3-tier hierarchical loading system
  - Tier 1: Core Layer (always loaded, ~500 tokens)
  - Tier 2: Domain Layer (on-demand, ~300-500 tokens)
  - Tier 3: Knowledge Base (referenced, not loaded)
- Reduced base context from ~2000 tokens to ~500 tokens
- Maintained full capability through on-demand loading
- Optimized for speed and accuracy without compromise

## [2.4] - 2025-01-07

### Added
- Agent 8: Academic Writing Specialist (agents/08_academic_writing_specialist.md)
  - Expert in natural, human-like scientific writing
  - AI pattern avoidance (eliminates typical AI phrases)
  - Sentence variation (beginnings, lengths, structures)
  - Vocabulary rotation and active voice preference
  - Writing protocol with planning, writing, and revision steps
  - Integration with all other agents for manuscript writing

### Changed
- Updated 15_agent_roles.md to include Academic Writing Specialist
  - Updated from seven to eight specialized agent roles
  - Added to agent selection guide
  - Added to multi-agent workflow examples
  - Added to agent learning domains
- Updated README.md to reflect new agent in folder structure

## [2.3] - 2025-01-07

### Added
- Agent roles system (15_agent_roles.md)
  - Seven specialized agent roles (Clinical Decision Support, Clinical Research Methodologist, Code Quality Assurance, Medical Data Science Coder, Prompt Engineering Specialist, Rules & Roles System Maintainer, Statistical Analysis Expert)
  - Agent collaboration protocols
  - Inter-agent communication rules
  - Agent selection guide
  - Multi-agent workflow examples
  - Universal rules applying to all agents
  - Agent learning and adaptation protocol
- Cursor optimization rules (16_cursor_optimization.md)
  - Cursor IDE-specific optimizations
  - Composer mode best practices
  - Code reference format (```startLine:endLine:filepath```)
  - @-mention usage for file/function references
  - Token efficiency strategies
  - Context management for speed
  - Accuracy improvements for Cursor
- Integrated Medical Data Science Laboratory knowledge base
- Added references to knowledge bases in relevant behavior rules
- Created comprehensive knowledge base documentation

### Changed
- Updated README.md with knowledge base references
- Enhanced agent role documentation with learning integration

## [2.2] - 2024-12-31

### Added
- R programming rules (11_r_programming.md)
  - Detailed R-specific rules
  - Vectorization, namespace conflicts, factor handling
  - Common pitfalls and how to avoid them
  - R code quality checklist
  - R code templates
- Machine learning rules (12_machine_learning.md)
  - Data leakage prevention
  - Safe ML pipeline template
  - Model validation checklist
  - Fairness & bias checking
- Agentic workflow controls (13_agentic_workflow.md)
  - Task decomposition protocol
  - Checkpoint system
  - Rollback protocol
  - Progress tracking
- Learning loop protocol (14_learning_loop.md)
  - Learning loop architecture
  - Observation protocol
  - Analysis protocol
  - Adaptation protocol
  - Evaluation protocol

### Changed
- Expanded 01_general_rules.md with:
  - Confidence Declaration Requirements (🟢/🟡/🔴 format)
  - Context Management Protocol
  - Security Guardrails (PHI protection, input validation)
  - Emergency Protocols (stop triggers, escalation matrix)
  - Extended Error Handling (4-level classification)
  - Extended Self-Assessment (more detailed matrix)
  - Extended R Best Practices (vectorization, namespace, factors, pitfalls)
  - Extended Output Format Standards

## [2.1] - 2024-12-31

### Added
- Study types rules (06_study_types.md)
- Project structure rules (07_project_structure.md)
- Swiss Cheese solution (08_swiss_cheese_solution.md)
- Workflow optimization (09_workflow_optimization.md)
- AI writing plagiarism detection (10_ai_writing_plagiarism.md)

## [2.0] - 2024-12-31

### Added
- Consolidated behavior rules system
- General rules (01_general_rules.md)
- Statistics rules (02_statistics.md)
- Scientific writing rules (03_scientific_writing.md)
- Visualization rules (04_visualization.md)
- Verification protocol (05_verification.md)
- Reference library structure
- Tools directory with learning loop and plagiarism checker

### Changed
- Reorganized from single `.ai/rules.md` to modular structure
- Consolidated duplicate rules into appropriate files

---

## Version History Notes

- **3.0**: Major architecture optimization with hierarchical loading, new core files, enhanced workflows, and knowledge bases
- **2.4**: Added Academic Writing Specialist agent
- **2.3**: Major expansion with agent roles system and Cursor optimizations
- **2.2**: Added R programming, ML, and workflow controls
- **2.1**: Added study types, project structure, and workflow optimization
- **2.0**: Initial consolidated behavior rules system

---

**Version:** 3.3  
**Last updated:** 2026-04-10

## Semantic graph (auto)

- [[Skill registry]]
- [[Skill gap pipeline]]
- [[Behavior rules hub]]
- [[Orchestrator - agent roles]]
- [behavior rules INDEX](../docs/indexes/behavior_rules_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[skills-auto-detect]]
- [[README]]
- [[Non-academic writing skill]]
- [[VERSION]]
- [[Skill registry]]
