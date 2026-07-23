# R package catalog by domain (on-demand install)

Install core tiers via `source("40_operations/scripts/utils/install_packages.R")`. Add domain packages only when needed.

## Core tidy + tables

`tidyverse`, `here`, `gtsummary`, `modelsummary`, `flextable`, `gt`

## Modeling

| Domain | Packages |
|--------|----------|
| GLMM | `glmmTMB`, `lme4`, `emmeans`, `marginaleffects` |
| Survival | `survival`, `survminer`, `flexsurv`, `survRM2` |
| Causal / PS | `MatchIt`, `WeightIt`, `cobalt` |
| MI | `mice` |
| Bayes | `brms`, `cmdstanr` (see `bayesian-workflow`) |
| Meta-analysis | `meta`, `metafor`, `dmetar` |

## Diagnostics and viz

`performance`, `see`, `ggstatsplot`, `patchwork`

## ML (exploratory unless prespecified)

`tidymodels`, `mlr3`, `rms`

## Notes

- Packages &lt;1 year on CRAN: label exploratory until methods literature supports use.
- Prefer `glmmTMB` over `lme4` for new code with complex random structures.
- Prefer `marginaleffects` for new marginal effects code.

**Test choice only:** load `SKILL_test-selection` + `reference/kdense/*`, not this full catalog.

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
- [[r_statistics_coding]]
