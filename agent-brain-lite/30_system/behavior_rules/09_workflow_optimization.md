# Workflow Optimization for AI Agents

## Purpose

This document describes optimized workflows for different types of tasks in scientific paper writing projects. Optimized workflows ensure efficiency, consistency and quality of output.

---

## Workflow Dependency Map

| Workflow | Depends on | Gates | Current rating |
|----------|-----------|-------|---------------|
| 1. Project setup | — | All others | 9/10 |
| 2. Statistical analysis | Workflow 1 | Workflow 3, 5 | 9/10 |
| 3. Manuscript writing | Workflow 2 | Workflow 4, 7 | 9/10 |
| 4. Reference verification | Workflow 3 | Workflow 7 | 9/10 |
| 5. Figure generation | Workflow 2 | Workflow 3 | 9/10 |
| 6. Search strings | — | Workflow 7 | 9/10 |
| 7. Integrated writing | Workflows 3–6 | Workflow 8 | 9/10 |
| 8. Publishing | Workflow 7 | — | 9/10 |

Workflows 2 and 3: content upgrades are reflected in `02_statistics.md` (Bayesian, multilevel,
survival, effect sizes) and `03_scientific_writing.md` (jargon vs clarity by section). Target
rating **9/10** for statistical and writing workflows when those files are applied.

---

## General Optimization Principles

### 1. Proactivity
- Anticipate user needs
- Suggest next steps
- Identify potential problems before they arise

### 2. Batch Processing
- Group similar tasks
- Execute multiple operations in one cycle
- Minimize number of iterations

### 3. Caching and Reusability
- Save results for reuse
- Use previously generated components
- Avoid duplicating work

### 4. Parallel Processing
- Execute independent tasks in parallel
- Optimize time-intensive operations

### 5. Quality Gates
- Check quality at each step
- Do not continue with bad input
- Iterate until goal is achieved

---

## Workflow 1: Creating New Project (Enhanced Version 3.1)

### Enhanced Setup Workflow

The setup process now includes automatic detection, validation, error recovery, and learning integration.

### Steps

```
1. PRE-FLIGHT CHECKS
   ├── Check prerequisites (R/Python, packages)
   ├── Verify permissions
   └── Check disk space

2. STUDY TYPE AUTO-DETECTION
   ├── Analyze project name for study type patterns
   ├── Analyze existing files (if any)
   ├── Calculate confidence score
   └── Use default if confidence < 0.7

3. CHECKPOINT CREATION
   ├── Create backup of existing project state
   └── Store checkpoint metadata

4. LEARNING INTEGRATION - LOG START
   ├── Log setup_start event
   ├── Record project name and study type
   └── Track setup patterns

5. STRUCTURE CREATION
   ├── Create basic folders (01_input, 02_analysis, 03_output, etc.)
   ├── Create subfolders (literature, figures, tables, etc.)
   ├── Add study-specific folders (PRISMA, CONSORT, STROBE)
   └── Create template files (README, changelog, search_strings)

6. VALIDATION
   ├── Validate project structure (all folders exist)
   ├── Validate template files (exist and have content)
   ├── Validate R scripts syntax (if any)
   ├── Validate paths in scripts
   ├── Check git setup
   └── Check dependencies

7. LEARNING INTEGRATION - LOG COMPLETE
   ├── Log setup_complete event
   ├── Record validation results
   └── Update user preferences

8. ERROR RECOVERY (if needed)
   ├── Detect errors during setup
   ├── Suggest fixes based on error type
   ├── Rollback to checkpoint if needed
   └── Log setup_error event
```

### Optimizations

- **Automatic creation**: Use R/Python script to create structure
- **Template library**: Use previously created templates
- **Batch creation**: Create all folders in one cycle

### Code Template

```r
# create_project_structure.R
create_project_structure <- function(project_name, study_type = "meta_analysis") {
  
  # Define structure
  folders <- list(
    "01_input" = c("literature/pdf", "literature/citations", "literature/notes",
                   "data/00_inbox/raw", "data/processed", "data/metadata",
                   "search_strings"),
    "02_analysis" = c("40_operations/scripts", "data", "40_operations/logs"),
    "03_output" = c("figures/forest_plots", "figures/funnel_plots", 
                    "figures/sensitivity", "figures/other",
                    "tables/baseline", "tables/results", "tables/supplementary",
                    "r_scripts",
                    "manuscript/abstract", "manuscript/introduction",
                    "manuscript/methods", "manuscript/results",
                    "manuscript/discussion", "manuscript/references"),
    "30_system/04_documentation" = c("protocol", "sap", "meeting_notes", "correspondence"),
    "05_version_control" = c("versions", "git")
  )
  
  # Create structure
  base_dir <- file.path(getwd(), project_name)
  dir.create(base_dir, showWarnings = FALSE)
  
  for (parent_folder in names(folders)) {
    parent_path <- file.path(base_dir, parent_folder)
    dir.create(parent_path, showWarnings = FALSE, recursive = TRUE)
    
    for (subfolder in folders[[parent_folder]]) {
      subfolder_path <- file.path(parent_path, subfolder)
      dir.create(subfolder_path, showWarnings = FALSE, recursive = TRUE)
    }
  }
  
  # Create template files
  create_template_files(base_dir, study_type)
  
  cat("Project structure created successfully!\n")
  return(base_dir)
}
```

---

## Workflow 2: Statistical Analysis

Statistical workflow follows **`30_system/behavior_rules/02_statistics.md`**. Test-selection hierarchy:
`.cursor/rules/statistics-test-selection.mdc`. Do not duplicate that material here.

### References

- **Test selection:** `.cursor/rules/statistics-test-selection.mdc`
- **Full statistical protocol:** `30_system/behavior_rules/02_statistics.md`

---

## Workflow 3: Writing Manuscript

Writing, reporting (PRISMA/GRADE), AI-aware drafting, and plagiarism checks are defined in
**`30_system/behavior_rules/03_scientific_writing.md`** and **`30_system/behavior_rules/10_ai_writing_plagiarism.md`**.
Integrated AI-score workflow: see **Workflow 7** below. Do not duplicate manuscript workflow detail here.

---

## Workflow 4: Reference Verification

Reference verification checklists and standards are in **`30_system/behavior_rules/03_scientific_writing.md`**
(Rules for References and Citations; PRISMA reference integrity). Do not duplicate that material here.

---

## Workflow 5: Figure Generation

### Steps

```
1. FIGURE PLANNING
   ├── Identify required figures
   ├── Determine figure types (forest, funnel, etc.)
   └── Determine outcomes for each figure

2. DATA PREPARATION
   ├── Prepare data for figures
   ├── Check data quality
   └── Identify required transformations

3. FIGURE CREATION
   ├── Create figures according to standards
   ├── Apply colors and styles
   └── Add labels and annotations

4. EXPORT AND VERIFICATION
   ├── Export to appropriate format (PDF preferred)
   ├── Check resolution
   ├── Check quality
   └── Create figure captions
```

### Optimizations

- **Template-based creation**: Use templates for each figure type
- **Batch generation**: Generate multiple figures at once
- **Automated styling**: Automatically apply standards
- **Pipeline:** For full figure workflow use Pipeline 5 in `30_system/behavior_rules/23_figure_visualization_pipeline.md`; general pipeline stages (Retrieve → Plan → Render → Refine) in `30_system/behavior_rules/22_pipeline_and_refinement.md`.

### Code Template

```r
# generate_figures.R
generate_all_figures <- function(analysis_results, output_dir) {
  
  # Forest plots
  if (!is.null(analysis_results$forest_data)) {
    generate_forest_plots(
      analysis_results$forest_data,
      output_dir = file.path(output_dir, "figures/forest_plots")
    )
  }
  
  # Funnel plots
  if (!is.null(analysis_results$funnel_data)) {
    generate_funnel_plots(
      analysis_results$funnel_data,
      output_dir = file.path(output_dir, "figures/funnel_plots")
    )
  }
  
  # Sensitivity plots
  if (!is.null(analysis_results$sensitivity_data)) {
    generate_sensitivity_plots(
      analysis_results$sensitivity_data,
      output_dir = file.path(output_dir, "figures/sensitivity")
    )
  }
  
  cat("All figures generated successfully!\n")
}
```

---

## Workflow 6: Search String Management

### Steps

```
1. CREATING SEARCH STRINGS
   ├── Identify key terms
   ├── Create search string for each database
   └── Test search string

2. DOCUMENTATION
   ├── Record search string
   ├── Record results
   └── Record modifications

3. UPDATING
   ├── Identify need for updates
   ├── Modify search string
   └── Document changes
```

### Optimizations

- **Version control**: Track versions of search strings
- **Result tracking**: Automatic result tracking
- **Template management**: Standardized format

---

## Workflow 7: Integrated Writing with AI Check

### Overview

This workflow automates the complete writing process with integrated AI detection and automatic revision. It ensures all generated text meets AI detection thresholds through iterative improvement.

### Steps

```
1. WRITE TEXT
   ├── Generate text using Academic Writing Specialist rules
   ├── Apply natural writing variation
   └── Follow academic writing guidelines

2. REAL-TIME CHECK
   ├── Check for banned words
   ├── Check for AI phrases
   ├── Check for sentence patterns
   └── Provide immediate feedback

3. AI SCORE CHECK
   ├── Fast AI detection (basic_ai, text_statistics)
   ├── Advanced methods (BERT, Gradient Boosting, Ensemble) if needed
   └── Calculate AI probability score

4. EVALUATE
   ├── Compare score to target (default: 20%)
   ├── If score < target: Finish
   └── If score >= target: Continue to revision

5. AUTO-REVISE
   ├── Identify specific issues (banned words, phrases, patterns)
   ├── Apply fixes automatically
   ├── Vary sentence beginnings and lengths
   └── Improve paragraph structure

6. RE-CHECK
   ├── Check AI score again
   └── Compare to previous score

7. ITERATE
   ├── Repeat steps 4-6 until score < target
   └── Maximum 5 iterations (configurable)
```

### Implementation

**Python:**
```python
# Run from repo root; add 30_system/behavior_rules/tools to path. See 30_system/behavior_rules/tools/README_tools.md.
import sys
sys.path.insert(0, "30_system/behavior_rules/tools")
from writing.writing_workflow import write_with_ai_check

result = write_with_ai_check(
    initial_text="Your text here",
    target_ai_score=0.20,
    max_iterations=5,
    fast_mode=True
)
```

**R:**
```r
source("30_system/behavior_rules/tools/writing/writing_workflow.R")

result <- write_with_ai_check(
  initial_text = "Your text here",
  target_ai_score = 0.20,
  max_iterations = 5,
  fast_mode = TRUE
)
```

### Components

1. **Real-Time Checker** (`writing_realtime_check.py/R`):
   - Detects banned words, AI phrases, sentence patterns
   - Provides suggestions for replacements

2. **Auto-Revision Engine** (`writing_auto_revise.py/R`):
   - Automatically fixes identified issues
   - Varies sentence structure
   - Improves paragraph organization

3. **AI Score Checker** (`check_ai_score_fast.py/R`):
   - Fast AI detection using basic methods
   - Optional advanced methods (BERT, Gradient Boosting, Ensemble)

4. **Feedback System** (`writing_feedback.py/R`):
   - Formats warnings and suggestions
   - Provides actionable recommendations

5. **Integrated Workflow** (`writing_workflow.py/R`):
   - Orchestrates all components
   - Manages iteration loop
   - Tracks revision history

### Advanced Detection Methods

The workflow supports advanced AI detection methods:

- **BERT-based Detection**: Transformer models for classification
- **Gradient Boosting**: ML models with NLP features
- **Ensemble Methods**: Combination of multiple classifiers
- **N-gram Models**: Structural pattern analysis
- **RADAR-inspired Robust Detection**: Adversarial learning approach

### Agent Integration

When Academic Writing Specialist is activated, the workflow is automatically enabled. The agent uses `write_with_ai_check()` for all text generation, ensuring consistent quality.

### Quality Gates

- **Target AI Score**: < 20% (configurable)
- **Max Iterations**: 5 (configurable)
- **Success Criteria**: AI score below target OR max iterations reached with improvement

### Benefits

1. **Automation**: No manual AI checking required
2. **Consistency**: All text meets quality standards
3. **Efficiency**: Fast detection and revision
4. **Transparency**: Full revision history tracked
5. **Flexibility**: Configurable thresholds and methods

---

## Workflow 8: Publishing (Submission → Revision → Publication)

Publishing steps, desk-rejection screening, journal guidelines placement, and revision flow are
defined in **`30_system/behavior_rules/21_publishing_workflow.md`**. **`07_project_structure.md`** describes
`30_system/04_documentation/journal_guidelines/`, correspondence, and version archives. Do not duplicate that material here.

---

## Best Practices for Workflow Optimization

### 1. Automation

- **Use scripts**: Automate repetitive tasks
- **Pipeline approach**: Connect steps in pipeline
- **Error handling**: Handle errors elegantly

### 2. Documentation

- **Log everything**: Record all steps
- **Version control**: Track changes
- **Comments**: Clear comments in code

### 3. Quality

- **Quality gates**: Quality checks at each step
- **Validation**: Validate input and output
- **Testing**: Test critical components

### 4. Efficiency

- **Caching**: Save results for reuse
- **Parallel processing**: Parallel execution where possible
- **Resource management**: Optimize resource usage

---

## Optimization Checklist

### Before Starting Workflow

- [ ] Task type identified
- [ ] Appropriate workflow selected
- [ ] Required resources prepared
- [ ] Outputs defined

### During Workflow

- [ ] Each step is documented
- [ ] Quality is checked
- [ ] Errors are handled
- [ ] Results are saved

### After Workflow

- [ ] All outputs generated
- [ ] Quality verified
- [ ] Documentation current
- [ ] Version control current

---

## Workflow Evaluation (Post-Upgrade)

Post-implementation assessment of structure and workflow for **statistics**, **writing**, and **publishing** (scale 1–10).

| Domain | Score | Notes |
|--------|-------|--------|
| **Statistics** | **9/10** | Workflow 2 defers to `02_statistics.md` (includes survival, Bayesian decision rule, multilevel/ICC, effect-size thresholds). Test-selection hierarchy in `statistics-test-selection.mdc`. |
| **Writing** | **9/10** | Workflow 3 defers to `03_scientific_writing.md` + `10_ai_writing_plagiarism.md`; jargon vs clarity by section in `03`. Workflow 7 unchanged for AI-check integration. |
| **Publishing** | **8/10** | Workflow 8 defers to `21_publishing_workflow.md` (includes desk-rejection screening). Remaining gap: execution quality still depends on user-provided journal guidelines. |

**Duplications addressed:** Workflows 2–4 and 8 use cross-references instead of repeating content from `02`, `03`, `10`, `21`.

**Overall:** **8.5/10** — Dependency map in place; canonical detail lives in numbered rule files.

---

## References

- See `07_project_structure.md` for project structure
- See `02_statistics.md` for statistical methods
- See `04_visualization.md` for figure standards
- See `21_publishing_workflow.md` for publishing workflow (Workflow 8)
- See `03_scientific_writing.md` for pre-submission checklist and reporting

---

**Version:** 1.2  
**Last updated:** 2026-04-10  
**Status:** Workflow dependency map; Workflows 2–4/8 deduplicated to `02`/`03`/`10`/`21`; evaluation updated

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
