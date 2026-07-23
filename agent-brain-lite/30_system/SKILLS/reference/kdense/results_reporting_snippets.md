# Results reporting snippets

Use as phrasing templates; replace placeholders with verified numbers from analysis output.

## Continuous outcome, two groups

"The [outcome] was [higher/lower] in the [group A] than [group B] (mean ± SD or median [IQR]); Welch t-test t(df) = X.XX, p = .XXX, d = X.XX, 95% CI [low, high]."

## Survival

"Median [time metric] was X (95% CI …) in [group A] vs Y in [group B]. The hazard ratio was X.XX (95% CI …, p = …). Proportional hazards assumptions were [met/violated; method if adjusted]."

## Regression

"[Predictor] was associated with [outcome] (β = X.XX, 95% CI …, p = …) after adjusting for [covariates]. Model fit: [R² / AUC / C-index as appropriate]."

## Non-significant primary

"The estimated difference was directionally [description] but the 95% CI included [null/clinical threshold], consistent with [imprecision / no evidence against null], not proof of absence."

## Sensitivity

"In a prespecified sensitivity analysis [describe change], the estimate was … compared with … in the primary analysis."

Tag all numbers `[VERIFIED]` only after matching script output.

## Parent skills (auto)

- [[SKILL_manuscript-structure]]
- [[SKILL_test-selection]]

## Related playbooks (auto)

- [[bayesian_statistics]]
- [[test_selection_guide]]
- [[assumptions_and_diagnostics]]
- [[effect_sizes_and_power]]
- [[reporting_standards]]
