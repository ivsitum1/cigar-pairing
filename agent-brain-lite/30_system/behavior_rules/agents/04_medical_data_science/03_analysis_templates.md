# Analysis Templates for Medical Data Science

## Data Cleaning Pipeline

```r
# STANDARD CLEANING WORKFLOW

clean_clinical_data <- function(data_raw) {
  
  data_clean <- data_raw %>%
    # 1. Select relevant columns
    select(
      patient_id, age, sex, bmi, asa_score,
      treatment_group, qor_40_baseline, qor_40_day1,
      complications, los_hospital
    ) %>%
    
    # 2. Rename for consistency
    rename(
      qor_baseline = qor_40_baseline,
      qor_day1 = qor_40_day1,
      los = los_hospital
    ) %>%
    
    # 3. Recode variables
    mutate(
      # Binary to logical
      sex = case_when(
        sex == "M" ~ "Male",
        sex == "F" ~ "Female",
        TRUE ~ NA_character_
      ),
      
      # Numeric with range checks
      age = if_else(age >= 18 & age <= 100, age, NA_real_),
      bmi = if_else(bmi >= 15 & bmi <= 60, bmi, NA_real_),
      
      # Factor with explicit levels
      asa_score = factor(
        asa_score,
        levels = c("I", "II", "III", "IV"),
        ordered = TRUE
      ),
      
      # Derived variables
      qor_change = qor_day1 - qor_baseline,
      bmi_category = cut(
        bmi,
        breaks = c(0, 18.5, 25, 30, 100),
        labels = c("Underweight", "Normal", "Overweight", "Obese"),
        right = FALSE
      )
    ) %>%
    
    # 4. Handle missing data
    filter(!is.na(patient_id)) %>%
    filter(!is.na(treatment_group)) %>%
    
    # 5. Remove duplicates
    distinct(patient_id, .keep_all = TRUE) %>%
    
    # 6. Sort
    arrange(patient_id)
  
  # 7. Validation checks
  stopifnot(
    "Duplicate IDs found" = !any(duplicated(data_clean$patient_id)),
    "Invalid ages" = all(data_clean$age >= 18 & data_clean$age <= 100, na.rm = TRUE),
    "Missing treatment groups" = !any(is.na(data_clean$treatment_group))
  )
  
  # 8. Print summary
  cat("Data cleaning complete:\n")
  cat("  Rows:", nrow(data_raw), "→", nrow(data_clean), "\n")
  cat("  Missing outcomes:", sum(is.na(data_clean$qor_day1)), "\n")
  
  return(data_clean)
}

# USAGE
data_clean <- clean_clinical_data(data_raw)
```

## Descriptive Statistics (Table 1)

```r
# PUBLICATION-READY TABLE 1

create_table1 <- function(data, by_var = "treatment_group") {
  
  table1 <- data %>%
    select(
      # Demographics
      age, sex, bmi, bmi_category,
      # Clinical
      asa_score, comorbidities,
      # Surgical
      surgery_duration, blood_loss,
      # Outcomes
      qor_baseline, qor_day1,
      # Grouping
      all_of(by_var)
    ) %>%
    tbl_summary(
      by = all_of(by_var),
      statistic = list(
        all_continuous() ~ "{mean} ({sd})",
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits = list(
        all_continuous() ~ 1,
        all_categorical() ~ c(0, 1)
      ),
      label = list(
        age ~ "Age (years)",
        sex ~ "Sex",
        bmi ~ "BMI (kg/m²)",
        bmi_category ~ "BMI category",
        asa_score ~ "ASA physical status",
        surgery_duration ~ "Surgery duration (min)",
        qor_baseline ~ "QoR-40 baseline",
        qor_day1 ~ "QoR-40 day 1"
      ),
      missing = "no"
    ) %>%
    add_p(
      test = list(
        all_continuous() ~ "t.test",
        all_categorical() ~ "chisq.test"
      )
    ) %>%
    add_overall() %>%
    bold_labels() %>%
    modify_header(
      label ~ "**Characteristic**",
      stat_0 ~ "**Overall**<br>N = {N}",
      stat_1 ~ "**TIVA**<br>n = {n}",
      stat_2 ~ "**Sevoflurane**<br>n = {n}",
      p.value ~ "**P-value**"
    ) %>%
    modify_caption("**Table 1. Baseline Characteristics**")
  
  return(table1)
}

# EXPORT TO WORD
table1 <- create_table1(data_clean)

table1 %>%
  as_flex_table() %>%
  flextable::save_as_docx(
    path = "outputs/tables/table1_baseline.docx"
  )
```

## Primary Analysis Template

```r
# STANDARD ANALYSIS WORKFLOW

analyze_primary_outcome <- function(data, outcome, treatment, covariates) {
  
  # 1. Descriptive statistics by group
  descriptive <- data %>%
    group_by(.data[[treatment]]) %>%
    summarize(
      n = n(),
      mean = mean(.data[[outcome]], na.rm = TRUE),
      sd = sd(.data[[outcome]], na.rm = TRUE),
      median = median(.data[[outcome]], na.rm = TRUE),
      q25 = quantile(.data[[outcome]], 0.25, na.rm = TRUE),
      q75 = quantile(.data[[outcome]], 0.75, na.rm = TRUE)
    )
  
  print(descriptive)
  
  # 2. Descriptive diagnostics only (do NOT use for test selection; see statistics-test-selection.mdc)
  # Requires: moments
  cat("\n=== DESCRIPTIVE DIAGNOSTICS ===\n")
  diag_by_group <- data %>%
    group_by(.data[[treatment]]) %>%
    summarise(
      n = n(),
      skewness = moments::skewness(.data[[outcome]], na.rm = TRUE),
      n_outliers = length(boxplot.stats(.data[[outcome]])$out),
      .groups = "drop"
    )
  print(diag_by_group)
  
  # 3. Primary analysis (linear regression when adjusting for covariates; use Welch/permutation for unadjusted per hierarchy)
  formula_primary <- as.formula(
    paste(outcome, "~", treatment, "+", paste(covariates, collapse = " + "))
  )
  
  model_primary <- lm(formula_primary, data = data)
  
  # 4. Results summary
  cat("\n=== PRIMARY ANALYSIS ===\n")
  summary(model_primary)
  
  # Extract treatment effect
  coef_treatment <- coef(model_primary)[2]
  ci_treatment <- confint(model_primary)[2, ]
  p_treatment <- summary(model_primary)$coefficients[2, 4]
  
  cat("\n=== TREATMENT EFFECT ===\n")
  cat(sprintf(
    "Mean difference: %.2f (95%% CI: %.2f to %.2f), p = %.3f\n",
    coef_treatment, ci_treatment[1], ci_treatment[2], p_treatment
  ))
  
  # 5. Sensitivity analysis (Mann-Whitney as sensitivity only; primary per Welch/permutation hierarchy)
  cat("\n=== SENSITIVITY ANALYSIS ===\n")
  wilcox_test <- wilcox.test(
    as.formula(paste(outcome, "~", treatment)),
    data = data
  )
  cat("Mann-Whitney U (sensitivity only):\n")
  print(wilcox_test)
  
  # 6. Return results
  results <- list(
    descriptive = descriptive,
    model = model_primary,
    treatment_effect = c(
      estimate = coef_treatment,
      ci_lower = ci_treatment[1],
      ci_upper = ci_treatment[2],
      p_value = p_treatment
    ),
    sensitivity = wilcox_test
  )
  
  return(results)
}

# USAGE
results_primary <- analyze_primary_outcome(
  data = data_clean,
  outcome = "qor_day1",
  treatment = "treatment_group",
  covariates = c("age", "sex", "asa_score", "qor_baseline")
)

# Save model
saveRDS(results_primary, "outputs/models/model_primary.rds")
```

## Bayesian Analysis (brms)

```r
# BAYESIAN LINEAR REGRESSION

fit_bayesian_model <- function(data, outcome, treatment, covariates) {
  
  # Build formula
  formula_bayes <- bf(
    paste(outcome, "~", treatment, "+", paste(covariates, collapse = " + "))
  )
  
  # Set priors (weakly informative)
  priors <- c(
    prior(normal(0, 10), class = "Intercept"),
    prior(normal(0, 5), class = "b"),
    prior(student_t(3, 0, 10), class = "sigma")
  )
  
  # Fit model
  model_bayes <- brm(
    formula = formula_bayes,
    data = data,
    family = gaussian(),
    prior = priors,
    iter = 4000,
    warmup = 2000,
    chains = 4,
    cores = 4,
    seed = 20250107,
    backend = "cmdstanr",
    refresh = 0
  )
  
  # Diagnostics
  cat("\n=== CONVERGENCE DIAGNOSTICS ===\n")
  print(summary(model_bayes))
  
  ## Trace plots
  plot_trace <- plot(model_bayes, ask = FALSE)
  ggsave(
    "outputs/figures/bayes_trace_plots.png",
    plot_trace,
    width = 10,
    height = 6
  )
  
  ## Posterior predictive check
  pp_check_plot <- pp_check(model_bayes, ndraws = 100)
  ggsave(
    "outputs/figures/bayes_pp_check.png",
    pp_check_plot,
    width = 8,
    height = 6
  )
  
  # Extract treatment effect
  posterior_samples <- as_draws_df(model_bayes)
  treatment_effect <- posterior_samples[[paste0("b_", treatment, "1")]]
  
  cat("\n=== TREATMENT EFFECT (POSTERIOR) ===\n")
  cat(sprintf("Mean: %.2f\n", mean(treatment_effect)))
  cat(sprintf("Median: %.2f\n", median(treatment_effect)))
  cat(sprintf(
    "95%% CrI: %.2f to %.2f\n",
    quantile(treatment_effect, 0.025),
    quantile(treatment_effect, 0.975)
  ))
  cat(sprintf("P(effect < 0): %.3f\n", mean(treatment_effect < 0)))
  
  return(model_bayes)
}

# USAGE
model_bayes <- fit_bayesian_model(
  data = data_clean,
  outcome = "qor_day1",
  treatment = "treatment_group",
  covariates = c("age", "sex", "asa_score", "qor_baseline")
)
```

## Survival Analysis

```r
# KAPLAN-MEIER + COX REGRESSION

analyze_survival <- function(data, time_var, event_var, treatment, covariates) {
  
  library(survival)
  library(survminer)
  
  # 1. Kaplan-Meier curves
  km_formula <- as.formula(
    paste("Surv(", time_var, ",", event_var, ") ~", treatment)
  )
  
  fit_km <- survfit(km_formula, data = data)
  
  ## Plot
  km_plot <- ggsurvplot(
    fit_km,
    data = data,
    pval = TRUE,
    conf.int = TRUE,
    risk.table = TRUE,
    risk.table.height = 0.25,
    legend.title = treatment,
    xlab = "Time (days)",
    ylab = "Survival probability",
    break.time.by = 30,
    ggtheme = theme_bw()
  )
  
  ggsave(
    "outputs/figures/km_curve.png",
    print(km_plot),
    width = 10,
    height = 8
  )
  
  # 2. Log-rank test
  logrank_test <- survdiff(km_formula, data = data)
  cat("\n=== LOG-RANK TEST ===\n")
  print(logrank_test)
  
  # 3. Cox proportional hazards model
  cox_formula <- as.formula(
    paste(
      "Surv(", time_var, ",", event_var, ") ~",
      treatment, "+",
      paste(covariates, collapse = " + ")
    )
  )
  
  fit_cox <- coxph(cox_formula, data = data)
  
  cat("\n=== COX REGRESSION ===\n")
  print(summary(fit_cox))
  
  # 4. Check proportional hazards assumption
  ph_test <- cox.zph(fit_cox)
  cat("\n=== PROPORTIONAL HAZARDS TEST ===\n")
  print(ph_test)
  
  if (any(ph_test$table[, "p"] < 0.05)) {
    warning("Proportional hazards assumption violated!")
  }
  
  # 5. Forest plot of hazard ratios
  forest_plot <- ggforest(fit_cox, data = data)
  ggsave(
    "outputs/figures/cox_forest_plot.png",
    forest_plot,
    width = 10,
    height = 6
  )
  
  # Return results
  results <- list(
    km_fit = fit_km,
    cox_fit = fit_cox,
    logrank = logrank_test,
    ph_test = ph_test
  )
  
  return(results)
}
```

## Monte Carlo Simulation (Power Analysis)

```r
# POWER ANALYSIS VIA SIMULATION

simulate_trial_power <- function(
  n_per_group,
  effect_size,
  sd,
  n_simulations = 1000,
  alpha = 0.05
) {
  
  library(furrr)
  plan(multisession, workers = 4)
  
  cat("Running", n_simulations, "simulations...\n")
  
  # Simulation function
  simulate_one_trial <- function(i) {
    
    # Generate data
    data_sim <- tibble(
      group = rep(c("control", "treatment"), each = n_per_group),
      outcome = c(
        rnorm(n_per_group, mean = 0, sd = sd),
        rnorm(n_per_group, mean = effect_size, sd = sd)
      )
    )
    
    # Analyze
    test_result <- t.test(outcome ~ group, data = data_sim)
    
    # Extract p-value
    return(test_result$p.value)
  }
  
  # Run simulations in parallel
  p_values <- future_map_dbl(
    1:n_simulations,
    simulate_one_trial,
    .options = furrr_options(seed = TRUE),
    .progress = TRUE
  )
  
  # Calculate power
  power <- mean(p_values < alpha)
  
  cat("\n=== SIMULATION RESULTS ===\n")
  cat("Sample size per group:", n_per_group, "\n")
  cat("True effect size:", effect_size, "\n")
  cat("Power:", round(power, 3), "\n")
  
  # Plot p-value distribution
  p_value_plot <- ggplot(tibble(p_value = p_values), aes(x = p_value)) +
    geom_histogram(bins = 50, fill = "steelblue", alpha = 0.7) +
    geom_vline(xintercept = alpha, linetype = "dashed", color = "red") +
    labs(
      title = "Distribution of p-values from simulations",
      subtitle = paste("Power =", round(power, 3)),
      x = "P-value",
      y = "Count"
    ) +
    theme_minimal()
  
  ggsave(
    "outputs/figures/power_simulation.png",
    p_value_plot,
    width = 8,
    height = 6
  )
  
  return(power)
}

# USAGE: Power curve
sample_sizes <- seq(50, 200, by = 10)

power_curve <- map_dbl(
  sample_sizes,
  ~simulate_trial_power(
    n_per_group = .x,
    effect_size = 6.3,  # MCID for QoR-40
    sd = 15,
    n_simulations = 1000
  )
)

# Plot power curve
power_curve_data <- tibble(
  n_per_group = sample_sizes,
  power = power_curve
)

ggplot(power_curve_data, aes(x = n_per_group, y = power)) +
  geom_line(size = 1.2, color = "steelblue") +
  geom_point(size = 3, color = "steelblue") +
  geom_hline(yintercept = 0.80, linetype = "dashed", color = "red") +
  scale_y_continuous(limits = c(0, 1), labels = scales::percent) +
  labs(
    title = "Power curve: QoR-40 analysis",
    subtitle = "Effect size = 6.3, SD = 15",
    x = "Sample size per group",
    y = "Power"
  ) +
  theme_minimal()

ggsave("outputs/figures/power_curve.png", width = 10, height = 6)
```

## Related Hubs

- [Folder index hub](../../../docs/FOLDER_INDEX.md)
- [All notes index](../../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../docs/GRAPH_CONNECTIVITY_MAP.md)
