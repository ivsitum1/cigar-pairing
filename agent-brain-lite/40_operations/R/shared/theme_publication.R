# =============================================================================
# theme_publication.R – Publication-ready ggplot2 theme and figure export
# =============================================================================
# Usage: source("R/shared/theme_publication.R"); p + theme_publication()
# =============================================================================

#' Publication-ready ggplot2 theme
#' Follows journal standards: clean, minimal, high-contrast
#'
#' @param base_size numeric
#' @param base_family character (e.g. "Arial")
#' @return theme object
#' @export
theme_publication <- function(base_size = 12, base_family = "sans") {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop("Install ggplot2: install.packages('ggplot2')")
  }
  ggplot2::theme_minimal(base_size = base_size, base_family = base_family) +
    ggplot2::theme(
      plot.title = ggplot2::element_text(
        size = base_size * 1.2, face = "bold",
        hjust = 0, margin = ggplot2::margin(b = 10)
      ),
      plot.subtitle = ggplot2::element_text(
        size = base_size * 0.9,
        margin = ggplot2::margin(b = 15)
      ),
      axis.title = ggplot2::element_text(size = base_size, face = "bold"),
      axis.text = ggplot2::element_text(size = base_size * 0.85),
      legend.title = ggplot2::element_text(size = base_size * 0.9, face = "bold"),
      legend.text = ggplot2::element_text(size = base_size * 0.85),
      panel.grid.major = ggplot2::element_line(color = "grey90", linewidth = 0.3),
      panel.grid.minor = ggplot2::element_blank(),
      legend.position = "bottom",
      legend.box = "horizontal",
      plot.margin = ggplot2::margin(15, 15, 15, 15),
      strip.text = ggplot2::element_text(size = base_size * 0.9, face = "bold")
    )
}

#' Save publication figure with standard dimensions
#'
#' @param plot ggplot object
#' @param filename character (no extension)
#' @param width_cm numeric (default 17 for single column)
#' @param height_cm numeric (default: width * 0.618)
#' @param dpi numeric (default 300)
#' @param format "tiff", "pdf", or "png"
#' @param output_dir optional; default uses here::here("03_output", "figures")
#' @export
save_publication_figure <- function(plot, filename,
                                   width_cm = 17, height_cm = NULL,
                                   dpi = 300, format = c("tiff", "pdf", "png"),
                                   output_dir = NULL) {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop("Install ggplot2")
  }
  format <- match.arg(format)
  if (is.null(height_cm)) height_cm <- width_cm * 0.618

  if (is.null(output_dir)) {
    if (requireNamespace("here", quietly = TRUE)) {
      output_dir <- here::here("03_output", "figures")
    } else {
      output_dir <- file.path(getwd(), "03_output", "figures")
    }
  }
  dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)
  filepath <- file.path(output_dir, paste0(filename, ".", format))

  ggplot2::ggsave(
    filename = filepath,
    plot = plot,
    width = width_cm, height = height_cm, units = "cm",
    dpi = dpi, bg = "white"
  )
  message(sprintf("Saved: %s (%g x %g cm, %d DPI)", filepath, width_cm, height_cm, dpi))
  invisible(filepath)
}

#' Standard color palettes for clinical data
palette_clinical <- list(
  treatment = c(intervention = "#2166AC", control = "#B2182B"),
  outcome = c(positive = "#1B7837", negative = "#762A83"),
  severity = c(
    mild = "#FEE08B", moderate = "#FDAE61",
    severe = "#F46D43", critical = "#D73027"
  ),
  sequential = c("#F7FCF5", "#C7E9C0", "#74C476", "#238B45", "#00441B")
)
