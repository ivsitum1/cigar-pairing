# R scripts

**Scope:** R is used **only** for statistics, hypothesis testing, simulation, modeling, and power analysis. Writing, quality gates (self-assessment, Swiss Cheese), AI detection, and agents use **Python** (`40_operations/python/quality_validation/`, `30_system/behavior_rules/tools/`, `.ai/`). Put statistical R code in this `40_operations/R/` folder.

**Runnable in RStudio** with project root set to the folder containing `40_operations/R/`, `.ai/`, `30_system/behavior_rules/`.

## Paths

- **Project root:** In RStudio: *File → Open Project* → select the "agent rules" folder. Then `getwd()` is project root.
- **Raw data:** Set when you load data for statistics. Default: `file.path(getwd(), "01_input", "data", "00_inbox/raw")`. Override in your script or in `40_operations/R/00_paths.R`:
  ```r
  source("40_operations/R/00_paths.R")
  path_raw_data <- "C:/your/path/to/00_inbox/raw"   # override when loading data
  ```

## Quality validation (not in R)

Self-assessment and Swiss Cheese run in Python. See `40_operations/R/validation/README.md` and:

```bash
python 40_operations/scripts/run_quality_validation.py assess --text "your output" --domain statistics
```

## Structure

- `00_paths.R` – project root and `path_raw_data` (configurable).
- `validation/README.md` – pointer to Python implementation (historical folder).
- Add subfolders as needed for analysis, simulation, power, modeling. Keep statistical R under `40_operations/R/`.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
