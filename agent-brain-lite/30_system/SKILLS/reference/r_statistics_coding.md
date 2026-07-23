# R statistics coding standards (repo)

## Reproducibility

```r
source("40_operations/R/shared/reproducibility.R")
init_analysis(seed = 2024, project_name = "label")
```

- `here::here()` for paths; never `setwd()`
- `set.seed()` before stochastic steps
- `TRUE`/`FALSE`, not `T`/`F`
- `dplyr::filter()`, not `subset()` or `df[df$x,]`
- `package::function()` inside functions

## Workflow order

1. Descriptive / EDA (`eda-flexplot` if not done)
2. Assumptions (`check_assumptions.R`)
3. Primary model (per `test-selection` / SAP)
4. Sensitivity analyses
5. `sessionInfo()` to log

## Reporting

- Effect size + 95% CI for primary
- Welch default for two-group continuous comparisons
- Cox: report PH test

## Full protocol

`30_system/behavior_rules/11_r_programming.md`, `.cursor/rules/python_r_code_always.mdc` (R globs).

## Parent skills (auto)

- [[SKILL_r-statistics]]

## Related playbooks (auto)

- [[ai_detection_patterns]]
- [[ai_phrase_replacements]]
- [[bayesian_code_templates]]
- [[consort_checklist_items]]
- [[literature_synthesis_templates]]
- [[meta_analysis_code_templates]]
- [[OBSIDIAN_AGENT_PLAYBOOK]]
- [[r_statistics_packages]]
