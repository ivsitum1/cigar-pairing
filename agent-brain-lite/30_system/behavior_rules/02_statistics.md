> **⚠️ PARTIALLY MIGRATED:** Test selection framework has been migrated to `.cursor/rules/statistics-test-selection.mdc`.
> See `.cursor/rules/statistics-test-selection.mdc` for modern test selection hierarchy.
> This file is retained for comprehensive statistical rules and backward compatibility.

# Statistical Rules and Guidelines

## Purpose

This document establishes standardized rules and guidelines for conducting statistical analyses in meta-analysis projects. These rules ensure consistency, transparency and adherence to best practices.

**Related Knowledge Base:**
- `20_knowledge/reference_library/statistics/knowledge_bases/medical_data_science_laboratory.md` — Complete 17-layer methodological framework
- `20_knowledge/reference_library/statistics/knowledge_bases/modern_statistical_literature_2024_2025.md` — Latest methodological advances with verification status

---

## Statistical Workflow Protocol (MANDATORY)

### 0. General Principles

- Use **R (tidyverse ecosystem)**, avoid experimental or unstable packages
- Every analysis must be:
  - Reproducible (`set.seed()`)
  - Transparent (no "magic numbers")
  - Clinically motivated
- Clearly separate:
  - **Descriptive analysis**
  - **Inferential analysis**
  - **Modeling**
  - **Validation**
- Never rely solely on p-value → always show **effect size + CI**

### 1. Data Loading and Initial Review

**Data loading:**
```r
set.seed(123)
library(tidyverse)

DATA_PATH <- "data/analysis_dataset.csv"
df <- read_csv(DATA_PATH)
```

**Structure review (MANDATORY):**
- `str(df)`
- `glimpse(df)`
- `summary(df)`

**Identify:**
- Variable types (numeric, factor, ordered)
- Obvious inconsistencies (e.g., negative values where not allowed)

### 2. Exploratory Data Analysis (EDA) - FlexPlot-First Protocol

**MANDATORY: Use FlexPlot for initial exploration**

```r
library(flexplot)

# 1. Quick overview of relationships
flexplot(outcome ~ predictor, data = df)

# 2. Distribution check
flexplot(variable ~ 1, data = df, method = "histogram")

# 3. Relationship exploration with covariates
flexplot(y ~ x + z, data = df)
```

**Purpose:** Visual verification of relationships and interactions before modeling.

**Standard visualizations (also required):**
- Histogram / density plot
- Boxplot / violin plot
- Scatter plot for relationships

**Descriptive statistics:**
```r
df %>%
  summarise(across(where(is.numeric), list(
    mean = mean,
    sd = sd,
    median = median,
    iqr = IQR
  ), na.rm = TRUE))
```

**Format:**
- Continuous variables: mean ± SD **and/or** median [IQR]
- Categorical variables: n (%)

### 3. Distribution and Descriptive Diagnostics (Do NOT Use for Test Selection)

**MANDATORY: Use descriptive checks only.** Do **not** use formal assumption tests (Shapiro–Wilk, Kolmogorov–Smirnov, Levene, Bartlett) to decide between parametric and nonparametric tests. Follow the hierarchy in `.cursor/rules/statistics-test-selection.mdc`.

**Descriptive diagnostics (for reporting and context only):**
```r
# Descriptive only — NOT for choosing tests
check_descriptive <- function(x) {
  list(
    n = length(na.omit(x)),
    skewness = moments::skewness(x, na.rm = TRUE),
    kurtosis = moments::kurtosis(x, na.rm = TRUE),
    outliers = length(boxplot.stats(x)$out)
  )
}
# Use histograms, density plots, boxplots for exploration.
```

**Test selection:** Use **Welch's t-test** as default for two independent groups; **permutation Welch** for small samples (n < 20) or strong non-normality; **Yuen–Welch** or **permutation Yuen–Welch** for outliers/heavy tails. Use rank tests only as **sensitivity analyses**. See `statistics-test-selection.mdc` for full decision tree.

## Survival Data Test Selection

For time-to-event outcomes: use log-rank test (2 groups) or Cox proportional hazards
(multivariable). Check PH assumption with Schoenfeld residuals (`cox.zph()`).
For competing risks: use Fine-Gray subdistribution HR or cause-specific HR (`cmprsk` package).
Do NOT use standard t-tests or ANOVA for time-to-event data.

## Effect Size Thresholds

| Effect size | Small | Medium | Large |
|-------------|-------|--------|-------|
| Cohen's d   | 0.2   | 0.5    | 0.8   |
| Pearson r   | 0.1   | 0.3    | 0.5   |
| Odds ratio  | 1.5   | 2.5    | 4.0   |
| Eta-squared | 0.01  | 0.06   | 0.14  |

Never write "medium effect" or "large effect" without citing the specific threshold used.

## When to Use Bayesian Methods

Use Bayesian inference (not frequentist) when:

- Sample size is small (n < 30 total) AND relevant prior information exists
- Sequential design requires interim analysis without inflating Type I error
- The research question is explicitly about P(effect | data), not P(data | H₀)

When using Bayesian methods:

- Specify prior distribution and justify the choice
- Report sensitivity analysis varying the prior
- Use `brms` or `rstanarm` in R
- Report posterior median + 95% credible interval (not p-values)

## Clustered and Hierarchical Data

ICU data is almost always hierarchical (patients nested in units, units in hospitals,
repeated measures within patients). Standard regression violates independence assumptions
and inflates Type I error when clustering exists.

Rules:

- Calculate ICC (intraclass correlation coefficient) before any regression analysis
- If ICC > 0.05: mixed-effects models are mandatory (not optional)
  - Continuous outcomes: `lmer()` from lme4
  - Binary outcomes: `glmer()` from lme4
- Report ICC in all manuscripts with clustered data
- For clustered RCTs: account for clustering in sample size calculation (design effect)
- Minimum 10–20 clusters required for reliable random effects estimation

### 4. Missing Data - Assessment and Handling

**Assessment:**
```r
library(naniar)
vis_miss(df)  # Visualize missing patterns
```

**Strategy:**
- <5% missing → Complete case analysis (with warning)
- ≥5% and clinically justified → **Multiple Imputation (MICE)**

**MICE Workflow:**
```r
library(mice)

# Imputation
imp <- mice(df, m = 20, method = "pmm", seed = 123)

# Check convergence
plot(imp)

# Complete dataset
df_imp <- complete(imp, "long")

# Pool results (for analysis)
# Use with() and pool() for regression models
```

**MANDATORY checks:**
- Justify MAR assumption
- Check convergence
- Report imputation method and m (number of imputations)

### 5. Bootstrap for Effect Sizes and Confidence Intervals

**MANDATORY: Use bootstrap for effect size CI**

```r
library(boot)

boot_fun <- function(data, idx) {
  d <- data[idx, ]
  mean(d$outcome[d$group == 1]) - mean(d$outcome[d$group == 0])
}

boot_res <- boot(df, boot_fun, R = 5000)
boot.ci(boot_res, type = "perc")
```

**Bootstrap is used for:**
- Confidence intervals for effect sizes
- Stability of estimates
- Non-parametric inference

**Minimum R = 5000** for stable estimates.

---

## Meta-Analysis - General Rules

### Effect Model Selection

**Rule: Always Calculate Both Random and Common Effects**

**Rationale:**
- Random effects model accounts for heterogeneity between studies
- Common effects model assumes all studies share the same true effect
- Cochrane recommends reporting both, with random effects as primary

**Implementation:**
```r
ma <- metacont(..., random = TRUE, common = TRUE)
# or
ma <- metabin(..., random = TRUE, common = TRUE)
```

**Decision Criteria:**
- **Primary analysis**: Always use random effects model
- **Sensitivity analysis**: Report common effects for comparison
- **When I² = 0%**: Both models give same results, but still report both for transparency

**Justification:**
- Even with low heterogeneity, random effects is more conservative
- Accounts for any heterogeneity that is present
- Preferred by Cochrane guidelines

---

## Heterogeneity - Thresholds and Interpretation

### I² Interpretation Thresholds

| I² Value | Interpretation | Action |
|----------|---------------|--------|
| 0-40% | May not be important (low) | Acceptable, still use random effects |
| 30-60% | May represent moderate heterogeneity | Acceptable, investigate sources if I² > 50% |
| 50-90% | May represent substantial heterogeneity | Investigate sources, report prediction intervals |
| 75-100% | Substantial heterogeneity | Strongly investigate sources, consider subgroup analysis |

### τ² (Tau-squared) Estimation

**Preferred Estimator:**
- **Primary**: REML (Restricted Maximum Likelihood)
- **Comparison**: DL (DerSimonian-Laird) for Cochrane compatibility

**Implementation:**
```r
ma <- update(ma, method.tau = "REML")  # Primary
ma_DL <- update(ma, method.tau = "DL")  # For comparison
```

### Q-Statistic

**Interpretation:**
- p < 0.10 or p < 0.05: Suggests heterogeneity
- Consider in context of I² (Q may be significant with low I² if many studies)
- Consider in context of I² (Q may not be significant with high I² if few studies)

---

## Outlier Detection and Handling

### Detection Methods

1. **Visual Inspection**: Forest plot
2. **Standardized Residuals**: |residual| > 2 or > 3
3. **Influence Analysis**: Cook's distance, DFFITS
4. **Leave-One-Out Analysis**: Large changes in pooled estimate

### Standardized Residual Thresholds

- |Residual| > 2: Potentially influential
- |Residual| > 3: Likely outlier

### Handling Strategy

1. **Identify outliers** using influence analysis
2. **Primary analysis**: Include all studies
3. **Sensitivity analysis**: Exclude outliers and report both results
4. **Document**: Report both analyses, explain all differences
5. **NEVER**: Exclude outliers without sensitivity analysis

**Implementation:**
```r
# Primary analysis (all studies)
ma_all <- ma

# Influence analysis
inf <- influence(ma)
outliers <- which(abs(inf$resid) > 3)

# Sensitivity analysis (without outliers)
ma_clean <- update(ma, subset = !(1:ma$k %in% outliers))
```

---

## Missing Data

### Approach Hierarchy

1. **Contact authors**: Preferred method for missing data
2. **Use published estimates**: If raw data unavailable but effect estimates published
3. **Imputation**: Only as sensitivity analysis, clearly documented
4. **Exclude from analysis**: Only if critical data missing and cannot be obtained

### Rules for Missing Standard Deviations

**For continuous outcomes:**
- If SD missing: Contact authors first
- If unavailable: Use imputation methods (e.g., coefficient of variation, SD from other studies)
- Clearly document all assumptions
- Sensitivity analysis excluding studies with imputed SDs

**Implementation:**
```r
# Check for missing SDs
missing_sd <- is.na(data$sd_tiva) | is.na(data$sd_sevo)

# Document
cat("Studies with missing SDs:", sum(missing_sd), "\n")

# Sensitivity analysis
ma_complete <- update(ma, subset = !missing_sd)
```

### Rules for Zero Events

**For binary outcomes:**
- Use continuity correction if zero events in one group
- Preferred: Treatment arm continuity correction (TACC) or 0.5
- Try multiple corrections as sensitivity analysis
- Document all corrections used

**Implementation:**
```r
# Multiple continuity corrections
ma_cc05 <- metabin(..., incr = 0.5)
ma_cc_tacc <- metabin(..., incr = "TACC")
ma_no_cc <- metabin(..., incr = 0)
```

---

## Transformations and Assumptions

### Log Transformation

**When to use:**
- Risk ratios and odds ratios (always log-transform for analysis)
- Skewed continuous outcomes (if needed)
- Count data (if needed)

**Rules:**
- Always use log scale for RR/OR internally
- Report on original scale in results
- Ensure back-transformation is accurate: exp(log_RR) = RR

### Normality Assumptions

**For continuous outcomes:**
- Meta-analysis is robust to non-normality with reasonable sample sizes (n > 30 per group)
- Check extreme outliers (influence analysis)
- Formal normality test not needed for individual studies in meta-analysis

### Variance Homogeneity

**For continuous outcomes:**
- Not needed for meta-analysis (uses study-specific variances)
- Each study contributes its own variance

---

## Statistical Tests

### Test for Overall Effect

**Always report:**
- z-statistic (Wald test)
- p-value (exact value, not just < 0.05)
- Test for both random and common effects

**Implementation:**
```r
forest(ma,
       test.overall.random = TRUE,
       test.overall.fixed = TRUE)
```

### Heterogeneity Tests

**Always report:**
- Q-statistic with degrees of freedom
- p-value for Q
- I² with interpretation
- τ² with confidence interval (if available)

### Subgroup Difference Test

**When performing subgroup analysis:**
- Use chi-square test for subgroup differences (Cochran's Q_between)
- Report p-value for interaction
- Interpret cautiously (often low power)

**Implementation:**
```r
forest(ma,
       byvar = subgroup,
       print.CMH = TRUE)  # Test for subgroup differences
```

---

## Publication Bias Assessment

### Minimum Requirements

1. **Funnel plot**: Always if ≥10 studies
2. **Statistical test**: 
   - Binary outcomes: Peters' test (preferred), Egger's test (comparison)
   - Continuous outcomes: Egger's test
3. **Trim-and-fill**: When asymmetry detected

### Rules

- **<10 studies**: Visual inspection only, acknowledge low power
- **≥10 studies**: Complete assessment (funnel plot + statistical test + trim-and-fill)
- **Interpretation**: Consider other causes of asymmetry (heterogeneity, quality, true effect)

**Implementation:**
```r
# Funnel plot
if(ma$k >= 10) {
  funnel(ma, contour = c(0.9, 0.95, 0.99))
  
  # Statistical test
  if(outcome_type == "binary") {
    peters_test <- metabias(ma, method = "peters")
    egger_test <- metabias(ma, method = "egger")
  } else {
    egger_test <- metabias(ma, method = "egger")
  }
  
  # Trim-and-fill
  tf <- trimfill(ma)
}
```

---

## Meta-Regression Rules

### Prerequisites

- **Minimum studies**: ≥10 (ideally ≥20)
- **A priori hypotheses**: Test only pre-specified covariates
- **Heterogeneity present**: I² > 0% (otherwise little to explain)

### Rules

1. **Pre-specify**: All covariates must be specified in protocol
2. **Avoid data dredging**: Do not test many covariates without hypotheses
3. **Report R²**: Proportion of heterogeneity explained
4. **Report residual heterogeneity**: τ² after adjustment
5. **Multiple testing**: Consider Bonferroni correction if testing many covariates

**Implementation:**
```r
# Only if k >= 10 and I² > 0
if(ma$k >= 10 && ma$I2 > 0) {
  # Only pre-specified covariates
  res <- rma(yi, vi, mods = ~ year, data = dat, method = "REML")
  cat("R² =", res$R2, "\n")
  cat("Residual τ² =", res$tau2, "\n")
}
```

---

## Sensitivity Analysis Requirements

### Mandatory Sensitivity Analyses

1. **Leave-one-out**: Assessment of individual study influence
2. **Method comparison**: Random vs. common effects, different τ² estimators
3. **Core vs. all studies**: If sensitivity studies included

### Optional (But Recommended)

4. **Risk of bias**: Restrict to high-quality studies
5. **Outlier removal**: If outliers identified
6. **Continuity correction**: Different corrections for zero events
7. **Subgroup analysis**: By clinically relevant factors

### Reporting Rules

- Report all sensitivity analyses in supplementary material
- Compare results with primary analysis
- Discuss all significant differences
- Document robustness or lack thereof

---

## Best Practices in Medical Statistics

### Clinical vs. Statistical Significance
- Always interpret both statistical AND clinical significance
- Consider Minimal Clinically Important Difference (MCID) when available
- Report Number Needed to Treat (NNT) for binary outcomes when appropriate
- Consider absolute risks, not just relative risks

### Reporting Standards
- Report exact p-values (not just p < 0.05)
- Always report 95% confidence intervals with point estimates
- Report sample sizes for all groups
- Distinguish between "no difference" and "proven equivalence"
- Avoid selective reporting - report all pre-specified outcomes

### Common Errors to Avoid
1. Dichotomizing p-values - report exact values
2. Ignoring heterogeneity - always report and interpret
3. Over-interpreting non-significant results - "no difference" ≠ "proven equivalence"
4. Selective reporting - report all pre-specified outcomes
5. Missing confidence intervals - always report with point estimates
6. Ignoring clinical significance - statistical ≠ clinical significance
7. Reporting only relative risks without absolute risks

---

## Statistical Error Types - Type 1, Type 2, Type M, and Type S Errors

### Overview

When conducting statistical analyses, it is essential to consider not only traditional Type 1 and Type 2 errors, but also Type M (magnitude) and Type S (sign) errors, particularly in the context of underpowered studies or when effect sizes are estimated with uncertainty.

### Type 1 Error (False Positive)

**Definition:**
- Rejecting the null hypothesis when it is actually true
- Concluding there is an effect when there is none

**Control:**
- Controlled by significance level (α), typically set at 0.05
- Multiple testing corrections (Bonferroni, FDR) when testing multiple hypotheses
- Pre-specification of primary outcomes reduces risk

**Reporting:**
- Always report exact p-values, not just "p < 0.05"
- When multiple comparisons are made, report correction method used

### Type 2 Error (False Negative)

**Definition:**
- Failing to reject the null hypothesis when it is actually false
- Concluding there is no effect when there actually is one

**Control:**
- Controlled by statistical power (1 - β)
- Power depends on: effect size, sample size, significance level, and variability
- Aim for power ≥ 80% (β ≤ 0.20) for primary outcomes

**Reporting:**
- Report power calculations for primary outcomes
- When results are non-significant, discuss whether study was adequately powered
- Distinguish between "no difference" and "proven equivalence" (equivalence requires different design)

**Implementation:**
```r
# Power calculation example
library(pwr)
pwr.t.test(d = 0.5, power = 0.80, sig.level = 0.05, type = "two.sample")
```

### Type M Error (Magnitude Error)

**Definition:**
- The ratio of the absolute value of the estimated effect to the true effect
- Type M error > 1 means the estimated effect is larger than the true effect (exaggeration)
- Type M error < 1 means the estimated effect is smaller than the true effect (underestimation)

**When it matters:**
- Particularly important in underpowered studies
- When true effect is small relative to measurement error
- In studies with high variability or small sample sizes
- When p-values are just below significance threshold (p ≈ 0.05)

**Implications:**
- Significant results in underpowered studies are likely to be exaggerated
- The "winner's curse": published significant effects are often overestimated
- Can lead to overestimation of clinical importance

**Considerations:**
- Report confidence intervals, not just point estimates
- Consider prediction intervals in meta-analysis
- Be cautious interpreting effect sizes from underpowered studies
- Consider Bayesian approaches that can provide more realistic effect size estimates

**Reporting:**
- When study is underpowered, explicitly note that effect size estimates may be exaggerated
- Report confidence intervals to show uncertainty
- In meta-analysis, report prediction intervals to show expected range of true effects

### Type S Error (Sign Error)

**Definition:**
- The probability that the estimated effect has the wrong sign (positive vs. negative)
- Concluding the effect is in one direction when it is actually in the opposite direction

**When it matters:**
- In underpowered studies
- When true effect is small relative to standard error
- When confidence intervals include zero and extend far in both directions
- In studies with high variability

**Implications:**
- Can lead to completely wrong conclusions about direction of effect
- Particularly dangerous when making clinical recommendations
- More likely when p-values are close to significance threshold

**Considerations:**
- Wide confidence intervals that include zero suggest risk of Type S error
- Report confidence intervals, not just p-values
- Consider whether confidence interval excludes clinically meaningful effects in both directions
- In meta-analysis, check for consistency of direction across studies

**Reporting:**
- When confidence intervals are wide and include zero, note uncertainty about direction
- Report confidence intervals alongside p-values
- Discuss clinical implications of both possible directions

### Practical Guidelines

**For All Statistical Analyses:**

1. **Always consider all four error types:**
   - Type 1: False positive (controlled by α)
   - Type 2: False negative (controlled by power)
   - Type M: Magnitude exaggeration/underestimation
   - Type S: Wrong sign

2. **Report confidence intervals:**
   - Confidence intervals provide information about Type M and Type S errors
   - Wide intervals suggest high uncertainty (risk of Type M and Type S errors)
   - Intervals that include zero suggest risk of Type S error

3. **Consider study power:**
   - Underpowered studies have higher risk of Type M and Type S errors
   - Significant results from underpowered studies are likely exaggerated
   - Non-significant results from underpowered studies provide little information

4. **Interpretation:**
   - Be cautious interpreting effect sizes from underpowered studies
   - Consider prediction intervals in meta-analysis
   - Discuss uncertainty and limitations honestly

5. **Reporting standards:**
   - Always report: point estimate, confidence interval, p-value, and power (if applicable)
   - Discuss implications of uncertainty
   - Avoid overinterpreting results from underpowered studies

**Implementation Example:**
```r
# Example: Reporting with consideration of all error types
# After analysis, report:
cat("Effect estimate: ", effect_estimate, "\n")
cat("95% CI: [", ci_lower, ", ", ci_upper, "]\n")
cat("p-value: ", p_value, "\n")
cat("Power: ", power, "\n")

# If underpowered:
if (power < 0.80) {
  cat("WARNING: Study is underpowered (power = ", power, ").\n")
  cat("Significant results may be exaggerated (Type M error).\n")
  cat("Wide confidence intervals suggest uncertainty about direction (Type S error risk).\n")
}
```

### References

- Gelman, A., & Carlin, J. (2014). Beyond power calculations: Assessing type S (sign) and type M (magnitude) errors. *Perspectives on Psychological Science*, 9(6), 641-651.
- Button, K. S., et al. (2013). Power failure: why small sample size undermines the reliability of neuroscience. *Nature Reviews Neuroscience*, 14(5), 365-376.

---

## Hypothesis Testing for Primary Clinical Studies

**Decision tree and primary hierarchy:** `.cursor/rules/statistics-test-selection.mdc`. The section below expands with SAP limitations, ordinal outcomes, and reporting.

### General Philosophy

**Fundamental Principles:**
- **DO NOT** base choice between parametric and nonparametric tests solely on formal assumption tests (Shapiro–Wilk, Kolmogorov–Smirnov, Levene, Bartlett, etc.).
- Use **robust parametric and permutation procedures** as PRIMARY tools.
- Treat **nonparametric rank tests** as SECONDARY or SENSITIVITY analyses.
- Use graphical diagnostics (histograms, density plots, Q–Q plots) and simple summaries (skewness, outliers) only as descriptive guidance, not as hard decision rules.

**Rationale:**
- Robust parametric methods directly estimate clinically interpretable estimands (mean differences)
- Maintain Type I error control under heteroscedasticity and moderate deviation from normality
- Often provide greater power than traditional nonparametric tests
- Permutation methods provide exact inference without distributional assumptions

### Design Structure Identification

**Always detect whether comparison is:**
- **Independent groups** (between-subjects): Two or more separate groups of participants
- **Paired / matched / repeated measures** (within-subjects): Same participants measured multiple times, or matched pairs

**For paired designs:**
- Use paired versions of all methods listed below (paired Welch, paired permutation tests, paired robust 40_operations/tests)

### Two-Group Comparisons of Continuous Outcomes

#### 3.1 Independent Groups

**Primary Method:**
- Use **Welch's t-test** as default primary method (assumes unequal variances).
- This is robust to unequal variances and moderate non-normality.

**When to use classical Student's t-test:**
- Only if there is clear substantive reason to assume equal variances (and document that reason explicitly).

**For small samples or strong non-normality:**
- Use **permutation version of Welch's t-test**:
  - Retain Welch's t statistic as test statistic
  - Obtain p-values (and confidence intervals if possible) via permutation of group labels
  - Recommended when n < 20 per group and/or distribution is clearly strongly non-normal

**For outliers or heavy tails:**
- Use **robust trimmed-mean test**, such as **Yuen–Welch's test** with 20% trimming by default
- When possible, combine with permutation p-values (permutation Yuen–Welch)

**Implementation:**
```r
# Primary: Welch's t-test
test_welch <- t.test(outcome ~ group, var.equal = FALSE)

# Permutation Welch (for small samples)
library(coin)
test_perm <- independence_test(outcome ~ group, distribution = "exact")

# Robust trimmed mean (Yuen-Welch)
library(WRS2)
test_yuen <- yuen.t.test(outcome ~ group, tr = 0.2)
```

#### 3.2 Paired / Matched Groups

**Primary Method:**
- Use **paired Welch-type t-test** (on differences) as default
- Test null hypothesis that mean difference = 0

**For strongly non-normal differences or outliers:**
- Use **permutation paired t-test** and/or **robust trimmed-mean test on differences**

**Implementation:**
```r
# Primary: Paired t-test
test_paired <- t.test(outcome_time1, outcome_time2, paired = TRUE)

# Permutation paired test
library(coin)
test_perm_paired <- independence_test(outcome ~ time | id, distribution = "exact")
```

### Multi-Group Comparisons (> 2 Groups)

**Primary Method:**
- Prefer **Welch-type ANOVA** (heteroscedastic one-way ANOVA) instead of classical equal-variance ANOVA
- This is robust to unequal variances between groups

**For strong outliers or heavy tails:**
- Use **robust ANOVA based on trimmed means** (e.g., Yuen-type procedure)
- Combine with permutation p-values where possible

**Implementation:**
```r
# Primary: Welch ANOVA
library(onewaytests)
test_welch_anova <- welch.test(outcome ~ group)

# Robust ANOVA (trimmed means)
library(WRS2)
test_robust_anova <- t1way(outcome ~ group, tr = 0.2)
```

### Ordinal Outcomes

**When outcome is truly ordinal:**
- If outcome is truly ordinal (e.g., Likert-type scales where interval meaning is questionable) and primary interest is in order rather than mean on interval scale:
  - Use **rank-based tests (Mann–Whitney, Wilcoxon, Kruskal–Wallis)** as primary tests, OR
  - Use appropriate **ordinal regression models** (e.g., cumulative logit / proportional odds)

**When ordinal scale has many categories:**
- If ordinal scale has many categories and commonly treated as approximately continuous in field:
  - Acceptable to apply robust parametric framework above
  - Clearly explain this choice in summary text

### Role of Nonparametric Rank-Based Tests

**DO NOT automatically switch to Mann–Whitney/Wilcoxon** just because normality or variance test is "significant".

**Use Mann–Whitney/Wilcoxon/Kruskal–Wallis primarily in two situations:**

1. **Outcome is truly ordinal or rank-based** (see above)
2. **As secondary / sensitivity analyses** to reassure conservative reviewers that conclusions do not depend on parametric assumptions

**When performing robust parametric tests as primary analyses:**
- Optionally calculate Mann–Whitney or Kruskal–Wallis as sensitivity checks
- Report that they lead to qualitatively similar conclusions (if they do)
- Always clearly state that:
  - Robust parametric/permutation procedures were chosen intentionally (not from ignorance of nonparametric 40_operations/tests)
  - Rank-based tests were additionally explored as sensitivity analyses when appropriate

**Implementation:**
```r
# Primary: Welch's t-test
test_primary <- t.test(outcome ~ group, var.equal = FALSE)

# Sensitivity: Mann-Whitney
test_sensitivity <- wilcox.test(outcome ~ group)

# Report both, emphasizing primary method
```

### Handling Assumptions and SAP Limitations

**Formal assumption tests:**
- You may calculate Shapiro–Wilk, Levene, or similar tests
- Treat them as **descriptive diagnostics** only
- **DO NOT** use rigid rules like "if p < 0.05 then switch to Mann–Whitney"

**Statistical Analysis Plan (SAP) limitations:**
- If formal SAP, protocol, or trial registration explicitly specifies certain primary test (e.g., Wilcoxon rank-sum):
  - **MUST** follow that specification for primary analysis
  - You may add robust methods as secondary or exploratory analyses
- Document in summary which analyses are:
  - Primary (pre-specified)
  - Secondary or robustness checks

### Effect Sizes and Reporting

**For Welch, permutation Welch, and Yuen–Welch tests:**
- Always report **estimated mean difference** (or trimmed-mean difference) with 95% confidence intervals
- Provide clear clinical interpretation of effect size

**For rank-based tests (when used):**
- Report **rank-based effect size** (e.g., probability of superiority, Cliff's delta)
- Explain its meaning in simple language

**Emphasize in reporting that robust parametric/permutation methods:**
- Directly target clinically interpretable estimands (mean / robust central tendency)
- Maintain Type I error under heteroscedasticity and moderate deviation from normality
- Often provide greater power than traditional nonparametric tests

**Implementation:**
```r
# Effect size for Welch's t-test
effect_size <- test_welch$estimate[1] - test_welch$estimate[2]
ci_lower <- test_welch$conf.int[1]
ci_upper <- test_welch$conf.int[2]

# Report: "Mean difference = X (95% CI: Y to Z)"
```

---

## Model Assessment - Rules

### Automatic Detection of Outcome Type

**Always detect outcome type before building model:**

1. **Continuous outcomes:**
   - Examples: scales (QoR-40, VAS), lab values (hemoglobin, creatinine), durations (length of stay, procedure time)
   - Characteristics: Numeric, interval or ratio scale, can take any value within range

2. **Binary outcomes:**
   - Examples: yes/no, death/survival, complication/no complication, event/no event
   - Characteristics: Two categories (0/1, yes/no, present/absent)

3. **Time-to-event / survival outcomes:**
   - Examples: time to death, time to complication, time to recovery
   - Characteristics: Time variable + censoring indicator (event occurred or was censored)

### Reporting Model Performance by Outcome Type

#### Continuous Outcomes

**For linear regression, linear mixed models (LMM), and other models predicting continuous Y:**

**Always report:**
- **R²** (coefficient of determination)
- **Adjusted R²** (adjusted for number of predictors)
- **RMSE** (root mean squared error)
- **MAE** (mean absolute error)
- **AIC** (Akaike Information Criterion)
- **BIC** (Bayesian Information Criterion)

**Interpretation:**
- **Higher is better**: R², Adjusted R²
- **Lower is better**: RMSE, MAE, AIC, BIC
- R² indicates proportion of variance explained
- Adjusted R² penalizes for model complexity
- RMSE and MAE indicate average prediction error
- AIC/BIC balance fit and complexity (lower = better balance)

#### Binary Outcomes

**For logistic regression, classification models, and other models predicting binary Y:**

**Always report:**
- **AUC (ROC)** with 95% confidence interval
- **Brier score**
- **Calibration intercept** and **calibration slope**
- **AIC** and **BIC**
- **One pseudo-R²** (e.g., Nagelkerke R²), clearly labeled as "pseudo-R²"

**For rare outcomes (event rate < 15–20%):**
- ALSO consider **Precision–Recall AUC (PR-AUC)**, if technically feasible
- PR-AUC may be more informative than ROC-AUC for imbalanced data

**For clinically relevant decision thresholds:**
- Report at least one clinically relevant decision threshold (selected or specified by user):
  - **Sensitivity** (true positive rate)
  - **Specificity** (true negative rate)
  - **PPV** (positive predictive value)
  - **NPV** (negative predictive value)

**Textual summary required:**
- **Discrimination**: How well model separates those with and without event (measured by AUC, PR-AUC)
- **Calibration**: How close predicted probabilities are to observed outcomes (measured by Brier score, calibration slope/intercept)

**Calibration assessment:**
- Hosmer–Lemeshow test is **optional** and, if used, **MUST NOT** be only calibration assessment
- Prefer calibration plots and calibration slope/intercept

#### Time-to-Event / Survival Outcomes

**For Cox proportional hazards models and other survival models:**

**Always report:**
- **Harrell's C-index** (concordance index) with 95% confidence interval
- **AIC** and **BIC** for model comparison

**If technically feasible, also report:**
- **Time-dependent AUC** at clinically relevant time points (e.g., 28 days, 90 days), OR
- **Integrated Brier score (IBS)** over specified time horizon

**Textual interpretation needed:**
- Explain what C-index means (e.g., "probability that patient who dies earlier has higher predicted risk than one who dies later")
- C-index = 0.5 means random prediction, C-index = 1.0 means perfect discrimination

---

## Deep learning and machine learning in study projects

This section complements the test-selection hierarchy in `.cursor/rules/statistics-test-selection.mdc`. Agent-rules **orchestrates**; **models train in the study workspace**.

### When DL/ML is appropriate

Use deep learning (or broader ML) when the **analysis plan** explicitly defines a **prediction, classification, or representation-learning** task and inputs are not well served by closed-form inference alone:

- Medical imaging, waveforms, video, or long unstructured text (after OCR if needed)
- Very high-dimensional tabular data with pre-specified validation (nested CV, temporal split, external cohort)
- Secondary exploratory models **clearly labeled** as non-primary

### When to stay with classical / Bayesian inferential methods

- Confirmatory hypothesis tests on tabular RCT or cohort data
- Meta-analysis pooled effects, meta-regression, standard survival primary analysis
- Small n where interpretability and reporting guidelines (effect + 95% CI) dominate
- Any case where DL would replace a simple pre-registered test without SAP amendment

### Mandatory workflow if DL is in scope

1. **SAP / protocol** — outcome, input modality, metrics (AUC/C-index **and** calibration), split strategy, baseline model
2. **Baseline first** — logistic regression, Cox, or simpler ML before deep models (`50_ml_mlops_standards.mdc`)
3. **Validation** — nested CV for tuning; group/temporal splits for clustered or longitudinal data; no leakage from test set
4. **Reporting** — SPIRIT-AI/CONSORT-AI when applicable; model card, subgroup performance, limitations
5. **Artifacts** — code under study `02_analysis/ml/` or `models/`; weights gitignored or DVC; not committed to agent-rules brain

### R vs Python

- **R (default inferential):** tidyverse, metafor, survival, brms — see sections above
- **Python DL/ML:** PyTorch, sklearn, statsmodels — study venv; skill `statsmodels-python` for classical Python inference only
- **OCR / library RAG:** brain tools (`PADDLEPADDLE.md`, `BOOKS_RAG.md`), not study outcomes

### Brain assist (not training)

- Skill routing: `40_operations/scripts/skill_rerank.py`
- Past error patterns: `40_operations/scripts/similar_errors.py`
- Policy: `30_system/docs/DEEP_LEARNING_POLICY.md`

---

## Methodology extensions (2020–2025)

For analyses involving **ML/MLOps**, **causal inference**, or **Bayesian workflow**, use the following references. Cursor loads the corresponding `.cursor/rules` when globs match; full reference material is in behavior_rules and SKILLs.

- **ML/MLOps production (including deep learning when protocol-appropriate):** Nested CV, calibration, FDA GMLP, feature engineering, DL training defaults. See `30_system/behavior_rules/18_ml_production.md`, `.cursor/rules/50_ml_mlops_standards.mdc`, and `30_system/docs/DEEP_LEARNING_POLICY.md`.
- **Causal inference:** Target trial emulation, DAGs, propensity scores, doubly robust estimation. See `30_system/behavior_rules/20_modern_causal_methods.md`, `.cursor/rules/52_causal_inference.mdc`, and `30_system/SKILLS/SKILL_target-trial-emulation.md`.
- **Bayesian workflow:** Prior/posterior predictive checks, convergence (Rhat, ESS), LOO-CV. See `.cursor/rules/53_bayesian_workflow.mdc` and `30_system/SKILLS/SKILL_bayesian-workflow.md`.

---

## References

See `methodology_repository/` for detailed methodology and citations:
- `01_meta_analysis_methodology.md` - Core meta-analysis methodology
- `02_effect_size_selection.md` - Guidelines for effect size selection
- `03_heterogeneity_assessment.md` - Heterogeneity assessment
- `04_publication_bias_assessment.md` - Methods for publication bias assessment
- `05_sensitivity_analysis.md` - Sensitivity analysis guidelines
- `07_meta_regression.md` - Meta-regression guidelines
- `08_medical_statistics_standards.md` - Medical statistics standards
- `09_prisma_grade_standards.md` - PRISMA and GRADE standards

### Key Guidelines
- PRISMA 2020 (Page et al., 2021)
- Cochrane Handbook for Systematic Reviews of Interventions
- CONSORT for randomized trials
- STROBE for observational studies
- GRADE approach for evidence quality

---

**Version:** 2.2  
**Last updated:** 2026-05-24

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
