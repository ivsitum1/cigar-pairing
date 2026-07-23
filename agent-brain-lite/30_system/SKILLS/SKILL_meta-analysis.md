---
name: meta-analysis
description: Conducts full systematic review and meta-analysis workflow from protocol/search through pooled estimates, heterogeneity, sensitivity checks, and reporting. Use when users request systematic review, pooled analysis, or quantitative synthesis across studies.
version: 1.4
last_updated: 2026-07-01
domain: statistics
tokens: ~1950
triggers:
  - meta-analysis
  - meta analiza
  - systematic review
  - sustavni pregled
  - systematic review and meta-analysis
  - combine studies
  - pooled estimate
  - systematic review quantitative
requires_packages: [meta, metafor, dmetar]
reference_files:
  - reference/meta_analysis_code_templates.md
  - reference/meta_analysis_pdf_trace.md
  - reference/scientific_thinking/literature_review_phases.md
  - reference/scientific_thinking/database_strategies.md
  - reference/scientific_thinking/pubmed/search_syntax.md
  - reference/medical_research/reference-integrity-checker/hard-rules.md
pipeline_position: [3]
---

# Skill: Systematic Review and Meta-Analysis

## When to use

Use this skill when:
- User requests systematic review and/or meta-analysis
- Full workflow: from protocol and search to pooled estimate and reporting
- Quantitative synthesis of multiple studies (with or without prior SR steps)

**Skill boundaries (no overlap):**
- **This skill (meta-analysis):** Full systematic review and/or meta-analysis *workflow* (protocol → search → screening → extraction → RoB → pooling → forest plot → publication bias). Use when the user wants to *do* an SR or MA.
- **SKILL_prisma-checklist:** Only *checking* an existing SR/MA manuscript against PRISMA 2020. Use when the manuscript is written and you need a compliance check.
- **SKILL_literature-synthesis:** Narrative synthesis, analysis grid, consensus meter, gap identification *without* mandatory quantitative pooling. Use for literature reviews that are not full systematic reviews; if the project is itself an SR/MA, use this skill only for narrative parts and follow meta-analysis + PRISMA for the rest.
- **SKILL_forest-plot / SKILL_publication-bias:** Single task (one forest plot, or publication bias only) when meta-analysis is already done. For full pipeline use this skill.

## Prerequisites

- Clear question (PICO/PECO) and protocol or analysis plan
- For meta-analysis: prepared data (effect sizes, SE, or raw counts/means)
- R packages: `meta`, `metafor`, `dmetar`

## Honesty and grounding checkpoints

- Mark key outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only for values confirmed from model output or executed code.
- If protocol elements are missing (population, outcomes, comparators), return `[BLANK]` for blocked steps and request missing inputs.
- Do not report pooled estimates, I2, tau2, prediction intervals, or bias-test results unless computed in-session or extracted from provided outputs.

---

## Part I: Systematic review (before meta-analysis)

When the task includes the full systematic review lifecycle, complete these steps before quantitative synthesis.

### 1. Protocol and registration

- Define PICO/PECO (population, intervention/exposure, comparison, outcome).
- Pre-specify: inclusion/exclusion, primary/secondary outcomes, subgroup/sensitivity plans, risk-of-bias tool.
- Register protocol (PROSPERO or equivalent) and note registration number.

### 2. Search

- Define sources (databases, registers, grey literature, hand search).
- Build and document search strategy (full strategy in supplement; PRISMA Item 7).
- Record dates of last search per source (Item 6).
- Export and deduplicate records.
- **Reproducible log:** record database, query string, filters, and hit counts per run. Use **PubMed MCP** when configured; else `reference/scientific_thinking/pubmed/` (E-utilities patterns, no embedded API keys). For trial registry gaps, see `scientific-thinking-index/SKILL_MAP.yaml` → clinicaltrials-database (staging scripts under `90_archive/imports/`). Load `literature_review_phases.md` for full SR phase checklist.

### 3. Screening and selection

- Two-stage screening (title/abstract, then full text) with predefined criteria.
- Document: number of records identified, screened, excluded (with reasons), full texts assessed, included (PRISMA flow diagram – Item 16).
- Use PRISMA 2020 flow diagram template; reconcile all numbers.

### 4. Data extraction

- **PDF trace (mandatory for PDF-sourced claims):** Follow `reference/meta_analysis_pdf_trace.md` end-to-end:
  1. Register PDFs under `01_input/literature/`
  2. `read_pdf` twin → `search_pdf` / `pdf_evidence` for tables and figures
  3. Append each extract to `02_analysis/extraction/pdf_trace.jsonl` with pages and tool
  4. Agent-proposed values stay `[INFERRED]` until human verifies in codebook
  5. Do not pool from PDF prose without a structured extraction row (OKF-4 / US-38)
- **Before extraction:** Pilot and version `01_input/data_extraction/codebook.md` (brain template: `40_operations/templates/codebooks/extraction_codebook.md`). Extraction sheet column names must match `variable_name` in the codebook.
- Extract on a piloted form: study ID, design, population, intervention/comparison, outcome definitions, effect data (for MA), funding, conflicts.
- At least two extractors; resolve disagreements (predefined process).
- List and define all variables (Item 10); bump codebook `version` in YAML front matter when fields change.

### 5. Risk of bias (RoB)

- Choose tool by design (e.g. RoB 2 for RCTs, ROBINS-I for non-randomised).
- Describe who assessed and how (Item 11).
- Present RoB per study and per domain (Item 18); use for interpretation and optional subgroup/sensitivity.

### 6. Handoff to meta-analysis

- Prepare analysis dataset: one row per study (or per outcome/contrast if multiple per study).
- Variables: study label, effect measure (OR/RR/MD/SMD), SE or variance, sample sizes; subgroup/covariates if pre-specified.

---

## Part II: Meta-analysis (quantitative synthesis)

When data are ready (from Part I or provided), follow these steps.

### 1. Data preparation

- Load data (CSV, Excel, or R data frame); use `here::here()` for paths.
- Compute effect sizes if needed (OR, RR, RD, MD, SMD) and SE/variance.
- Document transformations; handle missing data transparently.

### 2. Exploratory analysis

- Descriptives per study; draft forest plot; check for obvious outliers.
- If no prior EDA: consider SKILL_eda-flexplot for key variables; then return here.

### 3. Primary meta-analysis

- Choose model: random effects (default), common effect for sensitivity.
- Estimate between-study variance (e.g. REML); report method.
- Example (continuous outcome):
  ```r
  library(meta)
  ma <- metacont(n.e, mean.e, sd.e, n.c, mean.c, sd.c,
                 data = data, method.tau = "REML")
  ma_common <- update(ma, comb.fixed = TRUE, comb.random = FALSE)
  ```
- Binary: `metabin(event.e, n.e, event.c, n.c, data = data, sm = "OR", method.tau = "REML")`.
- See `reference/meta_analysis_code_templates.md` for other effect types.

### 4. Heterogeneity

- Report I² (interpret: 0–40% low, 30–60% moderate, 50–90% substantial, 75–100% considerable), τ², Q and p-value.
- If I² > 50%, compute and report prediction interval.

### 5. Forest plot

- Publication-ready forest plot (random and, if relevant, common effect).
- Include prediction interval when appropriate.
- Export ≥300 DPI; use SKILL_forest-plot if part of figure pipeline.

### 6. Sensitivity analyses

- Leave-one-out; influence diagnostics; method comparison (e.g. REML vs DL).
- Outlier removal only if pre-specified or clearly justified; report as sensitivity.

### 7. Publication bias (if k ≥ 10)

- Funnel plot; Egger-type test (Peters if binary); trim-and-fill if applicable.
- Use SKILL_publication-bias for full procedure.

### 8. Subgroup analysis (only if pre-specified)

- Typically k ≥ 10 and I² > 0%; report subgroup estimates, R², residual heterogeneity.

### 9. Report results

- Pooled estimate with 95% CI; heterogeneity (I², τ², Q); forest plot; sensitivity and publication bias; subgroup (if done).

---

## Part III: Reporting (PRISMA)

- When writing the manuscript, follow PRISMA 2020 (Items 1–27).
- Use `.cursor/rules/reporting-prisma.mdc` and SKILL_prisma-checklist for compliance.
- Include PRISMA flow diagram; reconcile all numbers in text and diagram.

---

## Verification

- [ ] SR: Protocol/registration; search; screening with flow; extraction; RoB (if full SR).
- [ ] MA: Data prepared; primary model; heterogeneity; forest plot; sensitivity; publication bias if k ≥ 10.
- [ ] Reporting: PRISMA checklist and flow diagram addressed.

## Examples

**Input:** "Imam 12 RCT studija i trebam random-effects meta-analizu za mortalitet."  
**Output:** "Pokrećem SR/MA workflow, računam pooled OR i heterogenost `[VERIFIED]` iz `metafor` outputa; PRISMA i RoB elementi koji nedostaju označeni su `[BLANK]` uz popis potrebnih podataka."

## Related rules

- `.cursor/rules/reporting-prisma.mdc`
- `30_system/behavior_rules/02_statistics.md`
- SKILL_prisma-checklist (reporting check)
- SKILL_forest-plot, SKILL_publication-bias, SKILL_sensitivity-analysis (downstream)

## Learning integration

- **task_type:** analysis
- **log_fields:** method (REML/DL), heterogeneity_handling, errors
- **post_step:** After completing procedure: output LEARNING_BLOCK if useful. If R script runs, suggest `log_analysis()` per project tools.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[literature_review_phases]]
- [[database_strategies]]
- [[search_syntax]]
- [[hard-rules]]
- [[meta_analysis_code_templates]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
