# Bayesian statistics (reference)

**Variance priors:** Never flat/uniform on variance; use half-Cauchy(0, 1) or exponential(1) on SD/sigma (`99_error_memory.mdc`).

## When to prefer Bayes

- Small samples with informative priors justified a priori.
- Complex hierarchical structures (brms).
- Direct probability statements on hypotheses or effect thresholds.

## Workflow pointer

Full procedure: `SKILL_bayesian-workflow` + `reference/bayesian_code_templates.md`.

## Bayes factors (exploratory unless pre-specified)

Use when comparing models; report BF with interpretation scale; label exploratory if not in SAP.

## Reporting

- Posterior median/mean and 95% credible intervals.
- Probability of effect &gt; clinically relevant threshold when prespecified.
- Prior sensitivity if priors are informative.
- PPC and LOO/WAIC per workflow skill.

## Disambiguation

Frequentist test selection only → `test-selection`. Python GLM tables → `statsmodels-python`.

## Parent skills (auto)

- [[SKILL_bayesian-workflow]]

## Related playbooks (auto)

- [[results_reporting_snippets]]
- [[test_selection_guide]]
- [[assumptions_and_diagnostics]]
- [[effect_sizes_and_power]]
- [[reporting_standards]]
