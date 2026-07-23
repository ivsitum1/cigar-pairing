# Assumption checking and diagnostics

## Normality

- n &lt; 50 per group: Shapiro-Wilk on residuals or per-group as design dictates.
- Larger n: Q-Q plots; do not over-rely on Shapiro-Wilk alone.
- Violation → non-parametric alternative or robust methods; document choice.

## Homogeneity of variance

- Levene test before t-tests and ANOVA.
- Unequal variances → Welch t-test or Welch ANOVA; not Student t-test.

## Independence

- Verify study design (clustering, repeated measures, matching).
- Clustered data → mixed models (`glmmTMB`, `lme4`), not naive t-test.

## Regression / GLM

- Linearity: scatter + residual vs fitted plots.
- Multicollinearity: VIF &lt; 5 (rule of thumb) for multiple predictors.
- Influential points: Cook's distance, DFBETAS where applicable.

## Cox / survival

- Proportional hazards: Schoenfeld residuals (`cox.zph` in R).
- Violation → stratified Cox, time-varying covariates, or prespecified alternative.

## Reporting when violated

State which assumption failed, which alternative was used, and whether analysis was primary or sensitivity.

## Parent skills (auto)

- [[SKILL_test-selection]]

## Related playbooks (auto)

- [[bayesian_statistics]]
- [[results_reporting_snippets]]
- [[test_selection_guide]]
- [[effect_sizes_and_power]]
- [[reporting_standards]]
