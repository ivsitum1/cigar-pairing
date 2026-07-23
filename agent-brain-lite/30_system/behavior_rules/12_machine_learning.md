> **⚠️ MIGRATED** -> `.cursor/rules/50_ml_mlops_standards.mdc` (2026-05-08)

# Machine Learning Workflow Protection

## Purpose

This document describes critical protocols for preventing data leakage and ensuring valid ML workflows. Data leakage is an invisible error that can lead to falsely optimistic results.

**Related Knowledge Base:**
- `20_knowledge/reference_library/statistics/knowledge_bases/medical_data_science_laboratory.md` — Layer 9: Prediction & ML (Responsible Use), including TRIPOD+AI and PROBAST+AI requirements
- `20_knowledge/reference_library/statistics/knowledge_bases/modern_statistical_literature_2024_2025.md` — TRIPOD+AI, PROBAST+AI, and bias recognition frameworks
- `20_knowledge/reference_library/statistics/knowledge_bases/digital_twin_blueprint.md` — Complete digital twin architecture for ICU/clinical research

---

## Digital Twins for Clinical Research

### What a Digital Twin Is (In This Context)

A digital twin is **not**:
- a dashboard
- a black-box predictor
- a single ML model

A digital twin **is**:
> A probabilistic, causal, time-evolving model that generates **counterfactual patient trajectories** under alternative interventions, with quantified uncertainty.

**Core properties:**
- longitudinal
- causal
- uncertainty-aware
- falsifiable
- modular

### Digital Twin Architecture (7 Layers)

Digital twin = **stack of coupled sub-models**

1. **Data layer** — Input data types (demographics, vitals, labs, treatments, outcomes)
2. **Latent state layer** — Translate noisy observables into clinically meaningful hidden states
3. **Dynamics layer** — Model how latent states evolve over time (natural history engine)
4. **Intervention layer** — Maps interventions → changes in state dynamics (causal core)
5. **Outcome layer** — Survival models, joint longitudinal–survival models, competing risks
6. **Decision layer** — Expected utility, decision curves, optimal treatment rules (optional for research, mandatory for deployment)
7. **Validation layer** — Multi-level validation and falsification

**Each layer must be independently testable.**

### Digital Twin vs ML Model

| Aspect | ML Predictor | Digital Twin |
|------|-------------|--------------|
| Time | Often static | Explicit |
| Causality | No | Yes |
| Counterfactuals | No | Yes |
| Uncertainty | Often ignored | Central |
| Interpretability | Optional | Mandatory |

**Interpretability and mechanistic reasoning:** For digital twins and high-stakes ML, interpretability is mandatory. A rigorous theoretical basis for mechanistic interpretability is given by *causal abstraction*: mapping model components to causal variables and interventions. See Geiger et al., "Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability" (JMLR 2025). For attribution methods (e.g. Integrated Gradients), prefer formulations with clear axiomatic characterizations so that guarantees are explicit (e.g. JMLR "Four Axiomatic Characterizations of the Integrated Gradients Attribution Method" 2025).

### Validation Levels for Digital Twins (MANDATORY)

**Non-negotiable validation:**

1. **Internal validation** — Posterior predictive checks
2. **Temporal validation** — Validation on future time periods
3. **External site validation** — Validation on different sites/cohorts
4. **Stress testing** — Testing under extreme conditions
5. **Prior sensitivity** — Testing sensitivity to prior assumptions

**Key question:**
> Where does the twin fail?

**A twin that never fails is useless.**

### Counterfactual Engine (Core Function)

**Given:**
- Patient history up to time t

**Generate:**
- Trajectory under treatment A
- Trajectory under treatment B
- Distribution of differences

**This is where science happens.**

### Failure Modes (Watch For These)

- Treating proxy variables as truth
- Ignoring timing
- Collapsing uncertainty
- Overfitting natural history
- Policy optimism bias

### Minimal Viable Digital Twin (MVDT)

**Start with:**
- 1 latent severity state
- 1 intervention
- 1 outcome
- Discrete time

**Scale later.**

**Reference:** See `20_knowledge/reference_library/statistics/knowledge_bases/digital_twin_blueprint.md` for complete blueprint and detailed implementation guidance.

---

## Model Interpretability (Clinical ML Requirement)

Clinical adoption of ML models requires explainability. Apply these rules:

1. **Prefer interpretable models** (logistic regression, decision tree, ridge regression)
   when their AUC is within 5% of the complex model — simpler is always better if performance
   is comparable
2. **If a complex model is used** (XGBoost, random forest, neural net): report SHAP values
   for global feature importance. Use `shapviz` or `fastshap` packages in R.
3. **Individual predictions**: provide explanation of top 3 contributing features on request
4. **Subgroup analysis**: report which features drive the top 10% of predictions differently
   from the average (identifies potential fairness issues)
5. **Report in manuscript**: "Model interpretability was assessed using SHAP (SHapley Additive
   exPlanations) values [citation]. Feature [X] contributed most to predicted risk..."

## When Classical Statistics Beats ML

Prefer logistic regression, Cox regression, or mixed models when:

- Fewer than 500 outcome events (ML overfits; classical methods better powered)
- Primary goal is inference (understanding associations), not prediction accuracy
- Causal interpretation is needed (ML gives prediction, not causation)
- Regulatory submission context (FDA/EMA expect pre-specified classical models)
- Fewer than 20 predictors (no high-dimensionality advantage for ML)

Reserve ML for:

- More than 1,000 outcome events
- Primary goal is prediction accuracy
- Strong prior expectation of non-linear relationships
- Feature set > 20 predictors
- Purely predictive tool (no causal claims)

---

## Data Leakage Prevention (CRITICAL)

### Problem: Data Leakage

Data leakage occurs when information from the test set "leaks" into the training set, resulting in:
- Falsely optimistic performance
- Models that don't generalize
- Invisible errors that are only discovered in production

### LEAKAGE PATTERN 1: Preprocessing Before Split

**Problem:** Fitting transformers on entire data before splitting

```r
# ❌ BAD - scaler sees test data
scaled_data <- scale(data)
train_idx <- sample(nrow(data), 0.8 * nrow(data))
train <- scaled_data[train_idx, ]
test <- scaled_data[-train_idx, ]
```

**Solution:**
```r
# ✅ GOOD - fit only on training data
train_idx <- sample(nrow(data), 0.8 * nrow(data))
train_raw <- data[train_idx, ]
test_raw <- data[-train_idx, ]

# Fit scaler on train only
train_means <- colMeans(train_raw)
train_sds <- apply(train_raw, 2, sd)

# Apply to both
train <- scale(train_raw, center = train_means, scale = train_sds)
test <- scale(test_raw, center = train_means, scale = train_sds)
```

### LEAKAGE PATTERN 2: Feature Selection Before Split

**Problem:** Feature selection using all data including test set

```r
# ❌ BAD - feature selection sees test data
important_features <- select_features(data, target)
train <- data[train_idx, important_features]
```

**Solution:**
```r
# ✅ GOOD - feature selection only on training data
important_features <- select_features(train_data, train_target)
train <- train_data[, important_features]
test <- test_data[, important_features]
```

### LEAKAGE PATTERN 3: Temporal Leakage

**Problem:** Random split for time series allows future data in training set

```r
# ❌ BAD for time series - random split allows future data in training
train_idx <- sample(nrow(data), 0.8 * nrow(data))
```

**Solution:**
```r
# ✅ GOOD - temporal split
cutoff_date <- quantile(data$date, 0.8)
train <- data[data$date < cutoff_date, ]
test <- data[data$date >= cutoff_date, ]
```

---

## Safe ML Pipeline Template

```r
# Safe ML pipeline without data leakage
create_ml_pipeline <- function(data, target_col, 
                                numeric_cols, categorical_cols,
                                test_size = 0.2, seed = 42) {
  
  set.seed(seed)
  
  # 1. SPLIT FIRST - before any preprocessing
  n <- nrow(data)
  train_idx <- sample(n, size = floor(n * (1 - test_size)))
  
  train_data <- data[train_idx, ]
  test_data <- data[-train_idx, ]

  message(sprintf("Split: %d train, %d test", nrow(train_data), nrow(test_data)))
  
  # 2. Calculate preprocessing parameters from TRAINING DATA ONLY
  preprocess_params <- list(
    # Numeric: mean and sd for scaling
    numeric = lapply(train_data[, numeric_cols, drop = FALSE], function(x) {
      list(mean = mean(x, na.rm = TRUE), sd = sd(x, na.rm = TRUE))
    }),
    # Categorical: levels for encoding
    categorical = lapply(train_data[, categorical_cols, drop = FALSE], function(x) {
      levels(factor(x))
    })
  )
  
  # 3. Apply preprocessing function
  preprocess <- function(df, params) {
    # Scale numeric
    for (col in names(params$numeric)) {
      p <- params$numeric[[col]]
      df[[col]] <- (df[[col]] - p$mean) / p$sd
    }
    # Encode categorical (handle unseen levels)
    for (col in names(params$categorical)) {
      known_levels <- params$categorical[[col]]
      df[[col]] <- factor(df[[col]], levels = known_levels)
      # Unknown levels become NA
    }
    return(df)
  }
  
  train_processed <- preprocess(train_data, preprocess_params)
  test_processed <- preprocess(test_data, preprocess_params)
  
  # 4. Return pipeline object
  list(
    train = train_processed,
    test = test_processed,
    target_train = train_data[[target_col]],
    target_test = test_data[[target_col]],
    preprocess_params = preprocess_params,
    preprocess_fn = preprocess,
    seed = seed,
    created_at = Sys.time()
  )
}
```

---

## Model Validation Checklist

**BEFORE DEPLOYING MODEL, check:**

```yaml
BEFORE_DEPLOYING_MODEL:
  □ No data leakage in preprocessing pipeline
  □ Proper cross-validation (temporal if time series)
  □ Performance on held-out test set reported
  □ Calibration assessed (for probabilistic models)
  □ Uncertainty reported as appropriate: sampling and, if relevant, distributional (e.g. calibrated inference; conformal prediction for prediction intervals — see JMLR Calibrated Inference 2025, TorchCP)
  □ Feature importance/explanation available
  □ Performance across subgroups checked (fairness)
  □ Confidence intervals for metrics reported
  □ Model versioning and reproducibility documented
```

### Cross-Validation Best Practices

**For time series:**
```r
# Use temporal cross-validation
library(rsample)
time_splits <- time_series_cv(
  data,
  initial = "1 year",
  assess = "3 months",
  skip = "1 month"
)
```

**For standard data:**
```r
# Use stratified k-fold if possible
library(caret)
folds <- createFolds(target, k = 5, list = TRUE, returnTrain = FALSE)
```

---

## Performance Metrics Reporting

**ALWAYS report:**
- Performance on training set
- Performance on validation set (cross-validation)
- Performance on held-out test set
- Confidence intervals for all metrics
- Calibration plots (for probabilistic models)

**Template:**
```r
report_model_performance <- function(model, train_data, test_data, 
                                     train_target, test_target) {
  # Training performance
  train_pred <- predict(model, train_data)
  train_metrics <- calculate_metrics(train_target, train_pred)
  
  # Test performance
  test_pred <- predict(model, test_data)
  test_metrics <- calculate_metrics(test_target, test_pred)
  
  # Report
  cat("=== MODEL PERFORMANCE ===\n")
  cat("\nTraining Set:\n")
  print(train_metrics)
  cat("\nTest Set:\n")
  print(test_metrics)
  cat("\nOverfitting Check:\n")
  cat(sprintf("Train-Test Gap: %.3f\n", 
              train_metrics$accuracy - test_metrics$accuracy))
  
  return(list(
    train = train_metrics,
    test = test_metrics
  ))
}
```

---

## Feature Importance & Explainability

**For all models, ensure:**
- Feature importance scores (for attribution methods like Integrated Gradients, prefer implementations with documented axiomatic guarantees where available, e.g. JMLR 2025 "Four Axiomatic Characterizations of the Integrated Gradients Attribution Method")
- SHAP values (if possible)
- Partial dependence plots for key features
- Model-agnostic interpretability (LIME, etc.)

```r
# Example with randomForest
library(randomForest)
library(pdp)

model <- randomForest(target ~ ., data = train_data)

# Feature importance
importance(model)

# Partial dependence plot
pdp_plot <- partial(model, pred.var = "important_feature", 
                    train = train_data)
plot(pdp_plot)
```

---

## Fairness & Bias Checking

**Check performance across subgroups:**
- By gender
- By age
- By ethnicity (if relevant)
- By other relevant categories

```r
check_fairness <- function(model, test_data, test_target, 
                           protected_attribute) {
  # Overall performance
  overall <- calculate_metrics(test_target, 
                               predict(model, test_data))
  
  # Performance by subgroup
  subgroups <- unique(test_data[[protected_attribute]])
  subgroup_performance <- lapply(subgroups, function(subgroup) {
    idx <- test_data[[protected_attribute]] == subgroup
    calculate_metrics(test_target[idx], 
                     predict(model, test_data[idx, ]))
  })
  
  # Report
  cat("=== FAIRNESS CHECK ===\n")
  cat("Overall Performance:\n")
  print(overall)
  cat("\nSubgroup Performance:\n")
  for (i in seq_along(subgroups)) {
    cat(sprintf("\n%s:\n", subgroups[i]))
    print(subgroup_performance[[i]])
  }
}
```

---

**Version:** 2.1
**Last updated:** 2026-04-10
**Reference:** CURSOR_AGENT_INSTRUCTIONS (1).md, Section 11

## Related (wiki)

- [[Machine learning rule stack]]
- [[Statistics skill stack]]
- [[Skill registry]]

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
