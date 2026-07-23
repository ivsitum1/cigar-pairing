---
name: r-statistics
description: >-
  End-to-end R biostatistics implementation for clinical and ICU research: package
  selection, reproducible scripts, modeling, survival, causal inference, and reporting.
  Use when writing or reviewing R analysis code, choosing CRAN packages, or running
  frequentist/Bayesian workflows outside dedicated meta-analysis or test-selection-only tasks.
version: 1.0
last_updated: 2026-05-16
domain: statistics
tokens: ~2100
triggers:
  - R statistics
  - R statistika
  - R analiza
  - biostatistics R
  - clinical statistics R
  - napiši R kod
  - R script analysis
  - glmmTMB
  - lme4
  - survival analysis R
  - gtsummary
  - ggstatsplot
  - MatchIt
  - mice imputation
  - tidymodels
  - mlr3
  - paketi za statistiku
requires_packages: []
reference_files:
  - reference/r_statistics_coding.md
  - reference/r_statistics_packages.md
pipeline_position: [1]
---

# Skill: R Clinical Statistics (implementation)

## When to use

- Implement, refactor, or review **R code** for statistical analysis in biomedical/ICU/RCT settings.
- Choose **which CRAN packages** fit the analysis domain (modeling, survival, causal, MA, ML, etc.).
- Apply repo **coding standards** and mandatory workflow order.

## When NOT to use (load specialized skill instead)

| User intent | Skill |
|-------------|--------|
| Only "which test?" / power / assumption narrative | `test-selection` |
| Full systematic review + pooling workflow | `meta-analysis` |
| Full brms prior → PPC → LOO workflow | `bayesian-workflow` |
| Flexplot EDA then pause for user choice | `eda-flexplot` |
| Python / statsmodels | `statsmodels-python` |
| Target trial emulation design | `target-trial-emulation` |
| End-of-analysis validation gate | `swiss-cheese` |

**Co-use:** This skill may follow `eda-flexplot` and precede `swiss-cheese` in Pipeline 1.

---

## Prerequisites

- Analysis-ready dataset path confirmed (`01_input/` or user path).
- Design, primary outcome, and analysis population defined (protocol/SAP or user statement). Mark gaps `[BLANK]`.
- R ≥ 4.1 recommended; project root via `here::here()`.

---

## Progressive disclosure (load on demand)

| Step needs | Load |
|------------|------|
| Writing or auditing R code | `reference/r_statistics_coding.md` |
| Package pick list by domain | `reference/r_statistics_packages.md` |
| Test choice hierarchy only | `SKILL_test-selection` (+ its `reference/kdense/*`) |

Do **not** load the full package catalog into context until the domain is known (one section at a time).

---

## Honesty and grounding

- Tag claims: `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, `[BLANK]`.
- Do not state assumptions passed without diagnostics cited.
- Packages on CRAN &lt;1 year: label **exploratory** until methodology peer-reviewed; cite primary paper before manuscript methods.
- Never substitute example drugs, doses, or cohort names from rules for the user's protocol.

---

## Procedure

### 0. Scope and install

1. Confirm stack is **R** (not Python).
2. Identify **domains** needed (e.g. GLMM + survival + Table 1 only).
3. From `reference/r_statistics_packages.md`, list packages for those domains only.
4. Ensure installed: `source("40_operations/scripts/utils/install_packages.R")` from repo root; add domain-specific `install.packages()` only for packages not in that script's tiers.
5. If `renv` active, snapshot after new installs.

### 1. Reproducibility and data

```r
source("40_operations/R/shared/reproducibility.R")
init_analysis(seed = 2024, project_name = "analysis_label")
# here::here("01_input/...") for data
```

Review structure (`glimpse`, types, plausibility checks). **Descriptive only** in this sub-step unless user asked for full pipeline in one pass.

### 2. EDA handoff (if not done)

If no EDA yet → **stop** and load `SKILL_eda-flexplot` (or run `40_operations/R/exploratory/eda_flexplot.R`). Present options; wait for user before primary inference unless `@autonomous` with explicit chain.

### 3. Missing data

- &lt;5% missing, MCAR plausible → complete case with explicit warning.
- ≥5% or MAR plausible → `mice` (document m, method, convergence); sensitivity complete-case.
- Bayesian joint imputation → delegate to `SKILL_bayesian-workflow` (`mi()` in brms).

### 4. Assumptions and test choice

- Run `check_assumptions()` from `40_operations/R/shared/check_assumptions.R` when comparing groups or fitting regression.
- Lock **primary** test/model via `SKILL_test-selection` rules (Welch default; PH for Cox; no stepwise).

### 5. Model family (quick map)

| Outcome | Default packages |
|---------|------------------|
| Continuous, clustered | `glmmTMB` or `lme4`; inference via `emmeans` or `marginaleffects` |
| Continuous, smooth time | `mgcv` |
| Binary / count | `glm` / `glmmTMB`; check overdispersion |
| Time-to-event | `survival` + `survminer`; PH check; consider `flexsurv`, `survRM2` if prespecified |
| Ordinal | `MASS::polr` or `brms` |
| Propensity / IPTW | `MatchIt`, `WeightIt`, `cobalt` |
| Prediction validation | `rms`, `tidymodels`, or `mlr3` per complexity |

Full alternatives and 2024–2026 packages: see package reference §2–17.

### 6. Fit, diagnose, report

- Primary estimate + **95% CI** + clinically interpretable effect measure.
- Diagnostics: residuals, influence (`performance::check_model` where appropriate); Cox → `cox.zph`.
- Multiple comparisons: Holm (confirmatory) or FDR (exploratory), labeled.
- Tables: `gtsummary` or `modelsummary`; export via `flextable` / `gt` as needed.
- Exploratory plots with tests: `ggstatsplot` (effect sizes in plot).

### 7. Sensitivity and validation

At minimum one sensitivity aligned with SAP (alternative outcome definition, alternative model, or complete-case vs MI). For prediction models: calibration + discrimination per `rms` or `tidymodels` yardstick.

### 8. Bayesian branch

If user requests Bayes or small-n stabilization → hand off to **`SKILL_bayesian-workflow`**; do not duplicate full prior/PPC checklist here.

### 9. Meta-analysis branch

If pooling across studies → **`SKILL_meta-analysis`**; single forest figure → `forest-plot`.

### 10. Figures and export

Publication theme: `40_operations/R/shared/theme_publication.R`. Save under `04_figures/` or `03_output/` with descriptive names (`forest_primary_outcome.pdf`).

### 11. Close

- Write `sessionInfo()` to analysis log.
- Before Methods/Results prose or submission → **`SKILL_swiss-cheese`** for primary/meta/survival/PS outcomes.

---

## Package defaults (repo install script)

`40_operations/scripts/utils/install_packages.R` installs **core + modeling + survival + causal-lite + viz** tiers. Extended catalog (100+ packages) is **on-demand** per domain in `reference/r_statistics_packages.md`; do not install entire catalog unless user requests full machine setup.

**GLMM default:** prefer `glmmTMB` over `lme4` for new code when zero-inflation, beta, or complex random structures matter; `lme4` remains acceptable for simple random intercepts.

**Post-model inference:** prefer `marginaleffects` for new code; `emmeans` when matching legacy scripts.

**Stan backend:** prefer `cmdstanr` + `brms` for new Bayesian projects; note `rstan` legacy where relevant.

---

## Output checklist

- [ ] Seed and paths documented
- [ ] Descriptive vs inferential clearly separated
- [ ] Primary analysis prespecified; sensitivities listed
- [ ] Effect sizes + CI for primary
- [ ] Assumptions/diagnostics cited
- [ ] Package versions noted (session info)
- [ ] No fabricated numbers or citations

---

## Related rules (Tier 1/2 when coding)

- `.cursor/rules/python_r_code_always.mdc` (globs `**/*.R`)
- `.cursor/rules/coding-standards-r.mdc` (detailed R standards)
- `.cursor/rules/statistics-test-selection.mdc` (test hierarchy)
- `30_system/behavior_rules/11_r_programming.md` (full protocol detail)

## Skill reference graph (auto)

- [[r_statistics_coding]]
- [[r_statistics_packages]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
