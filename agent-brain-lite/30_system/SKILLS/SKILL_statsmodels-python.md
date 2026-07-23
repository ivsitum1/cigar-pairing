---
name: statsmodels-python
description: Python statsmodels workflow for OLS, GLM, discrete models, and time series with diagnostics and inference tables. Use only when the user explicitly requests Python or statsmodels; for default clinical/R analysis use test-selection or bayesian-workflow.
version: 1.0
last_updated: 2026-05-16
domain: statistics
tokens: ~1200
triggers:
  - statsmodels
  - Python regression
  - OLS Python
  - ARIMA Python
  - Python inference
  - logistic regression Python
  - GLM Python
requires_packages: [statsmodels, pandas, numpy, scipy]
reference_files:
  - reference/kdense/statsmodels/linear_models.md
  - reference/kdense/statsmodels/glm.md
  - reference/kdense/statsmodels/discrete_choice.md
  - reference/kdense/statsmodels/time_series.md
  - reference/kdense/statsmodels/stats_diagnostics.md
pipeline_position: []
---

# Skill: Statsmodels (Python)

## When to use

Use when:
- User explicitly asks for **Python** or **statsmodels** implementation
- Econometrics-style coefficient tables, residual diagnostics, or ARIMA in Python are required

Do **not** use when:
- User is doing standard clinical/R manuscript work without mentioning Python (use `test-selection`, `bayesian-workflow`, or `eda-flexplot` instead)
- User only needs test *selection* guidance (use `test-selection`)

## Prerequisites

- Tabular data (CSV, parquet, or DataFrame path)
- Outcome and predictor types identified
- `statsmodels`, `pandas`, `numpy` available

## Honesty and grounding checkpoints

- Mark outputs `[VERIFIED]` only from executed code or user-supplied model output.
- Always add intercept via `sm.add_constant()` unless user model omits intercept by design.
- Report effect sizes and intervals where applicable; never p-value alone.
- For group comparisons, Welch or robust methods remain the workspace default in R; in Python, justify classical vs robust choices.

## Step-by-step procedure

1. **Confirm Python scope** with the user if ambiguous (one sentence).

2. **Load reference** for the model family:
   - Linear: `reference/kdense/statsmodels/linear_models.md`
   - GLM: `glm.md`
   - Binary/count: `discrete_choice.md`
   - Time series: `time_series.md`
   - Diagnostics: `stats_diagnostics.md`

3. **Prepare data:** handle missingness explicitly; document listwise deletion or imputation.

4. **Fit model:**
   - `import statsmodels.api as sm`
   - `X = sm.add_constant(X_data)`
   - OLS / GLM / Logit / ARIMA as appropriate
   - `print(results.summary())`

5. **Diagnostics (mandatory before interpretation):**
   - Residual plots; Breusch-Pagan or relevant test from `stats_diagnostics.md`
   - For time series: stationarity (ADF) before ARIMA order selection
   - Do not use sklearn as the primary inference engine for publication tables

6. **Report:**
   - Coefficients, SE, CI, and test statistics from `results`
   - For logistic: odds ratios `np.exp(params)` with CI
   - Manuscript text: Vancouver or journal style unless user requests APA

7. **Optional assumption script:** for raw assumption screening on columns, `python 40_operations/python/statistics/assumption_checks.py` (does not replace model-specific diagnostics).

## Verification

- [ ] `add_constant` used where intercept required
- [ ] Diagnostics run and reported
- [ ] Effect sizes or ORs with intervals included
- [ ] User did not need R workflow without being asked to switch stacks

## Related rules

- `30_system/behavior_rules/agents/04_medical_data_science/02_python_ecosystem.md`
- `.cursor/rules/python_r_code_always.mdc`

## Related Hubs

- [Skill registry](registry.json)
- [Statsmodels references](reference/kdense/statsmodels/)

## Skill reference graph (auto)

- [[linear_models]]
- [[glm]]
- [[discrete_choice]]
- [[time_series]]
- [[stats_diagnostics]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
