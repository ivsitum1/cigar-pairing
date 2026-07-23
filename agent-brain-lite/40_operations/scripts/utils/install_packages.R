# =============================================================================
# install_packages.R — Documented R package installs for clinical data science
# Idempotent: installs only packages not already present. Safe to re-run.
# Usage: source("scripts/utils/install_packages.R")
# =============================================================================

cran <- "https://cloud.r-project.org"

# Core workspace: DuckDB + tidyverse tooling + paths
core_pkgs <- c(
  "duckdb", "DBI", "tidyverse", "here", "readr", "readxl"
)

# Meta-analysis and Bayesian stack
analysis_pkgs <- c(
  "meta", "metafor", "brms", "bayesplot", "robvis",
  "writexl", "openxlsx", "gtsummary", "flextable"
)

# Modeling, inference, missing data (SKILL_r-statistics tier 2)
stats_modeling_pkgs <- c(
  "MASS", "lme4", "glmmTMB", "mgcv", "car", "emmeans", "marginaleffects",
  "performance", "broom", "broom.mixed", "mice", "naniar", "janitor", "boot"
)

# Survival
stats_survival_pkgs <- c("survival", "survminer", "flexsurv")

# Causal inference (lite)
stats_causal_pkgs <- c("MatchIt", "WeightIt", "cobalt", "EValue")

# Statistical visualization
viz_pkgs <- c("ggstatsplot", "patchwork", "ggpubr")

# Full catalog: 30_system/SKILLS/reference/r_statistics_packages.md (install on demand)

all_pkgs <- unique(c(
  core_pkgs, analysis_pkgs, stats_modeling_pkgs,
  stats_survival_pkgs, stats_causal_pkgs, viz_pkgs
))

# --- Install missing packages silently (no extra noise in logs) ---------------
installed <- rownames(utils::installed.packages())
to_install <- setdiff(all_pkgs, installed)

if (length(to_install)) {
  message("Installing: ", paste(to_install, collapse = ", "))
  utils::install.packages(
    to_install,
    repos = cran,
    quiet = TRUE,
    dependencies = TRUE
  )
} else {
  message("All listed packages are already installed.")
}

# --- Optional: renv snapshot if project uses renv -----------------------------
if (requireNamespace("renv", quietly = TRUE) && file.exists("renv/activate.R")) {
  renv::snapshot(prompt = FALSE)
  message("renv::snapshot() completed.")
} else {
  message("renv not active — skipped snapshot. To use: renv::init() then re-run this script.")
}

invisible(all_pkgs)
