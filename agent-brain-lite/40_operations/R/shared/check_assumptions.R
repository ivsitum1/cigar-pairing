# =============================================================================
# check_assumptions.R – Check statistical assumptions for common tests
# =============================================================================
# Usage: source("R/shared/check_assumptions.R")
#   result <- check_assumptions(data, "outcome", "group", test = "t_test")
# =============================================================================

#' Check statistical assumptions for common tests
#'
#' @param data data.frame
#' @param outcome character – outcome variable name
#' @param group character – grouping variable name (optional, for group comparisons)
#' @param test character – planned test type
#' @return list with results, recommendations, and recommended test
#' @export
check_assumptions <- function(data, outcome, group = NULL,
                              test = c("t_test", "anova", "regression",
                                       "chi_square", "survival")) {
  test <- match.arg(test)
  results <- list()

  # 1. Missing data assessment
  results$missing <- list(
    n_missing = sum(is.na(data[[outcome]])),
    pct_missing = mean(is.na(data[[outcome]])) * 100,
    pattern = if (requireNamespace("naniar", quietly = TRUE)) {
      tryCatch(naniar::miss_var_summary(data), error = function(e) "Install naniar for detailed missing data patterns")
    } else {
      "Install naniar for detailed missing data patterns"
    }
  )

  # 2. Normality (for parametric tests)
  if (test %in% c("t_test", "anova", "regression")) {
    x <- stats::na.omit(data[[outcome]])
    n <- length(x)

    shapiro_result <- if (n >= 3 && n <= 5000) {
      tryCatch(stats::shapiro.test(x), error = function(e) list(p.value = NA, statistic = NA))
    } else {
      "N too large for Shapiro-Wilk"
    }

    skewness_val <- if (requireNamespace("moments", quietly = TRUE)) {
      tryCatch(moments::skewness(x), error = function(e) NA)
    } else NA
    kurtosis_val <- if (requireNamespace("moments", quietly = TRUE)) {
      tryCatch(moments::kurtosis(x), error = function(e) NA)
    } else NA

    results$normality <- list(
      shapiro = shapiro_result,
      skewness = skewness_val,
      kurtosis = kurtosis_val,
      n = n,
      recommendation = if (n >= 30) {
        "N>=30: CLT applies for means. Check residuals if regression."
      } else {
        "N<30: Normality assumption critical. Consider non-parametric."
      }
    )
  }

  # 3. Homoscedasticity (for group comparisons)
  if (!is.null(group) && test %in% c("t_test", "anova")) {
    fmla <- stats::as.formula(paste(outcome, "~ as.factor(", group, ")"))
    levene_result <- if (requireNamespace("car", quietly = TRUE)) {
      tryCatch(car::leveneTest(fmla, data = data), error = function(e) list(`Pr(>F)` = c(NA, NA)))
    } else {
      list(`Pr(>F)` = c(NA, NA), note = "Install car for Levene test")
    }
    p_levene <- if (is.data.frame(levene_result) && "Pr(>F)" %in% names(levene_result)) {
      levene_result$`Pr(>F)`[1]
    } else {
      NA
    }
    results$homoscedasticity <- list(
      levene = levene_result,
      p_value = p_levene,
      recommendation = "If violated: use Welch's test (default) or robust methods"
    )
  }

  # 4. Sample size adequacy
  if (!is.null(group)) {
    group_ns <- table(data[[group]])
    min_n <- min(group_ns)
    results$sample_size <- list(
      per_group = group_ns,
      min_group = min_n,
      balanced = max(group_ns) / min_n < 1.5,
      recommendation = if (min_n < 10) {
        "Very small group. Consider exact tests or bootstrapping."
      } else if (min_n < 30) {
        "Small group. Welch + non-parametric sensitivity analysis."
      } else {
        "Adequate sample size for parametric methods."
      }
    )
  }

  # 5. Test recommendation
  results$recommended_test <- recommend_test(results, test)

  class(results) <- "assumption_check"
  results
}

recommend_test <- function(checks, planned_test) {
  issues <- character()

  if (!is.null(checks$normality)) {
    sh <- checks$normality$shapiro
    if (is.list(sh) && !is.na(sh$p.value) && sh$p.value < 0.05) {
      issues <- c(issues, "non-normal")
    }
  }
  if (!is.null(checks$homoscedasticity)) {
    pv <- checks$homoscedasticity$p_value
    if (!is.na(pv) && pv < 0.05) {
      issues <- c(issues, "heteroscedastic")
    }
  }

  if (length(issues) == 0) {
    paste("Planned", planned_test, "is appropriate. Use Welch variant as default.")
  } else {
    paste("Issues:", paste(issues, collapse = ", "),
          "-> Primary: Welch/robust method. Sensitivity: non-parametric.")
  }
}
