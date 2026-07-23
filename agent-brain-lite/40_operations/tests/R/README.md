# R tests (testthat)

Tests for `40_operations/R/validation/` and `40_operations/R/shared/` modules.

## Requirements

- R with **testthat**: `install.packages("testthat")`

## Run from project root

```r
# All R tests
testthat::test_dir("40_operations/tests/R")

# Single file
testthat::test_file("40_operations/tests/R/test_check_assumptions.R")
testthat::test_file("40_operations/tests/R/test_evaluate_rubric.R")
```

Or from shell (project root):

```bash
Rscript -e "testthat::test_dir('40_operations/tests/R')"
```

## Coverage target

>60% for `40_operations/R/shared/` and validation rubrics (per AGENT-RULES v2).

## Related Hubs

- [Folder index hub](../../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
