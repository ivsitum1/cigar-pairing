# Test selection quick reference (K-Dense adapted)

**Workspace default:** Welch t-test for two independent groups with continuous outcomes (not Student t-test). See `99_error_memory.mdc`.

## Comparing two groups

| Design | Outcome | Distribution | Test |
|--------|---------|--------------|------|
| Independent | Continuous | Normal, equal variance | Independent t-test (rare; verify Levene) |
| Independent | Continuous | Normal, unequal variance | **Welch t-test** |
| Independent | Continuous | Non-normal | Mann-Whitney U |
| Paired | Continuous | Normal differences | Paired t-test |
| Paired | Continuous | Non-normal differences | Wilcoxon signed-rank |
| Independent | Binary / categorical | — | Chi-square or Fisher exact (sparse cells) |

## Comparing three or more groups

| Design | Outcome | Test | Follow-up |
|--------|---------|------|-----------|
| Independent | Continuous, normal | One-way ANOVA | Prespecified post-hoc (Tukey, Holm) |
| Independent | Continuous, non-normal | Kruskal-Wallis | Dunn or pairwise with correction |
| Repeated measures | Continuous, normal | Repeated-measures ANOVA | Sphericity check |
| Repeated measures | Continuous, non-normal | Friedman | Pairwise with correction |

## Relationships and prediction

| Question | Test / model |
|----------|----------------|
| Two continuous variables | Pearson (normal) or Spearman |
| Continuous outcome, predictors | Linear regression (check linearity, residuals) |
| Binary outcome | Logistic regression |
| Count outcome | Poisson/negative binomial; check overdispersion |
| Time-to-event | Cox PH (check `cox.zph`); alternatives if violated |

## Before locking a test

1. Confirm primary vs secondary / exploratory.
2. Run assumption checks (normality, variance, independence).
3. Pre-specify one-tailed vs two-tailed.
4. Plan effect size and CI reporting, not p alone.
5. Multiple comparisons: Holm (confirmatory) or FDR (exploratory), labeled.

**Implementation:** R code → `SKILL_r-statistics`; Python statsmodels → `SKILL_statsmodels-python`.

## Parent skills (auto)

- [[SKILL_test-selection]]

## Related playbooks (auto)

- [[bayesian_statistics]]
- [[results_reporting_snippets]]
- [[assumptions_and_diagnostics]]
- [[effect_sizes_and_power]]
- [[reporting_standards]]
