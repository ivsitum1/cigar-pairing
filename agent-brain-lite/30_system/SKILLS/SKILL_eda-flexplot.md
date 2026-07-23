---
name: eda-flexplot
description: Use for EDA then visual EDA via flexplot script; mandatory pause to present results and suggest options; then user picks next skill (test-selection, meta-analysis, etc.). Do NOT run inferential analysis in same turn. Triggers include: exploratory analysis, EDA, explorativna analiza, flexplot, visual EDA, vizualna eksplorativna analiza.
version: 1.1
last_updated: 2026-03-30
domain: statistics
tokens: ~900
triggers:
  - exploratory analysis
  - EDA
  - explorativna analiza
  - flexplot
  - visual EDA
  - vizualna eksplorativna analiza
  - explore variables
  - explore data before analysis
requires_packages: [flexplot, tidyverse]
reference_files: [40_operations/R/exploratory/eda_flexplot.R]
pipeline_position: [0]
---

# Skill: Exploratory Analysis with FlexPlot Visual EDA

## When to use

Use this skill when:
- Starting analysis from raw or prepared data and exploratory step is needed
- User asks for exploratory analysis, EDA, or "explore variables"
- Before choosing inferential method: visual EDA informs test/model choice
- Pipeline: first statistics step before test-selection, meta-analysis, or other analysis skills

**Python/tabular EDA (optional):** If the user supplies only CSV/Excel and asks for profiling without R flexplot, see `reference/scientific_thinking/` and staging `scientific-thinking/exploratory-data-analysis` under `90_archive/imports/`; default path for this workspace remains **R flexplot** + pause.

## Prerequisites

- Data file available (path known or in project convention, e.g. `data/analysis_dataset.csv`)
- R environment with `flexplot` and `tidyverse` (and optionally `naniar` for missingness)

## Step-by-step procedure

### 0. Dataset codebook (if patient-level data)

- If `01_input/codebook/dataset_codebook.md` exists, read it before loading data.
- After load, compare `names(df)` to codebook `variable_name` rows; report mismatches and do not rename columns without updating the codebook.

### 1. Exploratory analysis (numeric + structure)

- Load data with `set.seed()` and tidyverse; use `here::here()` for paths.
- Run structure review: `str()`, `glimpse()`, `summary()`.
- Identify variable types (numeric, factor, ordered) and obvious inconsistencies.
- Compute descriptive statistics:
  - Numeric: mean, SD, median, IQR (report mean ± SD and/or median [IQR]).
  - Categorical: n (%).
- Optionally assess missing data (e.g. `naniar::vis_miss()`); report % missing per variable if relevant.

### 2. Visual exploratory analysis via FlexPlot script

- Run the visual EDA using the project script: **`40_operations/R/exploratory/eda_flexplot.R`**.
- Script must:
  - Plot distributions: `flexplot(variable ~ 1, data = df, method = "histogram")` (or density) for key variables.
  - Plot relationships: `flexplot(outcome ~ predictor, data = df)` for outcome–predictor pairs of interest.
  - Optionally add covariates: `flexplot(y ~ x + z, data = df)`.
  - Save figures to a standard output folder (e.g. `03_output/figures/eda/` or `02_analysis/figures/eda/`) so they can be referenced.
- Adapt script arguments/paths to the current dataset and outcome/predictor names; do not run generic code on wrong variables.

### 3. Present results and suggest next steps

- **Present:** Summarise what the descriptives and flexplot figures show (distributions, skewness, potential outliers, relationship shape, possible interactions).
- **Suggest options:** List concrete next-step options, for example:
  - **Group comparison** → SKILL_test-selection (Welch, permutation, nonparametric as per hierarchy).
  - **Meta-analysis** → SKILL_meta-analysis (then forest-plot, publication-bias as needed).
  - **Bayesian analysis** → SKILL_bayesian-workflow.
  - **Regression / multivariable model** → suggest linear/logistic/Cox per outcome type and refer to SAP or protocol.
  - **Sensitivity / robustness** → SKILL_sensitivity-analysis (if meta-analysis already planned).
  - **Target trial / causal** → SKILL_target-trial-emulation (if design matches).
- Do **not** start any inferential analysis or run another analysis skill in the same turn.

### 4. MANDATORY PAUSE

- **Stop after step 3.** Do not run test-selection, meta-analysis, regression, or any other inferential skill until the user specifies which direction they want (e.g. "nastavi s test-selection", "koristi meta-analysis", "Welch t-test", "Bayesian").
- Confirm: "Daljnja analiza čeka tvoj odabir. Reci koji smjer želiš (npr. test-selection, meta-analysis, bayesian-workflow, regresija)."

### 5. After user specifies method

- Load and apply the chosen skill (e.g. SKILL_test-selection, SKILL_meta-analysis, SKILL_bayesian-workflow) per its steps.
- Use the EDA and flexplot results to justify choices (e.g. Welch vs nonparametric, link function, need for sensitivity analyses).

## Integration with other skills

| User chooses | Skill to load next |
|---------------|---------------------|
| Test za grupe, usporedba grupa, Welch, nonparametrijski | SKILL_test-selection |
| Meta-analiza, pooled estimate, forest plot | SKILL_meta-analysis |
| Bayesian, prior, posterior, brms | SKILL_bayesian-workflow |
| Publication bias, funnel | SKILL_publication-bias (after meta-analysis) |
| Sensitivity, leave-one-out, robustness | SKILL_sensitivity-analysis |
| Target trial, emulation | SKILL_target-trial-emulation |

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Eksplorativno prikaži odnos doze i ishoda prije inferencije."  
**Output:** "Flexplot/EDA output `[VERIFIED]` ako se skripta izvrši; inferenciju ne radim u istom koraku; sljedeći skill predložim `[INFERRED]` (npr. test-selection)."

## Verification

- [ ] Data loaded and structure reviewed
- [ ] Descriptives reported (mean ± SD and/or median [IQR]; n (%) for categorical)
- [ ] Flexplot script run and figures saved; results summarised
- [ ] Options for further analysis presented; no inferential analysis run
- [ ] Pause observed until user specifies method
- [ ] After user choice: correct skill loaded and applied

## Handoff to test-selection

When the user picks group comparisons or regression, load **test-selection** next. Assumption checks and test choice follow `reference/kdense/assumptions_and_diagnostics.md` and `test_selection_guide.md` (do not run inferential tests in the EDA turn).

## Related rules

- `30_system/behavior_rules/02_statistics.md` (§ 1–2: data load, EDA, FlexPlot)
- `30_system/behavior_rules/11_r_programming.md` (Step 2: FlexPlot-first)
- `.cursor/rules/statistics-test-selection.mdc` (Step 1: EDA before test selection)

## Learning integration

- **task_type:** exploratory_analysis
- **log_fields:** data_path, n_vars, key_findings, suggested_skills
- **post_step:** After presenting options, output brief LEARNING_BLOCK if useful for project memory.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
