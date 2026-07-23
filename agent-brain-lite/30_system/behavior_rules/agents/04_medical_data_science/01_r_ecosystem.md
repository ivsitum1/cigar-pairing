# R Ecosystem for Medical Data Science

## Core R Packages

```
DATA MANIPULATION:
- tidyverse (dplyr, tidyr, purrr, stringr)
- data.table (for large datasets >1M rows)

STATISTICS:
- brms, rstanarm (Bayesian)
- survival, survminer (time-to-event)
- lme4, nlme (mixed models)
- MatchIt, WeightIt (causal inference)

VISUALIZATION:
- ggplot2 (primary)
- ggstatsplot (statistical tests with ggplot2; effect sizes, CIs)
- patchwork (composite plots)
- gganimate (animations)
- plotly (interactive)

TABLES:
- gtsummary (descriptive + regression tables)
- flextable, officer (Word/PowerPoint export)
- kableExtra (HTML/LaTeX tables)

REPORTING:
- rmarkdown, quarto
- papaja (APA-style manuscripts)
- bookdown (long documents)
```

## Code Style Guide (MANDATORY)

### Naming Conventions

```r
# VARIABLES: snake_case
patient_age <- 65
qor_40_score <- 152

# FUNCTIONS: verb_noun format
calculate_sample_size <- function() {}
clean_missing_data <- function() {}

# CONSTANTS: SCREAMING_SNAKE_CASE
ALPHA_LEVEL <- 0.05
MCID_QOR40 <- 6.3

# DATA FRAMES: descriptive nouns
patients_raw <- read_csv()
patients_clean <- patients_raw %>% filter()
analysis_cohort <- patients_clean %>% select()
```

### File Organization

```
project/
├── data/
│   ├── 00_inbox/raw/                    # Never modify
│   ├── processed/              # Cleaned, analysis-ready
│   └── external/               # Reference data
├── 40_operations/scripts/
│   ├── 01_data_import.R
│   ├── 02_data_cleaning.R
│   ├── 03_descriptive_stats.R
│   ├── 04_primary_analysis.R
│   └── 99_functions.R          # Custom functions
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── models/                 # Saved model objects
├── 30_system/docs/
│   ├── analysis_plan.md
│   └── codebook.md
├── renv/                       # Package management
└── project_name.Rproj
```

### Script Header Template

```r
#===============================================================================
# PROJECT: [Study name - SPECIFY FOR THIS PROJECT]
# SCRIPT: [Purpose - SPECIFY FOR THIS SCRIPT]
# AUTHOR: Ivan Bandić
# DATE: [Current date]
# UPDATED: [Date of last modification]
#
# DESCRIPTION:
# [2-3 sentences describing what this script does - SPECIFY FOR THIS PROJECT]
#
# INPUTS:
# - [Specify actual input files for THIS project]
#
# OUTPUTS:
# - [Specify actual output files for THIS project]
#
# DEPENDENCIES:
# - [List packages with versions used in THIS project]
#===============================================================================

# SETUP ----
## Set working directory
library(here)
PROJECT_ROOT <- here()
setwd(PROJECT_ROOT)

## Load packages
library(tidyverse)
# [Add other packages as needed for THIS project]

## Set options
options(
  scipen = 999,
  digits = 3,
  stringsAsFactors = FALSE
)

## Set seed for reproducibility
set.seed(20250107)  # CHANGE THIS to project-specific seed

# LOAD DATA ----
# data_raw <- read_rds(file.path(PROJECT_ROOT, "data/processed/dataset.rds"))

# [Rest of script - project-specific code]

# SESSION INFO ----
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
sessionInfo()
```

### Project-Specific Code Rules (CRITICAL)

**MANDATORY:** When generating code for a NEW project, it must be completely independent and not contain any hardcoded values from previous projects.

#### ❌ DO NOT DO THIS:
```r
# ❌ BAD: Copying constants from previous project (PSIOS)
MCID <- 6.3          # This is specific to PSIOS project!
POWER <- 0.80        # May not be relevant to new project
data_raw <- read_rds("data/processed/psios_clean.rds")  # Wrong project!
```

#### ✅ DO THIS INSTEAD:
```r
# ✅ GOOD: Project-agnostic template
ALPHA <- 0.05        # Standard significance level (OK - universal)
# MCID <- X.X        # Only define if THIS project uses MCID
# POWER <- 0.80      # Only define if THIS project needs power calculations

# Load data specific to THIS project
data_raw <- read_rds(file.path(PROJECT_ROOT, "data/processed/[THIS_PROJECT]_clean.rds"))
```

#### Rules for Constants:

1. **Universal constants** (OK to include):
   - `ALPHA <- 0.05` (standard significance level)
   - `set.seed()` with project-specific value

2. **Project-specific constants** (define ONLY if relevant):
   - MCID values (only if this project uses MCID)
   - Power calculations (only if this project needs them)
   - Effect sizes (only if predefined for this project)
   - Sample sizes (only if fixed for this project)

3. **Data files** (MUST be project-specific):
   - Never use file names from previous projects
   - Use placeholders: `[PROJECT_NAME]_clean.rds`
   - Or ask: "What is the actual data file name for this project?"

### Path Management Rules (CRITICAL)

**MANDATORY:** When generating R code, ALWAYS set up paths so code runs independently in RStudio.

1. **Set PROJECT_ROOT variable at start of every script (use here::here()):**
```r
library(here)
PROJECT_ROOT <- here()
setwd(PROJECT_ROOT)

# ALTERNATIVE: Manual path (if here::here() doesn't work)
# PROJECT_ROOT <- "C:/path/to/your/project"
# setwd(PROJECT_ROOT)
```

2. **Use file.path() for all file operations:**
```r
# ✅ GOOD: Use PROJECT_ROOT with file.path()
data_path <- file.path(PROJECT_ROOT, "data", "processed", "dataset.rds")
output_path <- file.path(PROJECT_ROOT, "outputs", "tables", "table1.csv")

# ❌ BAD: Hardcoded absolute paths
data_path <- "C:/Users/Admin/OneDrive/Dokumenti/agent rules/data/processed/dataset.rds"
```

### Function Documentation

```r
#' Calculate Propensity Scores
#'
#' Estimates propensity scores using logistic regression for a binary treatment.
#'
#' @param data Data frame containing treatment and covariates
#' @param treatment Character string naming the treatment variable (0/1)
#' @param covariates Character vector of covariate names
#' @param method Method for propensity score estimation: "logit" (default) or "probit"
#'
#' @return Data frame with original data plus propensity score column
#'
#' @examples
#' ps_data <- calculate_propensity_score(
#'   data = trial_data,
#'   treatment = "group",
#'   covariates = c("age", "sex", "asa_score")
#' )
#'
#' @export
calculate_propensity_score <- function(data, treatment, covariates, method = "logit") {
  
  # Input validation
  stopifnot(
    is.data.frame(data),
    treatment %in% names(data),
    all(covariates %in% names(data))
  )
  
  # Build formula
  formula_ps <- as.formula(
    paste(treatment, "~", paste(covariates, collapse = " + "))
  )
  
  # Fit model
  model_ps <- glm(
    formula_ps,
    data = data,
    family = binomial(link = method)
  )
  
  # Calculate propensity scores
  data$propensity_score <- predict(model_ps, type = "response")
  
  return(data)
}
```

## Package Management (renv)

```r
# INITIALIZE PROJECT
renv::init()

# SNAPSHOT CURRENT STATE
renv::snapshot()

# RESTORE FROM LOCKFILE
renv::restore()

# UPDATE PACKAGES
renv::update()

# CHECK STATUS
renv::status()
```

## Performance Optimization

### Vectorization > Loops

```r
# BAD (slow)
results <- numeric(length(x))
for (i in seq_along(x)) {
  results[i] <- x[i]^2 + 2*x[i] + 1
}

# GOOD (fast)
results <- x^2 + 2*x + 1

# data.table for large data (>1M rows)
library(data.table)

dt <- as.data.table(data_large)

# Fast aggregation
dt[, .(mean_age = mean(age)), by = treatment_group]

# Fast filtering
dt[age > 65 & asa_score %in% c("III", "IV")]
```

### Parallel Processing

```r
library(furrr)

# Setup parallel backend
plan(multisession, workers = 4)

# Parallel map
results <- future_map(
  1:1000,
  ~simulate_trial(.x),
  .options = furrr_options(seed = TRUE),
  .progress = TRUE
)
```

## Related Hubs

- [Folder index hub](../../../docs/FOLDER_INDEX.md)
- [All notes index](../../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../docs/GRAPH_CONNECTIVITY_MAP.md)
