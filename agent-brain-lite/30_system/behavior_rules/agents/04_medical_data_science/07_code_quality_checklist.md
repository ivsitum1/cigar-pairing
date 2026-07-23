# Code Quality & Debugging

## Error Handling & Defensive Programming

### Defensive Programming

```r
# ALWAYS VALIDATE INPUTS

analyze_with_validation <- function(data, outcome, treatment) {
  
  # Check arguments exist
  if (missing(data)) stop("Argument 'data' is missing")
  if (missing(outcome)) stop("Argument 'outcome' is missing")
  if (missing(treatment)) stop("Argument 'treatment' is missing")
  
  # Check data types
  stopifnot(
    "data must be a data frame" = is.data.frame(data),
    "outcome must be a string" = is.character(outcome),
    "treatment must be a string" = is.character(treatment)
  )
  
  # Check variables exist in data
  if (!outcome %in% names(data)) {
    stop(paste("Variable", outcome, "not found in data"))
  }
  if (!treatment %in% names(data)) {
    stop(paste("Variable", treatment, "not found in data"))
  }
  
  # Check variable types
  if (!is.numeric(data[[outcome]])) {
    stop(paste("Outcome", outcome, "must be numeric"))
  }
  if (!is.factor(data[[treatment]]) && !is.character(data[[treatment]])) {
    stop(paste("Treatment", treatment, "must be factor or character"))
  }
  
  # Check for sufficient data
  if (nrow(data) < 20) {
    warning("Sample size < 20, results may be unreliable")
  }
  
  # Check for missing data
  missing_outcome <- sum(is.na(data[[outcome]]))
  missing_treatment <- sum(is.na(data[[treatment]]))
  
  if (missing_outcome > 0) {
    warning(paste(missing_outcome, "observations with missing outcome"))
  }
  if (missing_treatment > 0) {
    stop(paste(missing_treatment, "observations with missing treatment (not allowed)"))
  }
  
  # Proceed with analysis
  # ...
}
```

### Debugging Tools

```r
# USE THESE FOR TROUBLESHOOTING

# 1. Browser (interactive debugging)
my_function <- function(x) {
  browser()  # Execution stops here, allows inspection
  result <- x^2
  return(result)
}

# 2. Trace (see function calls)
trace(lm, tracer = quote(print(head(model.frame()))))

# 3. Debug (step through function)
debug(my_function)
my_function(5)
undebug(my_function)

# 4. Print intermediate results
my_function <- function(x) {
  cat("Input:", x, "\n")
  result <- x^2
  cat("Output:", result, "\n")
  return(result)
}

# 5. Assertions with custom messages
stopifnot(
  "x must be positive" = x > 0,
  "x must be numeric" = is.numeric(x)
)
```

## Common Pitfalls (Avoid)

🚩 **Not setting seed** → Non-reproducible results  
🚩 **Using `attach()`** → Namespace conflicts  
🚩 **Forgetting `stringsAsFactors = FALSE`** → Unwanted factor conversion  
🚩 **Not checking assumptions** → Invalid inference  
🚩 **Printing large objects** → Console overflow  
🚩 **Hardcoding paths** → Breaks portability (use `here::here()`)  
🚩 **No version control** → Lost work  
🚩 **No backups** → Data loss  

## Self-Assessment Checklist

Before submitting code:

### General
- [ ] Script runs from top to bottom without errors
- [ ] Seed is set for reproducibility
- [ ] Input validation performed
- [ ] Results match expectations (sanity check)
- [ ] Code is commented (why, not what)

### Paths & Files
- [ ] PROJECT_ROOT variable set using here::here() (or manual path if needed)
- [ ] All file paths use file.path(PROJECT_ROOT, ...)
- [ ] Working directory set with setwd(PROJECT_ROOT)
- [ ] Code runs independently in RStudio (tested)

### Project Independence
- [ ] NO hardcoded values from previous projects (MCID, project-specific constants)
- [ ] Data file names are project-specific or placeholders
- [ ] Only relevant packages loaded (not from previous 10_projects/projects)
- [ ] Constants defined only if relevant to THIS project

### Reproducibility
- [ ] sessionInfo() saved to session_info/ directory
- [ ] Working directory included in session info output
- [ ] renv::snapshot() run after installing new packages (40_operations/R)
- [ ] environment.yml updated (Python)

## Code Review Checklist (for reviewers)

### Correctness
- [ ] Statistical methods appropriate for data type
- [ ] Sample size adequate for analysis
- [ ] Missing data handled correctly
- [ ] Assumptions checked and met

### Reproducibility
- [ ] Random seed set
- [ ] Package versions documented
- [ ] Data sources clearly specified
- [ ] Code runs without modification

### Clarity
- [ ] Variable names descriptive
- [ ] Functions documented
- [ ] Complex logic explained
- [ ] Output files clearly named

### Best Practices
- [ ] No hardcoded paths
- [ ] Error handling present
- [ ] Validation checks included
- [ ] Session info saved

## Related Hubs

- [Folder index hub](../../../docs/FOLDER_INDEX.md)
- [All notes index](../../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../docs/GRAPH_CONNECTIVITY_MAP.md)
