---
name: bayesian-workflow
description: Runs end-to-end Bayesian analysis with prior design, prior/posterior predictive checks, convergence diagnostics, model comparison, and reporting. Use when users ask about priors, posterior inference, brms, or Bayesian workflow decisions.
version: 1.2
last_updated: 2026-05-16
domain: statistics
tokens: ~3600
triggers:
  - Bayesian
  - prior
  - posterior
  - Bayes workflow
  - brms
requires_packages: [brms, bayesplot, loo, tidybayes, bayestestR]
reference_files:
  - reference/bayesian_code_templates.md
  - reference/kdense/bayesian_statistics.md
pipeline_position: []
---

# SKILL: Bayesian Analysis Workflow

## When to Use
- Need full uncertainty quantification
- Complex hierarchical/multilevel models
- Prior information available
- Small samples where priors stabilize estimation

## Honesty and grounding checkpoints

- Label critical claims as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Treat prior choices and convergence statements as `[VERIFIED]` only when backed by executed diagnostics.
- If package/version compatibility is unknown, return `[ASSUMPTION]` and verify via installed `brms`/Stan versions.
- Do not claim model adequacy without explicit posterior predictive checks and convergence evidence.

## K-Dense reference (progressive disclosure)

Load `reference/kdense/bayesian_statistics.md` for Bayes-factor and test-selection context. **Variance priors:** never use flat/uniform priors on variance; use half-Cauchy(0, 1) or exponential(1) on SD/sigma (see `99_error_memory.mdc`). Implementation templates remain in `reference/bayesian_code_templates.md` (R/brms).

## Step-by-Step Workflow

### Step 1: Specify Model and Priors
```r
library(brms)

# 1a. Write out likelihood
# Y ~ Normal(Î¼, Ïƒ)
# Î¼ = Î²â‚€ + Î²â‚Xâ‚ + Î²â‚‚Xâ‚‚

# 1b. Choose priors with justification
priors <- c(
    prior(normal(0, 2.5), class = "b"),           # Coefficients
    prior(student_t(3, 0, 10), class = "Intercept"), # Intercept
    prior(exponential(1), class = "sigma")        # Residual SD
)

# 1c. Document justification
# Î²: normal(0, 2.5) on standardized scale allows effects up to Â±5 SD
# Ïƒ: exponential(1) keeps SD positive, mode near 0 but allows larger
```

### Step 2: Prior Predictive Check
```r
# Simulate from priors ONLY (no data)
prior_only <- brm(
    y ~ x1 + x2,
    data = df,
    prior = priors,
    sample_prior = "only",  # Critical: no data used
    chains = 4,
    iter = 2000
)

# Check: are predictions plausible?
pp_check(prior_only, type = "hist", ndraws = 100)

# Questions to answer:
# - Are Y values in realistic range?
# - Is variance reasonable?
# - Do extreme values make sense?

# If NO: refine priors and repeat
```

### Step 3: Fit Model
```r
fit <- brm(
    y ~ x1 + x2 + (1 | group),  # Example with random intercept
    data = df,
    prior = priors,
    family = gaussian(),
    chains = 4,
    iter = 4000,
    warmup = 2000,
    cores = 4,
    seed = 123,
    control = list(adapt_delta = 0.95)  # Increase if divergences
)
```

### Step 4: Check Convergence
```r
# 4a. Summary check
summary(fit)
# ALL Rhat < 1.01
# ALL ESS > 400

# 4b. Visual diagnostics
library(bayesplot)
mcmc_trace(fit)       # Chains should mix
mcmc_rank_overlay(fit) # Ranks should be uniform

# 4c. Divergence check
divergent <- sum(subset(nuts_params(fit), Parameter == "divergent__")$Value)
if (divergent > 0) {
    warning(paste(divergent, "divergent transitions - increase adapt_delta"))
}

# STOP if convergence fails - results unreliable
```

### Step 5: Posterior Predictive Check
```r
# Does model capture data patterns?
pp_check(fit, type = "dens_overlay", ndraws = 100)
pp_check(fit, type = "stat", stat = "mean")
pp_check(fit, type = "stat", stat = "sd")
pp_check(fit, type = "stat_grouped", group = "group_var", stat = "mean")

# Questions:
# - Does observed data fall within predictions?
# - Are key summary stats reproduced?
# - Any systematic deviations?

# If poor fit: revise model specification
```

### Step 6: Model Comparison (if multiple models)
```r
library(loo)

# Add LOO criterion
fit1 <- add_criterion(fit1, "loo")
fit2 <- add_criterion(fit2, "loo")

# Compare
comp <- loo_compare(fit1, fit2)
print(comp)

# Interpretation:
# elpd_diff = expected predictive density difference
# SE = standard error of difference
# If |elpd_diff| > 4*SE: meaningful difference
# Negative diff = first model worse
```

### Step 7: Sensitivity Analysis
```r
# Fit with alternative priors
priors_skeptical <- c(
    prior(normal(0, 1), class = "b"),  # More skeptical
    prior(student_t(3, 0, 10), class = "Intercept"),
    prior(exponential(1), class = "sigma")
)

fit_sens <- brm(
    y ~ x1 + x2,
    data = df,
    prior = priors_skeptical,
    ...
)

# Compare posteriors
library(tidybayes)
compare <- bind_rows(
    spread_draws(fit, b_x1) %>% mutate(prior = "default"),
    spread_draws(fit_sens, b_x1) %>% mutate(prior = "skeptical")
)

ggplot(compare, aes(x = b_x1, fill = prior)) +
    geom_density(alpha = 0.5)

# If conclusions robust: proceed
# If not: report sensitivity and discuss
```

### Step 8: Summarize and Report
```r
# Point estimates with credible intervals
fixef(fit)

# Probability of direction
library(bayestestR)
p_direction(fit)

# Hypothesis testing (if needed)
hypothesis(fit, "x1 > 0")

# Generate report template
```

## Reporting Template
```markdown
## Bayesian Analysis

### Model Specification
- Likelihood: [distribution, link function]
- Fixed effects: [list with interpretation]
- Random effects: [if applicable]

### Prior Distributions
| Parameter | Prior | Justification |
|-----------|-------|---------------|
| Î²_treatment | Normal(0, 2.5) | [why appropriate] |
| Ïƒ | Exponential(1) | [why appropriate] |

### Prior Predictive Check
[Statement confirming priors produce plausible predictions]
[Figure showing prior predictive distribution]

### Convergence Diagnostics
- All R-hat < 1.01: âœ“
- Minimum Bulk ESS: [value]
- Minimum Tail ESS: [value]
- Divergent transitions: 0

### Posterior Predictive Check
[Figure comparing observed vs predicted]
[Statement on model adequacy]

### Results
| Parameter | Posterior Mean | 95% CI | P(Direction) |
|-----------|---------------|--------|--------------|
| Î²_treatment | X.XX | [X.XX, X.XX] | XX% |

### Sensitivity Analysis
[Comparison under alternative priors]
[Conclusion about robustness]

### Software
- R version: X.X.X
- brms version: X.X.X
- Stan version: X.X.X
```

## Learning integration

- **task_type:** analysis
- **log_fields:** package_used, prior_choice, convergence_status
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Examples

**Input:** "Treba mi Bayesian multilevel model za LOS u ICU-u s informativnim priorima."  
**Output:** "Definiram priore i opravdanje `[EXTRACTED]`, radim prior predictive check i convergence dijagnostiku `[VERIFIED]`; ako postoji divergence bez rezolucije, zaključak je `[BLANK]` dok se model ne stabilizira."

## Common Mistakes Checklist
- [ ] Skipping prior predictive check
- [ ] Using flat/improper priors without justification
- [ ] Ignoring convergence warnings
- [ ] Not checking for divergences
- [ ] Reporting only point estimates (ignoring uncertainty)
- [ ] Using DIC instead of LOO-CV
- [ ] No sensitivity analysis

## References
- Gelman et al. "Bayesian Workflow" (2020). arXiv:2011.01808
- BÃ¼rkner "brms Tutorial" (2017)

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[bayesian_code_templates]]
- [[bayesian_statistics]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
