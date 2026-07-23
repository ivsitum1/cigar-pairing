> **⚠️ MIGRATED** -> `.cursor/rules/python_r_code_always.mdc` (2026-05-08)

# R Programming - Detailed Rules

## Purpose

This document contains detailed, R-specific rules and best practices for AI agents working with R code. These rules are critical for avoiding common errors and ensuring code quality.

**Related Knowledge Base:**
- `20_knowledge/reference_library/statistics/knowledge_bases/medical_data_science_laboratory.md` — Complete R ecosystem and package recommendations (Layers 0-15)

---

## Complete R Statistical Workflow Protocol (MANDATORY)

**Agent must follow steps in order and explicitly document assumptions, limitations, and decisions.**

### Step 0: General Principles

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

### Step 1: Data Loading and Initial Review

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

### Step 2: Exploratory Data Analysis (EDA) - FlexPlot-First

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

### Step 3: Missing Data - Assessment and Handling

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
```

**MANDATORY checks:**
- Justify MAR assumption
- Check convergence
- Report imputation method and m (number of imputations)

### Step 4: Hypothesis Testing - Frequentist Approach

**Preference: Parametric tests**
- t-test / Welch t-test
- ANOVA / linear models

**Robust parametric approaches:**
If assumptions not satisfied:
- Permutation Welch t-test

```r
library(coin)
oneway_test(outcome ~ group, data = df, distribution = approximate(B = 10000))
```

**Do NOT use classical non-parametric tests without clear reason.**

### Step 5: Bootstrap (MANDATORY for Effect Size and CI)

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
- Confidence intervals
- Stability of estimates

### Step 6: Hypothesis Analysis by Model Comparison

**Mixed models (full vs reduced):**
```r
library(lme4)

model_full <- lmer(outcome ~ exposure + cov1 + cov2 + (1 | subject), data = df)
model_reduced <- lmer(outcome ~ cov1 + cov2 + (1 | subject), data = df)

anova(model_reduced, model_full)
```

**Tests incremental value of hypothesis, not just coefficient.**

### Step 7: Defining Controlling Variables (Confounders)

- Define **a priori**, by clinical logic
- Do NOT select variables solely by p-value

**Examples:**
- Age
- Sex
- Baseline values
- Disease severity

**Controlling variables must ALWAYS be included in models**, even if not statistically significant.

### Step 8: Multiple Comparisons - Corrections (MANDATORY)

If >1 hypothesis:

- Holm (preferred)
- Benjamini-Hochberg (FDR) for exploratory analyses

```r
p.adjust(p_values, method = "holm")
```

**Without correction → analysis is methodologically invalid.**

### Step 9: Bayesian Approach to Hypothesis Testing

**Use when:**
- Sample size small
- Prior knowledge exists
- Clinical interpretation more important than binary decision

```r
library(brms)

bayes_model <- brm(
  outcome ~ exposure + cov1 + cov2,
  data = df,
  family = gaussian(),
  prior = set_prior("normal(0, 1)", class = "b"),
  chains = 4, iter = 4000, seed = 123
)
```

**Report:**
- Posterior distribution
- Credible intervals
- Posterior probability of clinically relevant effect

### Step 10: Visualization of Results (Final)

- Forest plot for models
- Posterior density plot (Bayesian)
- Predicted vs observed

**Graph must answer:**
> "What does this change in clinical decision?"

### Step 11: Additional Recommendations / Workflow Enhancement

**Recommended additions:**
- Sensitivity analysis (different outcome definitions)
- Internal validation (bootstrap optimism correction)
- Model diagnostics (residuals, influence)
- Pre-registration of analysis logic (SPIRIT / SAP mindset)

**Forbidden:**
- p-hacking
- Stepwise selection without clinical logic
- Cherry-picking graphs

---

## Model Selection Decision Tree

```
DATA_TYPE:
├── Continuous outcome
│   ├── Normal dist → Linear regression
│   ├── Non-normal → GLM / Robust regression
│   └── Clustered → Mixed models (lme4)
├── Binary outcome → Logistic regression
├── Count data
│   ├── Poisson (if mean ≈ variance)
│   └── Negative binomial (overdispersion)
├── Time-to-event → Cox PH / AFT
└── Ordinal → Ordinal logistic (MASS::polr)
```

**Use FlexPlot to visually verify relationships before selecting model type.**

---

## R Code Style Mandates

### Pipe Operator

- **Default**: use native R pipe `|>` (requires R ≥ 4.1)
- **Exception**: use magrittr `%>%` only when the `.` placeholder is needed for argument position
- **Never**: use pipes in function definitions that will be exported to packages
- **Chain length**: max 10 steps in a single pipe chain. If longer, assign intermediate results
  with descriptive variable names to aid debugging.

Example of correct usage:

```r
# Native pipe — preferred
result <- data |> filter(age > 18) |> mutate(bmi = weight / height^2) |> summarise(mean_bmi = mean(bmi))

# Magrittr only when . placeholder needed
result <- data %>% lm(outcome ~ ., data = .)
```

### Vectorization (CRITICAL)

**RULE: ALWAYS prefer vectorized operations over loops**

```r
# ❌ BAD - growing vector in loop
result <- c()
for (i in 1:length(x)) {
  result <- c(result, x[i] * 2)  # NEVER do this
}

# ✅ GOOD - vectorized
result <- x * 2  # Vectorized

# ✅ GOOD - for more complex operations, use apply family
result <- sapply(x, function(val) val * 2)
# OR even better:
result <- x * 2  # If possible, direct vectorization
```

**Why this is critical:**
- Growing vectors in loops are extremely slow
- Vectorized operations use optimized C code
- More readable and shorter code

### Data Structures

**RULE: Use tibble instead of data.frame for all new code**

**Reason:**
- Consistent printing (doesn't print all rows)
- No automatic type conversion (strings stay strings, not factors)
- Better error messages
- Compatible with tidyverse ecosystem

**Implementation:**
```r
library(tibble)

# ✅ GOOD
df <- tibble(
  id = 1:10,
  name = c("a", "b", "c", ...)  # Stays character, not factor
)

# ❌ BAD (unless necessary)
df <- data.frame(
  id = 1:10,
  name = c("a", "b", "c", ...)  # May become factor
)
```

### Namespace Conflicts (CRITICAL)

**RULE: ALWAYS use explicit namespacing for conflicting functions**

**Common conflicts:**

| Function | Conflict between |
|----------|----------------|
| `filter` | `dplyr::filter()` vs `stats::filter()` |
| `select` | `dplyr::select()` vs `MASS::select()` |
| `lag` | `dplyr::lag()` vs `stats::lag()` |
| `map` | `purrr::map()` vs `maps::map()` |
| `extract` | `tidyr::extract()` vs `magrittr::extract()` |

**Solution 1: Explicit namespacing**
```r
# Always use explicitly
dplyr::filter(data, condition)
dplyr::select(data, columns)
```

**Solution 2: conflict_prefer (at script start)**
```r
library(conflicted)
conflict_prefer("filter", "dplyr")
conflict_prefer("select", "dplyr")
conflict_prefer("lag", "dplyr")
```

**Solution 3: Explicit loading with namespace**
```r
# At script start
library(dplyr)
library(MASS)
# Then use dplyr::filter() when needed
```

### Factor Handling (CRITICAL)

**RULE: NEVER rely on automatic factor conversion**

**Problem:**
- Base R (pre-4.0) automatically converts strings to factors
- Tibble never converts
- Models require explicit factors with defined levels

**Verification before modeling:**
```r
# Check that variable is factor
stopifnot(is.factor(df$treatment))

# Check that levels are correct
stopifnot(all(levels(df$treatment) %in% c("Control", "Treatment")))
```

**Explicit factor creation:**
```r
# ✅ GOOD - explicit factor creation
df$treatment <- factor(df$treatment, 
                       levels = c("Control", "Treatment"))

# OR with ordered factors
df$severity <- ordered(df$severity, 
                       levels = c("Mild", "Moderate", "Severe"))
```

---

## R Code Quality Checklist

**BEFORE COMMITTING R CODE, check:**

```yaml
BEFORE_COMMITTING_R_CODE:
  □ No hardcoded file paths (use here::here() or config)
  □ All packages loaded at top with library()
  □ No library() calls inside functions
  □ Seeds set for all stochastic operations
  □ Explicit namespacing for conflicting functions
  □ No growing vectors in loops
  □ Proper NA handling (na.rm = TRUE where appropriate)
  □ Factor levels explicitly defined
  □ Character encoding resolved (UTF-8 default)
  □ Memory-efficient for large datasets (data.table for >1M rows)
```

### Package Version Documentation

**ALWAYS document package versions for reproducibility:**

```r
# ALWAYS document package versions for reproducibility
session_info <- function() {
  cat("=== SESSION INFO ===\n")
  cat("Date:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
  cat("R version:", R.version.string, "\n")
  cat("Platform:", R.version$platform, "\n")
  cat("\n=== KEY PACKAGES ===\n")
  
  key_packages <- c("tidyverse", "brms", "rstanarm", "lme4", 
                    "survival", "caret", "mlr3", "data.table", 
                    "meta", "metafor")
  
  for (pkg in key_packages) {
    if (requireNamespace(pkg, quietly = TRUE)) {
      cat(sprintf("%s: %s\n", pkg, packageVersion(pkg)))
    }
  }
}

# Call at end of analysis scripts
session_info()
```

### Automatic Reproducibility Setup

**When generating R analysis code, ALWAYS include:**

1. **renv setup** (if project doesn't have it):
```r
# Check and initialize renv
if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv")
}
if (!file.exists("renv/renv.lock")) {
  renv::init()
  renv::snapshot()
}
renv::activate()
```

2. **Session info saving** (at end of every script):
```r
# Save session info for reproducibility
# Use here::here() to automatically find project root
library(here)
PROJECT_ROOT <- here()
# Alternative: Manual path if here::here() doesn't work
# PROJECT_ROOT <- "C:/path/to/your/project"  # CHANGE THIS

session_dir <- file.path(PROJECT_ROOT, "session_info")
if (!dir.exists(session_dir)) dir.create(session_dir, recursive = TRUE)
session_file <- file.path(session_dir, paste0("session_info_", format(Sys.Date(), "%Y%m%d"), ".txt"))
sink(session_file)
cat("=== SESSION INFO ===\n")
cat("Date:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("R version:", R.version.string, "\n")
cat("Platform:", R.version$platform, "\n")
cat("Working directory:", getwd(), "\n")
print(sessionInfo(), locale = FALSE)
sink()
sessionInfo()  # Also print to console
```

3. **Path handling** (use here::here() for flexible paths):
```r
# CRITICAL: Use here::here() to automatically find project root
# This works when "agent rules" folder is copied to new project locations
library(here)
PROJECT_ROOT <- here()
setwd(PROJECT_ROOT)

# Alternative: Manual path if here::here() doesn't work
# PROJECT_ROOT <- "C:/path/to/your/project"  # CHANGE THIS to actual project path
# setwd(PROJECT_ROOT)

# Use file.path() for all file operations
data_path <- file.path(PROJECT_ROOT, "data", "processed", "dataset.rds")
output_path <- file.path(PROJECT_ROOT, "outputs", "tables", "table1.csv")

# NOTE: When copying "agent rules" folder to a new project location:
# - If .Rproj file exists, here::here() will automatically detect the new location
# - Otherwise, manually set: PROJECT_ROOT <- "path/to/new/project"
# - All reviewers should know how to set paths in R using setwd()
```

**Note:** Do NOT generate Docker files. Use renv + documentation instead.

---

## Common R Pitfalls to Avoid

### PITFALL 1: StringsAsFactors

**Problem:** Base R converts strings to factors by default (pre-4.0)

**Prevention:**
```r
# Option 1: Global setting
options(stringsAsFactors = FALSE)  # Global setting

# Option 2: Use tibble (recommended)
library(tibble)
df <- tibble(name = c("a", "b", "c"))  # Stays character
```

### PITFALL 2: Partial Matching

**Problem:** R matches partial argument names

**Prevention:**
```r
# ❌ BAD: df$val matches df$value
df$val

# ✅ GOOD: Use exact names or [["column"]]
df[["value"]]  # Exact match only
df$value  # If sure it exists
```

### PITFALL 3: Drop Dimension

**Problem:** Selecting one column returns vector instead of data.frame

**Prevention:**
```r
# ❌ BAD: df[, 1] returns vector
df[, 1]

# ✅ GOOD: df[, 1, drop = FALSE] keeps data.frame
df[, 1, drop = FALSE]

# ✅ BEST: Use tibble which never drops
library(tibble)
df[, 1]  # Stays tibble
```

### PITFALL 4: Recycling

**Problem:** R silently recycles shorter vectors

**Prevention:**
```r
# Always verify lengths match
stopifnot(length(x) == length(y))

# OR use vctrs package for strict recycling
library(vctrs)
vec_recycle_common(x, y)
```

### PITFALL 5: Growing Vectors in Loops

**Problem:** Growing vectors in loops are extremely slow

**Prevention:**
```r
# ❌ BAD - growing vector
result <- c()
for (i in 1:1000) {
  result <- c(result, i * 2)
}

# ✅ GOOD - pre-allocate
result <- numeric(1000)
for (i in 1:1000) {
  result[i] <- i * 2
}

# ✅ BEST - vectorize
result <- (1:1000) * 2
```

---

## R-Specific Best Practices

### Memory Efficiency

**For large datasets (>1M rows):**
- Use `data.table` instead of `data.frame` or `tibble`
- Use `fread()` instead of `read.csv()` for faster loading
- Use `fwrite()` instead of `write.csv()` for faster writing

```r
library(data.table)

# Faster loading
dt <- fread("large_file.csv")

# Faster writing
fwrite(dt, "output.csv")
```

### Reproducibility

**ALWAYS set seed for stochastic operations:**
```r
set.seed(42)  # Or any other seed
# ... stochastic operations ...
```

**Document package versions:**
```r
# At script start
# R version: 4.3.0
# tidyverse: 2.0.0
# meta: 6.5-0
```

### Error Handling

**Use tryCatch for graceful error handling:**
```r
result <- tryCatch({
  # Code that may throw error
  risky_operation()
}, error = function(e) {
  # What to do if error occurs
  warning("Operation failed: ", e$message)
  return(NULL)  # OR default value
})
```

---

## R Code Templates

### Standard File Header

```r
# =============================================================================
# File: [filename]
# Purpose: [description]
# Author: [name/AI-assisted]
# Created: [date]
# Updated: [date]
# Dependencies: [package list]
# =============================================================================

# =============================================================================
# SETUP
# =============================================================================

library(tidyverse)
library(here)
set.seed(42)

# =============================================================================
# DATA LOADING
# =============================================================================

# ... code ...
```

### Function Template

```r
# =============================================================================
# FUNCTION: [function_name]
# Purpose: [description of what function does]
# Arguments:
#   - arg1: [description]
#   - arg2: [description]
# Returns: [description of what it returns]
# =============================================================================

function_name <- function(arg1, arg2 = default_value) {
  # Input validation
  stopifnot(is.numeric(arg1))
  stopifnot(length(arg1) > 0)
  
  # Main logic
  result <- arg1 * arg2
  
  # Return
  return(result)
}
```

---

**Version:** 2.0  
**Last updated:** 2026-04-10  
**Reference:** CURSOR_AGENT_INSTRUCTIONS (1).md, Section 8

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
