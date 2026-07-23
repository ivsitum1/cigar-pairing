# =============================================================================
# Paths – project root and raw data (configurable)
# =============================================================================
# Use in RStudio: set project to folder containing .ai/, behavior_rules/, R/
# (e.g. "agent rules"). Then getwd() is project root.
# For statistics: set path_raw_data when you load your data (override below).
# =============================================================================

if (!exists("PROJECT_ROOT") || is.null(PROJECT_ROOT)) {
  PROJECT_ROOT <- getwd()
}

# Default raw data path (relative to project root). Override when loading data:
#   path_raw_data <- "C:/your/path/to/raw"
if (!exists("path_raw_data") || is.null(path_raw_data)) {
  path_raw_data <- file.path(PROJECT_ROOT, "01_input", "data", "raw")
}
