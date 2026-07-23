## Overview
Detailed reference for causal inference methodology.
For Cursor-activated rules, see `.cursor/rules/52_causal_inference.mdc`.

## 1. Target Trial Emulation Framework

### Hernán & Robins Framework
Target trial emulation bridges observational and experimental research by explicitly specifying what randomized trial would answer the causal question.

### Protocol Template
```markdown
## Target Trial Protocol

### 1. Eligibility Criteria
- Inclusion: [Specific criteria at time zero]
- Exclusion: [What makes ineligible]
- Time period: [When patients entered]

### 2. Treatment Strategies
- Strategy A: [Detailed treatment protocol]
- Strategy B: [Comparator protocol]
- Assignment: [How treatment determined in data]

### 3. Assignment Procedures
- Randomization: N/A (observational)
- Baseline confounders adjusted: [List]

### 4. Follow-up
- Start: [Time zero definition]
- End: [Outcome or censoring]
- Duration: [Maximum follow-up]

### 5. Outcome
- Primary: [Definition, timing]
- Secondary: [If applicable]

### 6. Causal Contrast
- Estimand: [ITT, per-protocol, etc.]
- Effect measure: [RR, OR, HR, RD]

### 7. Statistical Analysis
- Method: [IPW, standardization, etc.]
- Confounders: [Adjustment set]
- Sensitivity: [Unmeasured confounding]
```

### Common Biases and Solutions

| Bias | Cause | Solution |
|------|-------|----------|
| Immortal time | Misaligned time zero | Clone-censor-weight |
| Selection | Conditioning on post-treatment | Align eligibility to time zero |
| Confounding | Common causes | Adjust or weight |
| Informative censoring | Differential dropout | IPW for censoring |

## 2. Directed Acyclic Graphs (DAGs)

### Building DAGs

#### Step-by-Step Process
1. List all relevant variables
2. Identify temporal ordering
3. Draw arrows based on causal knowledge (not data)
4. Identify adjustment sets using rules:

```
d-separation rules:
1. Chains (A â†’ B â†’ C): B blocks path, don't adjust
2. Forks (A â† B â†’ C): B opens path, adjust
3. Colliders (A â†’ B â† C): B blocked, don't adjust (conditioning opens)
```

### DAG Tools Implementation
```r
library(dagitty)

# Define causal structure
dag <- dagitty('dag {
    // Exposure and Outcome
    Treatment [exposure]
    Outcome [outcome]
    
    // Confounders
    Age -> Treatment
    Age -> Outcome
    Comorbidity -> Treatment
    Comorbidity -> Outcome
    
    // Mediator
    Treatment -> Biomarker -> Outcome
    
    // Collider
    Treatment -> Hospitalization <- Outcome
}')

# Find minimal adjustment set
adjustmentSets(dag, effect = "total")
# Returns: { Age, Comorbidity }

# Check if a set is sufficient
isAdjustmentSet(dag, c("Age", "Comorbidity"))
# Returns: TRUE

# Find instrumental variables
instrumentalVariables(dag)

# Implied conditional independencies (testable)
impliedConditionalIndependencies(dag)
```

### Common DAG Patterns in Medical Research

#### Mediation
```
Treatment â†’ Mediator â†’ Outcome
    â†“                    â†‘
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ (direct effect)

Analysis:
- Total effect: Don't adjust for mediator
- Direct effect: Adjust for mediator (if no mediator-outcome confounding)
- Use mediation analysis for decomposition
```

#### Time-Varying Confounding
```
Lâ‚€ â†’ Aâ‚€ â†’ Lâ‚ â†’ Aâ‚ â†’ Y
 â†“    â†“    â†“    â†“
 â””â”€â”€â”€â”€â”´â”€â”€â”€â”€â”´â”€â”€â”€â”€â”˜
 
Solution: G-methods (IPW, g-formula, g-estimation)
Standard regression FAILS here
```

## 3. Propensity Score Methods Deep Dive

### Which Propensity Score Method to Use — Decision Algorithm

Follow this decision tree before selecting a PS method:

1. **Is treatment binary or continuous?**
   - Continuous treatment → generalized propensity score + IPTW (PSM not valid)
   - Binary → continue to step 2

2. **What estimand do you need?**
   - ATT (Average Treatment Effect in Treated) → Propensity Score Matching (PSM)
   - ATE (Average Treatment Effect, population) → IPTW with stabilized weights or TMLE

3. **How large is the sample?**
   - Small sample + good overlap → PSM (intuitive, easy to check balance)
   - Large sample → IPTW (more efficient, uses all patients)

4. **How worried are you about model misspecification?**
   - Very worried → AIPW or TMLE (doubly robust: protected if one model is wrong)
   - Moderately worried → stabilized IPTW + sensitivity analysis

5. **Time-varying treatment?**
   → Marginal Structural Model (MSM) with time-varying IPTW

**Default recommendation for ICU observational studies:**
IPTW with stabilized weights as primary analysis + AIPW as doubly robust sensitivity analysis.

### Propensity Score Estimation

#### Model Building
```r
# Baseline model
ps_model <- glm(
    treatment ~ age + sex + comorbidity + baseline_severity,
    data = df,
    family = binomial(link = "logit")
)

# With splines for continuous
library(splines)
ps_model <- glm(
    treatment ~ ns(age, df = 4) + sex + ns(baseline_severity, df = 3),
    data = df,
    family = binomial
)

# Machine learning approach (for high-dimensional)
library(SuperLearner)
sl_ps <- SuperLearner(
    Y = df$treatment,
    X = df[, covariate_cols],
    family = binomial(),
    SL.library = c("SL.glm", "SL.ranger", "SL.xgboost")
)
```

### Matching Methods

#### Nearest Neighbor
```r
library(MatchIt)

# 1:1 nearest neighbor without replacement
m1 <- matchit(
    treatment ~ age + sex + comorbidity,
    data = df,
    method = "nearest",
    distance = "glm",  # logistic PS
    caliper = 0.2,     # 0.2 SD of logit PS
    ratio = 1
)

# Extract matched data
matched_df <- match.data(m1)
```

#### Optimal Matching
```r
# Minimizes total distance (better balance, slower)
m_opt <- matchit(
    treatment ~ age + sex + comorbidity,
    data = df,
    method = "optimal",
    ratio = 1
)
```

#### Full Matching
```r
# Variable ratio matching (no sample loss)
m_full <- matchit(
    treatment ~ age + sex + comorbidity,
    data = df,
    method = "full"
)
```

### Inverse Probability Weighting

#### Weight Calculation
```r
# Unstabilized weights
df$ps <- predict(ps_model, type = "response")
df$ipw <- ifelse(df$treatment == 1, 1/df$ps, 1/(1-df$ps))

# Stabilized weights (recommended)
p_treat <- mean(df$treatment)
df$sw <- ifelse(
    df$treatment == 1,
    p_treat / df$ps,
    (1 - p_treat) / (1 - df$ps)
)

# Check weight distribution
summary(df$sw)
# Ideal: mean â‰ˆ 1, no extreme values

# Truncate extreme weights if needed
df$sw_truncated <- pmin(pmax(df$sw, quantile(df$sw, 0.01)), 
                         quantile(df$sw, 0.99))
```

#### Weighted Outcome Analysis
```r
# Weighted regression
library(survey)
design <- svydesign(ids = ~1, weights = ~sw, data = df)
model <- svyglm(outcome ~ treatment, design = design)

# Or with robust SE
library(sandwich)
model <- glm(outcome ~ treatment, data = df, weights = sw)
coeftest(model, vcov = vcovHC(model, type = "HC1"))
```

### Balance Diagnostics

#### Standardized Mean Difference
```r
library(cobalt)

# Before and after matching
bal.tab(m1, thresholds = c(m = 0.1))

# Visual assessment
love.plot(m1, 
          thresholds = c(m = .1),
          var.order = "unadjusted")

# Variance ratio (for continuous variables)
# Target: 0.5 to 2.0
```

#### Overlap Assessment
```r
# PS distribution by treatment
bal.plot(m1, var.name = "distance", which = "both")

# Check positivity
# Flag if any PS < 0.01 or > 0.99
sum(df$ps < 0.01 | df$ps > 0.99)
```

## 4. Doubly Robust Methods

### AIPW Estimator
```r
library(AIPW)

# Define models
# Outcome model with SuperLearner
# PS model with SuperLearner

aipw <- AIPW$new(
    Y = df$outcome,
    A = df$treatment,
    W = df[, covariate_cols],
    Q.SL.library = c("SL.glm", "SL.ranger", "SL.gam"),
    g.SL.library = c("SL.glm", "SL.ranger")
)$
fit()$
summary()

# Access results
aipw$result  # ATE, SE, CI
```

### Targeted Maximum Likelihood Estimation (TMLE)
```r
library(tmle)

result <- tmle(
    Y = df$outcome,
    A = df$treatment,
    W = df[, covariate_cols],
    family = "binomial",  # for binary outcome
    Q.SL.library = c("SL.glm", "SL.ranger"),
    g.SL.library = c("SL.glm", "SL.ranger")
)

# Results
result$estimates$ATE  # Point estimate
result$estimates$CI   # Confidence interval
```

## 5. Sensitivity Analysis for Unmeasured Confounding

### E-value
```r
library(EValue)

# For risk ratio
evalues.RR(
    est = 1.5,     # Observed RR
    lo = 1.2,      # Lower CI
    hi = 1.9       # Upper CI
)

# Interpretation:
# E-value = 2.3 means an unmeasured confounder would need
# RR â‰¥ 2.3 with both treatment AND outcome to fully explain
# the observed association
```

### Sensitivity Analysis with sensemakr
```r
library(sensemakr)

# Fit outcome model
model <- lm(outcome ~ treatment + covariates, data = df)

# Sensitivity analysis
sens <- sensemakr(
    model = model,
    treatment = "treatment",
    benchmark_covariates = c("age", "comorbidity"),  # Known confounders
    kd = 1:3,  # 1x, 2x, 3x confounder strength
    ky = 1:3
)

# Contour plot
plot(sens)

# Summary
summary(sens)
```

### Rosenbaum Bounds (for Matching)
```r
library(rbounds)

# After matching
psens(matched_data$outcome[matched_data$treatment == 1] - 
      matched_data$outcome[matched_data$treatment == 0],
      Gamma = 2)  # Test sensitivity to 2x odds of treatment

# Interpretation:
# If significant at Gamma = 2, result robust to unmeasured
# confounder that doubles odds of treatment
```

## 6. Time-Varying Treatments

### G-computation
```r
library(gfoRmula)

# Specify models
gform <- gformula(
    outcome_model = list(
        formula = Y ~ treatment_lag1 + L + A,
        family = "binomial"
    ),
    covariate_model = list(
        formula = L ~ treatment_lag1 + L_lag1,
        family = "gaussian"
    ),
    treatment_model = list(
        formula = A ~ L,
        family = "binomial"
    ),
    data = long_data,
    id = "id",
    time = "time",
    intervention = list(
        "always_treat" = function(a, t) return(1),
        "never_treat" = function(a, t) return(0)
    )
)

# Estimate
result <- gform$estimate()
```

### Marginal Structural Models
```r
# Calculate time-varying weights
library(ipw)

# Weight at each time point
df$weight <- ipwtm(
    exposure = treatment ~ L + treatment_lag1,
    family = "binomial",
    link = "logit",
    numerator = ~ treatment_lag1,
    data = long_df,
    id = "id",
    type = "all"
)$ipw.weights

# Weighted outcome model
library(geepack)
msm <- geeglm(
    outcome ~ treatment,
    data = long_df,
    weights = weight,
    id = id,
    corstr = "independence"
)
```

## 7. Further Reading (JMLR)

The following *Journal of Machine Learning Research* (JMLR) papers extend or complement the methods above. Use when specifying estimands, treatment regimes, or causal discovery.

| Topic | Paper | When to use |
|-------|--------|-------------|
| **Identifiability under non-additive models** | Bodik & Chavez-Demoulin, "Identifiability of Causal Graphs under Non-Additive Conditionally Parametric Causal Models" (JMLR 2025) | When treatment/outcome models are non-additive; check whether causal graph remains identifiable. |
| **Optimal treatment regimes (survival)** | Zhao et al., "Efficient and Robust Transfer Learning of Optimal Individualized Treatment Regimes with Right-Censored Survival Data" (JMLR 2025) | Individualized treatment rules with time-to-event outcomes; transfer learning. |
| **Causal effect of functional treatment** | Tan et al., "Causal Effect of Functional Treatment" (JMLR 2025) | Exposure is a function (e.g. time-varying dose); estimand definition. |
| **Experiment design for causal ID** | Akbari et al., "Optimal Experiment Design for Causal Effect Identification" (JMLR 2025) | Designing experiments or data collection to identify causal effects. |

**Source:** [Journal of Machine Learning Research](https://www.jmlr.org/) — all papers freely available.

---

## References

1. Hernán & Robins "Causal Inference: What If" (2020): https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/
2. Hernán & Robins "Target Trial Emulation" (2016): JAMA
3. Austin "Propensity Score Methods" (2011): Multivariate Behavioral Research
4. VanderWeele & Ding "Sensitivity Analysis" (2017): Annals of Internal Medicine
5. MatchIt: kosukeimai.github.io/MatchIt
6. dagitty: dagitty.net

---

**Version:** 1.1  
**Last updated:** 2026-04-10

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
