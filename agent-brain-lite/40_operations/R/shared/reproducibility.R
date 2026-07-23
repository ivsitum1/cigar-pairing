# =============================================================================
# reproducibility.R – Standard reproducibility header for analysis scripts
# =============================================================================
# Call at the top of every analysis script.
# Usage: source("R/shared/reproducibility.R"); init_analysis(seed = 42, "MyProject")
# =============================================================================

`%||%` <- function(x, y) if (is.null(x)) y else x

#' Standard reproducibility setup for analysis scripts
#'
#' Sets seed, records session info, creates standard output dirs.
#' Requires 'here' package for project root.
#'
#' @param seed integer – random seed (default 42)
#' @param project_name character – optional project name for log
#' @return invisible list with seed, project_root, session, timestamp
#' @export
init_analysis <- function(seed = 42, project_name = NULL) {
  set.seed(seed)

  if (!requireNamespace("here", quietly = TRUE)) {
    stop("Install 'here' package for init_analysis()")
  }
  project_root <- here::here()

  dirs <- c("01_input", "02_analysis", "03_output", "04_figures", "05_tables")
  for (d in dirs) {
    dir.create(file.path(project_root, d), showWarnings = FALSE, recursive = TRUE)
  }

  session <- utils::sessionInfo()
  cat("Analysis initialized:",
      "\n  Date:", format(Sys.time()),
      "\n  Seed:", seed,
      "\n  R:", paste(R.version$major, R.version$minor, sep = "."),
      "\n  Project:", project_name %||% basename(project_root),
      "\n")

  invisible(list(
    seed = seed,
    project_root = project_root,
    session = session,
    timestamp = Sys.time()
  ))
}
