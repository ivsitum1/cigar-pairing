# Bayesian Workflow – Code Templates

**Used by:** `SKILL_bayesian-workflow.md`
**Source:** Extracted from skill to enable progressive loading. Load only when executing the corresponding step.

---

## Prior Specification

```r
library(brms)

priors <- c(
    prior(normal(0, 2.5), class = "b"),
    prior(student_t(3, 0, 10), class = "Intercept"),
    prior(exponential(1), class = "sigma")
)
```

## Prior Predictive Check

```r
prior_only <- brm(
    y ~ x1 + x2,
    data = df,
    prior = priors,
    sample_prior = "only",
    chains = 4,
    iter = 2000
)
pp_check(prior_only, type = "hist", ndraws = 100)
```

## Model Fitting

```r
fit <- brm(
    y ~ x1 + x2 + (1 | group),
    data = df,
    prior = priors,
    family = gaussian(),
    chains = 4,
    iter = 4000,
    warmup = 2000,
    cores = 4,
    seed = 123,
    control = list(adapt_delta = 0.95)
)
```

## Convergence Diagnostics

```r
summary(fit)  # ALL Rhat < 1.01, ALL ESS > 400

library(bayesplot)
mcmc_trace(fit)
mcmc_rank_overlay(fit)

divergent <- sum(subset(nuts_params(fit), Parameter == "divergent__")$Value)
if (divergent > 0) {
    warning(paste(divergent, "divergent transitions - increase adapt_delta"))
}
```

## Posterior Predictive Check

```r
pp_check(fit, type = "dens_overlay", ndraws = 100)
pp_check(fit, type = "stat", stat = "mean")
pp_check(fit, type = "stat", stat = "sd")
pp_check(fit, type = "stat_grouped", group = "group_var", stat = "mean")
```

## Model Comparison (LOO-CV)

```r
library(loo)
fit1 <- add_criterion(fit1, "loo")
fit2 <- add_criterion(fit2, "loo")
comp <- loo_compare(fit1, fit2)
print(comp)
# |elpd_diff| > 4*SE = meaningful difference
```

## Sensitivity Analysis

```r
priors_skeptical <- c(
    prior(normal(0, 1), class = "b"),
    prior(student_t(3, 0, 10), class = "Intercept"),
    prior(exponential(1), class = "sigma")
)

fit_sens <- brm(y ~ x1 + x2, data = df, prior = priors_skeptical, ...)

library(tidybayes)
compare <- bind_rows(
    spread_draws(fit, b_x1) %>% mutate(prior = "default"),
    spread_draws(fit_sens, b_x1) %>% mutate(prior = "skeptical")
)
ggplot(compare, aes(x = b_x1, fill = prior)) +
    geom_density(alpha = 0.5)
```

## Reporting

```r
fixef(fit)

library(bayestestR)
p_direction(fit)
hypothesis(fit, "x1 > 0")
```

## Reporting Template

| Parameter | Prior | Justification |
|---|---|---|
| beta_treatment | Normal(0, 2.5) | [why appropriate] |
| sigma | Exponential(1) | [why appropriate] |

### Results Table

| Parameter | Posterior Mean | 95% CI | P(Direction) |
|---|---|---|---|
| beta_treatment | X.XX | [X.XX, X.XX] | XX% |

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)

## Parent skills (auto)

- [[SKILL_bayesian-workflow]]

## Related playbooks (auto)

- [[ai_detection_patterns]]
- [[ai_phrase_replacements]]
- [[consort_checklist_items]]
- [[literature_synthesis_templates]]
- [[meta_analysis_code_templates]]
- [[OBSIDIAN_AGENT_PLAYBOOK]]
- [[r_statistics_coding]]
- [[r_statistics_packages]]
