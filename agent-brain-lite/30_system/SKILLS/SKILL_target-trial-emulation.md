---
name: target-trial-emulation
description: Use when emulating an RCT from observational data; NOT for actual RCTs or standard observational analysis Triggers include: target trial, emulation, causal inference design, comparative effectiveness.
version: 1.1
last_updated: 2026-03-30
domain: statistics
tokens: ~2400
triggers:
  - target trial
  - emulation
  - causal inference design
  - comparative effectiveness
requires_packages: [dagitty, ggdag, MatchIt, AIPW, cobalt, EValue, sensemakr]
reference_files: []
pipeline_position: []
---

# SKILL: Target Trial Emulation

## When to Use
- Causal inference from observational data
- Emulating RCT with existing databases
- Comparative effectiveness research

## Step-by-Step Workflow

### Step 1: Define Target Trial Protocol
```markdown
Write out the hypothetical trial you're trying to emulate:

1. ELIGIBILITY: Who would be enrolled?
   - [ ] Define inclusion criteria at time zero
   - [ ] Define exclusion criteria
   - [ ] Ensure all criteria measurable at baseline

2. TREATMENT: What interventions compared?
   - [ ] Define intervention arm precisely
   - [ ] Define control arm precisely
   - [ ] Specify any variations allowed

3. ASSIGNMENT: How allocated?
   - [ ] Identify what determines treatment in data
   - [ ] List potential confounders

4. TIME ZERO: When does follow-up start?
   - [ ] Eligibility, treatment, follow-up must align
   - [ ] Check for immortal time

5. OUTCOME: What measured?
   - [ ] Primary outcome definition
   - [ ] Measurement timing

6. ESTIMAND: What causal effect?
   - [ ] Intention-to-treat vs per-protocol
   - [ ] How handle intercurrent events
```

### Step 2: Draw DAG
```r
library(dagitty)
library(ggdag)

# List all variables
# Draw causal arrows
# Identify:
#   - Confounders (adjust)
#   - Colliders (don't adjust)
#   - Mediators (depends on question)
#   - Instruments (optional)

dag <- dagitty('dag {
    [your structure]
}')

# Find adjustment set
adjustmentSets(dag)
```

### Step 3: Check Assumptions
```r
# CONSISTENCY: Well-defined treatment
# - Treatment version doesn't matter OR
# - Same version in study population

# EXCHANGEABILITY: No unmeasured confounding
# - List all confounders
# - Justify completeness
# - Plan sensitivity analysis

# POSITIVITY: All subgroups can receive either treatment
# Check:
ps_range <- range(fitted(ps_model))
# Both bounds should be away from 0 and 1
```

### Step 4: Implement Analysis
```r
# Option A: Matching
library(MatchIt)
m <- matchit(treatment ~ confounders, data = df, method = "nearest")
matched_df <- match.data(m)
fit <- lm(outcome ~ treatment, data = matched_df, weights = weights)

# Option B: IPW
ps <- predict(glm(treatment ~ confounders, binomial), type = "response")
sw <- ifelse(treatment == 1, mean(treatment)/ps, (1-mean(treatment))/(1-ps))
fit <- glm(outcome ~ treatment, weights = sw)

# Option C: Doubly Robust
library(AIPW)
aipw <- AIPW$new(Y, A, W, Q.SL.library, g.SL.library)$fit()$summary()
```

### Step 5: Check Balance
```r
library(cobalt)
bal.tab(m, thresholds = c(m = 0.1))  # SMD < 0.1
love.plot(m)
```

### Step 6: Sensitivity Analysis
```r
library(EValue)
evalues.RR(est = point_estimate, lo = ci_lower, hi = ci_upper)

library(sensemakr)
sens <- sensemakr(model, treatment = "treatment", benchmark_covariates = "known_confounder")
```

### Step 7: Report Results
```markdown
## Results Template

### Target Trial Protocol
[Insert completed protocol table]

### DAG
[Figure showing assumed causal structure]

### Balance Assessment
- Standardized mean differences all < 0.1 after [matching/weighting]
- [Figure: Love plot]

### Main Results
- Estimated [effect measure]: X.XX (95% CI: X.XX to X.XX)
- P-value: X.XXX

### Sensitivity Analysis
- E-value: X.XX (for estimate), X.XX (for CI bound)
- Interpretation: [What strength unmeasured confounding would need]

### Limitations
- [Unmeasured confounders possible]
- [Positivity violations in subgroups]
- [Other causal identification issues]
```

## Learning integration

- **task_type:** analysis
- **log_fields:** method_used, balance_achieved, sensitivity_done
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Common Mistakes Checklist
- [ ] NOT checking for immortal time bias
- [ ] NOT aligning eligibility with time zero
- [ ] Including post-treatment variables in propensity score
- [ ] NOT checking balance after adjustment
- [ ] NOT doing sensitivity analysis
- [ ] Using language implying causation without proper methods

## References
- Hernán MA, Robins JM. Causal Inference: What If. 2020.
- Hernán MA, Robins JM. Using Big Data to Emulate a Target Trial. Am J Epidemiol. 2016.
```

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Definiraj target trial protokol za emulaciju u administrativnom kohortu."  
**Output:** "Eligibility i time-zero `[INFERRED]` uz podatke; varijable iz cohorta `[EXTRACTED]` ako su u kodu; bez sheme podataka `[BLANK]`."

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
