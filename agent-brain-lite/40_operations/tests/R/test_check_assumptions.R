# =============================================================================
# tests/R/test_check_assumptions.R – testthat for R/shared/check_assumptions.R
# =============================================================================
# Run from project root: testthat::test_dir("tests/R") or testthat::test_file("tests/R/test_check_assumptions.R")
# =============================================================================

if (!requireNamespace("testthat", quietly = TRUE)) {
  message("Install testthat: install.packages('testthat')")
  quit(save = "no", status = 1)
}

# Source from project root (parent of tests/)
root <- if (dir.exists("R")) getwd() else if (dir.exists("../R")) ".." else "."
source(file.path(root, "R", "shared", "check_assumptions.R"), local = FALSE)

test_that("check_assumptions detects missing data", {
  data <- data.frame(outcome = c(1:10, NA, NA, 13:20), group = rep(c("A", "B"), 10))
  result <- check_assumptions(data, "outcome", "group", test = "t_test")
  expect_equal(result$missing$n_missing, 2)
  expect_equal(result$missing$pct_missing, 10)
})

test_that("check_assumptions runs without group for regression", {
  data <- data.frame(outcome = rnorm(50))
  result <- check_assumptions(data, "outcome", test = "regression")
  expect_true(!is.null(result$missing))
  expect_true(!is.null(result$normality))
  expect_true(!is.null(result$recommended_test))
})

test_that("check_assumptions returns assumption_check class", {
  data <- data.frame(outcome = rnorm(30), group = rep(c("A", "B"), 15))
  result <- check_assumptions(data, "outcome", "group", test = "t_test")
  expect_s3_class(result, "assumption_check")
})

test_that("check_assumptions sample_size recommendation for small groups", {
  data <- data.frame(outcome = rnorm(12), group = rep(c("A", "B"), 6))
  result <- check_assumptions(data, "outcome", "group", test = "t_test")
  expect_true(grepl("small|Small|bootstrapping", result$sample_size$recommendation))
})

test_that("recommend_test is included in output", {
  data <- data.frame(outcome = rnorm(50), group = rep(c("A", "B"), 25))
  result <- check_assumptions(data, "outcome", "group", test = "t_test")
  expect_true(is.character(result$recommended_test))
  expect_true(nchar(result$recommended_test) > 0)
})
