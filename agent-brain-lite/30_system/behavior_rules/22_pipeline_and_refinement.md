> **⚠️ MIGRATED** -> `.cursor/rules/pipeline-refinement.mdc` (2026-05-08)

# Pipeline Architecture and Refinement (PaperBanana-Inspired)

## Purpose

This document adapts ideas from the **PaperBanana** agentic framework (Retrieve → Plan → Render → Refine) to improve our workflow: **explicit pipeline stages**, **ordered agent and skill sequences**, and a **Refine** phase. It does not replace the Orchestrator or existing handoffs; it extends them with named pipelines and optional Critic/Refinement behaviour.

**Version:** 1.0  
**Last updated:** 2026-04-10  
**Reference:** PaperBanana (paperbanana.org); Orchestrator: `.cursor/rules/00_orchestrator_agent.mdc`; Skills: `.cursor/rules/skills-auto-detect.mdc`.

---

## PaperBanana Parallels

| PaperBanana | Our system (adapted) |
|-------------|----------------------|
| **Retrieve** – gather context | **RETRIEVE** – load protocol, data context, literature; can be implicit in first subagent or a short "30_system/context" step |
| **Plan** – design layout / steps | **PLAN** – outline (METHODOLOGY: design/SAP; STATISTICS: analysis plan; WRITING: section outline) |
| **Render** – generate output | **EXECUTE** – primary subagent produces output (STATISTICS, WRITING, CODE_IMPL, etc.) |
| **Refine** – self-critique, iterate | **REFINE** – self-assessment, Swiss Cheese when mandatory, AI-check for text; optional **Critic** pass |

---

## Named Pipelines

Predefined pipelines bind **stages** to **subagents** and optionally **skills** in sequence. The Orchestrator uses these when the task matches a "full workflow" (e.g. "analysis then writing Methods", "setup project and validate"). See also **Pipeline 5** (Figure/Visualization) in `30_system/behavior_rules/23_figure_visualization_pipeline.md`.

### Pipeline 1: Analysis → Manuscript (STATISTICS → WRITING)

| Stage    | Subagent   | Optional skill(s) | Output |
|----------|------------|-------------------|--------|
| RETRIEVE | (30_system/context)  | —                 | Protocol/data/literature in scope |
| PLAN     | METHODOLOGY or STATISTICS | —       | Analysis plan / section outline |
| EXECUTE  | STATISTICS | Per task (e.g. SKILL_meta-analysis, SKILL_test-selection) | Tables, figures, numerical results |
| VALIDATE | STATISTICS | SKILL_swiss-cheese (if critical) | Validation pass; 9/10 self-assessment |
| EXECUTE  | WRITING    | SKILL_manuscript-writing, SKILL_manuscript-structure, SKILL_avoid-ai-formulations | Methods/Results text |
| REFINE   | WRITING    | SKILL_manuscript-writing (QC gate), SKILL_ai-detection, internal revise loop | Text below AI target |

Handoff: STATISTICS → WRITING with ≤50 token context (see `00_orchestrator_agent.mdc`).

### Pipeline 2: Setup project and validate

| Stage    | Subagent  | Optional skill(s)        | Output |
|----------|-----------|-------------------------|--------|
| RETRIEVE | (30_system/context) | —                       | Project name, study type |
| EXECUTE  | CODE_IMPL  | SKILL_setup-project     | Folder structure, templates |
| VALIDATE | CODE_IMPL  | SKILL_validate-setup    | Validation report |

### EDA-first (from 00_inbox/raw/prepared data)

When analysis starts from data without prior EDA:

| Stage    | Subagent   | Skill / action | Output |
|----------|------------|----------------|--------|
| EXECUTE  | STATISTICS | SKILL_eda-flexplot: exploratory analysis → run `40_operations/R/exploratory/eda_flexplot.R` (visual EDA) | Descriptives, flexplot figures, summary |
| PAUSE    | —          | Present results and suggest options (test-selection, meta-analysis, bayesian-workflow, etc.) | **Do not** run inferential analysis |
| EXECUTE  | STATISTICS | User specifies method → load corresponding SKILL (e.g. test-selection, meta-analysis) | Inferential results per chosen skill |

### Pipeline 3: Meta-analysis (single domain, ordered skills)

| Stage    | Subagent   | Skills in order | Output |
|----------|------------|-----------------|--------|
| EXECUTE  | STATISTICS | SKILL_meta-analysis → SKILL_forest-plot → SKILL_publication-bias | Full meta-analysis + figures + bias check |
| VALIDATE | STATISTICS | SKILL_swiss-cheese (if primary outcome) | Validation |

### Pipeline 4: Manuscript from scratch (METHODOLOGY → STATISTICS → WRITING)

| Stage    | Subagent    | Optional skill(s) | Output |
|----------|-------------|-------------------|--------|
| PLAN     | METHODOLOGY | —                 | PICO, design, analysis plan |
| EXECUTE  | STATISTICS  | Per design        | Results |
| VALIDATE | STATISTICS  | SKILL_swiss-cheese when critical | Validated results |
| EXECUTE  | WRITING     | SKILL_manuscript-structure, SKILL_consort-checklist / PRISMA / STROBE | Draft sections |
| REFINE   | WRITING     | SKILL_avoid-ai-formulations, SKILL_ai-detection | Polished text |

### Pipeline 5: Figure / Visualization

See **`30_system/behavior_rules/23_figure_visualization_pipeline.md`** for the full PaperBanana-style pipeline (Retrieve → Plan → Render → Refine) for publication figures and diagrams. Subagents: STATISTICS or CODE_IMPL; skill: SKILL_figure-pipeline.

### Pipeline 6: Full Research Lifecycle (GAP-ID → METHODOLOGY → STATISTICS → WRITING → QA)

End-to-end pipeline from gap identification through manuscript quality assurance. Designed for Q1 journal submissions and comprehensive research workflows.

| Stage    | Subagent     | Optional skill(s) | Output |
|----------|-------------|-------------------|--------|
| RETRIEVE | (30_system/context)   | —                 | Protocol/data/literature in scope; study type identified |
| GAP-ID   | WRITING     | SKILL_literature-synthesis | Analysis grid, consensus meter, gap statement, boolean search documentation |
| DESIGN   | METHODOLOGY | Per study type (CONSORT/PRISMA/STROBE) | PICO, study design, SAP |
| ANALYZE  | STATISTICS  | Per design (e.g. SKILL_meta-analysis, SKILL_test-selection) | Tables, figures, numerical results |
| VALIDATE | STATISTICS  | SKILL_swiss-cheese (if critical) | Validation pass; 9/10 self-assessment |
| WRITE    | WRITING     | SKILL_manuscript-writing, SKILL_manuscript-structure, SKILL_avoid-ai-formulations | Full manuscript (IMRaD; inverted triangle introduction) |
| QA       | OUTPUT_CTRL + WRITING | SKILL_output-controller, SKILL_ai-detection, reporting checklist | Zero-tolerance gate, batch AI-detection (1500-10000 word batches), plagiarism check, reporting checklist compliance, Swiss Cheese validation |

Handoffs: GAP-ID → DESIGN with gap statement and literature context; DESIGN → ANALYZE with SAP; ANALYZE → WRITE with validated results; WRITE → QA with full draft.

**Systematic review variant:** Skip ANALYZE stage if no quantitative synthesis; GAP-ID produces the PRISMA flow and extraction; WRITE covers narrative synthesis. For quantitative systematic reviews, use Pipeline 3 (Meta-analysis) within the ANALYZE stage.

### Pipeline 7: Discovery (7A MVP / 7B Full)

Discovery covers research-direction finding, gap identification, and (7B) full drug/therapeutic discovery.
**Stage definitions and step tables** live only in **`30_system/behavior_rules/24_discovery_pipeline.md`** (7A) and
**`30_system/behavior_rules/26_discovery_superpipeline.md`** + **`30_system/behavior_rules/25_capability_registry.md`** (7B). This file
defines REFINE expectations and skill routing; do not duplicate Discovery stage lists here.

**References:** `30_system/behavior_rules/24_discovery_pipeline.md` (7A), `30_system/behavior_rules/26_discovery_superpipeline.md`, `30_system/behavior_rules/25_capability_registry.md` (7B).

### Pipeline 8: Agentic engineering (PRD + Ralph)

| Stage | Subagent | Skills in order | Output |
|-------|----------|-----------------|--------|
| ALIGN | CODE_IMPL | SKILL_grill-me | Shared scope |
| SPEC | CODE_IMPL | SKILL_write-prd | `30_system/docs/prd.json` with `passes` |
| PLAN | CODE_IMPL | SKILL_prd-to-issues | Vertical slices / blockers |
| EXECUTE | CODE_IMPL | SKILL_ralph-loop (user: **Ralph ON**) | TDD iterations, `progress.txt` |

Full guide: `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`, `.cursor/rules/agentic_engineering_workflow.mdc`. Execution discipline: optional **SKILL_agentic-react-os**.

### Pipeline 9: Scholarly spec + iteration loop

| Stage | Subagent | Skills in order | Output |
|-------|----------|-----------------|--------|
| ALIGN | WRITING / METHODOLOGY / STATISTICS | SKILL_research-grill-me | Aligned PICO/design |
| SPEC | Same | SKILL_write-research-spec | `research-spec.json` with `passes` |
| PLAN | Same | SKILL_research-spec-to-milestones | Ordered milestones |
| EXECUTE | Per milestone | SKILL_scholarly-iteration-loop (user: **LOOP ON**) | `scholarly-progress.txt`, Swiss Cheese when required |

Full guide: `30_system/docs/SCHOLARLY_WORKFLOW.md`, `.cursor/rules/scholarly_workflow.mdc`. Not software PRD/Ralph.

### Ad hoc: Blog / newsletter (non-journal)

| Stage | Subagent | Skills | Output |
|-------|----------|--------|--------|
| DRAFT | WRITING | SKILL_nonacademic-writer | Outline, hooks, section drafts |
| POLISH | WRITING | Optional: avoid-ai-formulations or ai-detection (Tier 3 pairing) | Publishable prose |

See also Pipeline 1 table in `.cursor/rules/skills-auto-detect.mdc`.

---

## Skill Sequencing Within Pipelines

- **Single-task:** One skill per match (unchanged; see `skills-auto-detect.mdc`).
- **Pipeline:** For a named pipeline, the Orchestrator may load **multiple skills in order** for the same subagent (e.g. STATISTICS: meta-analysis → forest-plot → publication-bias). The pipeline table defines the order; the subagent executes steps accordingly.
- **Overlap:** If both a pipeline and a single skill match, prefer the pipeline when the user intent is "full workflow" (e.g. "run meta-analysis" → Pipeline 3); otherwise single skill.

---

## Refine Phase and Optional Critic Role

### Refine Phase (mandatory in existing rules)

- **When:** Already required by core principles for critical analyses (primary outcome, meta-analysis pooled estimate, etc.), end of analysis (before Methods/Results text), and pre-publication. See `30_system/behavior_rules/05_verification.md`, Swiss Cheese.
- **Who:** Usually the **same** subagent that produced the output (STATISTICS: self-assessment + Swiss Cheese; WRITING: `write_with_ai_check` / SKILL_ai-detection).
- **What:** Self-assessment ≥9/10, Swiss Cheese when applicable, AI score below target for prose.

### Optional Debate REFINE (Geometry / critical outputs)

For pipeline 6, 7, or user `@pipeline refine-debate`:

| Pass | Subagent | Role |
|------|----------|------|
| 1 | Primary (STATISTICS/WRITING/CODE) | Produce output |
| 2 | CODE_QA or METHODOLOGY as **Investigator** | Verify claims, list gaps |
| 3 | Same or WRITING as **Contrarian** | Challenge strongest assumptions |
| 4 | Primary | Apply fixes; Swiss Cheese if mandatory |

Keep each debate pass under one short paragraph; do not spawn unbounded subagent chains.

### Optional Critic / Refinement Subagent

- **Idea (from PaperBanana):** A dedicated agent evaluates and suggests improvements after the primary agent.
- **Our option:** A **Refinement** pass that can be:
  - **Implicit:** Done by the same subagent (Refine phase above).
  - **Explicit (optional):** A **Critic**-style pass: second subagent (e.g. CODE_QA for code, WRITING or RULES_MAINT for consistency) reviews the output and returns short, actionable feedback; primary subagent (or user) applies it.
- **Implementation:** No new "Critic" subagent is required initially. For high-stakes outputs the Orchestrator may add a **REFINE** stage and assign it to the most relevant existing subagent (STATISTICS for analysis, WRITING for manuscript, CODE_QA for code). If a dedicated "Output Critic" role is added later, it would slot into the REFINE stage.

---

## Orchestrator Behaviour (Summary)

1. **Classify** task (including MIXED / pipeline intent).
2. **If** user intent matches a **named pipeline** (e.g. "analysis then writing", "setup and validate project", "full meta-analysis", "all figures for study"):
   - Select the pipeline and run **stages in order**.
   - For each stage: select subagent (+ skills from pipeline table), execute, then hand off to next stage (with handoff format as in `00_orchestrator_agent.mdc`).
3. **If** single-domain but **multi-skill** (e.g. "meta-analysis with forest plot and funnel plot"):
   - Load skills in the **recommended order** for that domain (see pipeline tables or skill-sequencing in `skills-auto-detect.mdc`).
4. **REFINE:** For critical outputs, ensure a Refine phase is run by the appropriate subagent (existing rules and `30_system/behavior_rules/05_verification.md`).

---

## References

- `.cursor/rules/00_orchestrator_agent.mdc` – classification, handoff, MIXED
- `.cursor/rules/skills-auto-detect.mdc` – task → skill mapping, pipeline skill sequence
- `30_system/behavior_rules/05_verification.md` – Swiss Cheese, when mandatory
- `30_system/behavior_rules/09_workflow_optimization.md` – workflow steps (align pipelines with Workflow 2, 3, 7)
- `30_system/behavior_rules/15_agent_roles.md`, `30_system/behavior_rules/15b_agent_subagent_system.md` – subagents and handoff
- `30_system/behavior_rules/23_figure_visualization_pipeline.md` – Pipeline 5 (Figure/Visualization)

---

**Status:** Active. Orchestrator and skills-auto-detect reference this document and the pipeline/skill-order tables above. Pipelines 1–6 defined.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [[Scholarly skill loop]]
- [[Orchestrator - agent roles]]
- [behavior rules INDEX](../docs/indexes/behavior_rules_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[23_figure_visualization_pipeline]]
- [[SKILL_eda-flexplot]]
- [[24_discovery_pipeline]]
- [[15b_agent_subagent_system]]
- [[README]]
