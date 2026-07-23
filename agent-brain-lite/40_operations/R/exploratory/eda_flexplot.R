# =============================================================================
# Visual Exploratory Data Analysis (FlexPlot)
# =============================================================================
# Use after initial EDA (structure, descriptives). Run this script to produce
# distribution and relationship plots. Present results and suggest next-step
# analysis; do not proceed to inferential analysis until user specifies method.
# See SKILL_eda-flexplot.md.
# =============================================================================

set.seed(123)
library(tidyverse)
library(flexplot)

# -----------------------------------------------------------------------------
# Configuration (adjust for your project and dataset)
# -----------------------------------------------------------------------------
# Data path: CSV or RDS. Prefer here::here() for portability.
data_path <- here::here("data", "analysis_dataset.csv")
# If data is in project layout 01_input/ or 02_analysis/:
# data_path <- here::here("01_input", "data", "analysis_dataset.csv")

# Output folder for EDA figures (created if missing)
out_dir <- here::here("03_output", "figures", "eda")
# Alternative: out_dir <- here::here("02_analysis", "figures", "eda")

# Key variables: replace with actual names from your dataset
# outcome   = main outcome (continuous or binary)
# predictor = main grouping or continuous predictor
# covariate = optional second predictor or covariate (can be NULL)
outcome_name   <- "outcome"    # e.g. "score", "sbp", "event"
predictor_name <- "predictor" # e.g. "group", "treatment", "age"
covariate_name <- NULL        # e.g. "sex" or NULL to skip

# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------
if (!file.exists(data_path)) {
  stop("Data file not found: ", data_path,
       ". Set data_path and variable names at top of script.")
}
df <- readr::read_csv(data_path, show_col_types = FALSE)

# -----------------------------------------------------------------------------
# Create output directory
# -----------------------------------------------------------------------------
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# -----------------------------------------------------------------------------
# 1. Distribution of outcome
# -----------------------------------------------------------------------------
if (outcome_name %in% names(df)) {
  p_outcome <- flexplot(
    as.formula(paste(outcome_name, "~ 1")),
    data = df,
    method = "histogram"
  )
  ggplot2::ggsave(
    file.path(out_dir, "eda_outcome_dist.png"),
    p_outcome,
    width = 6,
    height = 4,
    dpi = 150
  )
}

# -----------------------------------------------------------------------------
# 2. Distribution of predictor (if numeric)
# -----------------------------------------------------------------------------
if (predictor_name %in% names(df) && is.numeric(df[[predictor_name]])) {
  p_pred <- flexplot(
    as.formula(paste(predictor_name, "~ 1")),
    data = df,
    method = "histogram"
  )
  ggplot2::ggsave(
    file.path(out_dir, "eda_predictor_dist.png"),
    p_pred,
    width = 6,
    height = 4,
    dpi = 150
  )
}

# -----------------------------------------------------------------------------
# 3. Outcome vs predictor (main relationship)
# -----------------------------------------------------------------------------
if (outcome_name %in% names(df) && predictor_name %in% names(df)) {
  p_rel <- flexplot(
    as.formula(paste(outcome_name, "~", predictor_name)),
    data = df
  )
  ggplot2::ggsave(
    file.path(out_dir, "eda_outcome_vs_predictor.png"),
    p_rel,
    width = 6,
    height = 4,
    dpi = 150
  )
}

# -----------------------------------------------------------------------------
# 4. Outcome ~ predictor + covariate (if provided)
# -----------------------------------------------------------------------------
if (!is.null(covariate_name) &&
    outcome_name %in% names(df) &&
    predictor_name %in% names(df) &&
    covariate_name %in% names(df)) {
  form_3 <- as.formula(paste(outcome_name, "~", predictor_name, "+", covariate_name))
  p_cov <- flexplot(form_3, data = df)
  ggplot2::ggsave(
    file.path(out_dir, "eda_outcome_predictor_covariate.png"),
    p_cov,
    width = 7,
    height = 5,
    dpi = 150
  )
}

# -----------------------------------------------------------------------------
# 5. Optional: distributions of all numeric variables (first N for readability)
# -----------------------------------------------------------------------------
num_vars <- names(df)[vapply(df, is.numeric, logical(1))]
if (length(num_vars) > 0L) {
  n_show <- min(6L, length(num_vars))
  for (v in num_vars[seq_len(n_show)]) {
    p <- flexplot(as.formula(paste(v, "~ 1")), data = df, method = "histogram")
    ggplot2::ggsave(
      file.path(out_dir, paste0("eda_dist_", gsub("[^a-zA-Z0-9_]", "_", v), ".png")),
      p,
      width = 5,
      height = 3,
      dpi = 150
    )
  }
}

message("EDA figures saved to: ", out_dir)
message("Next: present these results and suggest analysis options; pause until user chooses method (see SKILL_eda-flexplot).")
