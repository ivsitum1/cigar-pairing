# Standardized Project Structure

## Purpose

This document defines a standardized folder structure for all scientific paper writing projects. Consistent structure ensures organization, reproducibility and easier navigation through projects.

---

## Standard Folder Structure

```
project_name/
├── 01_input/                    # Input folder for materials
│   ├── literature/              # Papers for citation
│   │   ├── pdf/                 # PDF files of papers
│   │   ├── citations/           # Exported citations (RIS, BibTeX, etc.)
│   │   └── notes/               # Notes on papers
│   ├── data/                    # Input data
│   │   ├── 00_inbox/raw/                 # Raw data
│   │   ├── processed/           # Processed data
│   │   └── metadata/            # Data metadata
│   └── search_strings/          # Search strings for literature review
│       ├── pubmed_search.txt     # PubMed search string
│       ├── embase_search.txt     # Embase search string
│       ├── cochrane_search.txt   # Cochrane Library search string
│       └── search_log.md         # Log of searches and updates
│
├── 02_analysis/                 # Analysis folder
│   ├── 40_operations/scripts/                 # R/Python scripts
│   │   ├── 01_data_preparation.R
│   │   ├── 02_descriptive.R
│   │   ├── 03_inferential.R
│   │   └── 99_utils.R           # Helper functions
│   ├── data/                    # Working data for analysis
│   └── 40_operations/logs/                    # Execution log files
│
├── 03_output/                   # Output folder
│   ├── figures/                 # Visualizations
│   │   ├── forest_plots/        # Forest plots
│   │   ├── funnel_plots/        # Funnel plots
│   │   ├── sensitivity/         # Sensitivity analysis figures
│   │   └── other/               # Other figures
│   ├── tables/                  # Tables
│   │   ├── baseline/            # Baseline characteristics
│   │   ├── results/             # Analysis results
│   │   └── supplementary/      # Supplementary tables
│   ├── r_scripts/               # R analysis scripts (execution order)
│   │   ├── 01_data_loading.R    # Load and prepare raw data
│   │   ├── 02_data_cleaning.R   # Data cleaning and transformation
│   │   ├── 03_descriptive.R     # Descriptive statistics
│   │   ├── 04_analysis.R        # Main analysis
│   │   ├── 05_sensitivity.R     # Sensitivity analyses
│   │   └── README.md            # Execution order and dependencies
│   └── manuscript/              # Manuscript sections
│       ├── abstract/
│       ├── introduction/
│       ├── methods/
│       ├── results/
│       ├── discussion/
│       └── references/          # Verified references
│
├── 30_system/04_documentation/            # Documentation
│   ├── protocol/                # Study protocol
│   ├── sap/                     # Statistical analysis plan
│   ├── meeting_notes/           # Meeting notes
│   ├── correspondence/          # Correspondence
│   └── journal_guidelines/      # Journal-specific guidelines (paste when ready for submission)
│
├── 05_version_control/          # Version control and change log
│   ├── changelog.md             # Log of all changes
│   ├── versions/                # Archived versions
│   │   ├── v1.0/
│   │   ├── v1.1/
│   │   └── ...
│   └── git/                     # Git repository (if used)
│
└── README.md                    # Project README
```

---

## Detailed Folder Description

### 01_input/

**Purpose:** All input materials for the project

#### literature/
- **pdf/**: PDF files of all papers that will be cited
  - Naming: `AuthorYear_ShortTitle.pdf` (e.g., `Smith2023_PropofolTIVA.pdf`)
  - Organization: By date added or by topic

- **citations/**: Exported citations in various formats
  - RIS format (`.ris`)
  - BibTeX format (`.bib`)
  - EndNote format (`.enw`)
  - CSV format for review

- **notes/**: Notes on papers
  - One file per paper: `AuthorYear_notes.md`
  - Key points, relevant citations, critical assessment

#### data/
- **00_inbox/raw/**: Raw data as received
  - Never modify original files
  - Keep original filenames

- **processed/**: Processed data
  - Cleaned data
  - Transformed data
  - Naming: `processed_[description]_[date].csv`

- **metadata/**: Data file provenance (source, receipt date, checksums). Not variable semantics.

#### codebook/ (patient-level studies)
- **dataset_codebook.md**: Canonical definitions for columns in `data/00_inbox/raw/` and processed files (types, units, missing codes, SAP links). Seed from brain template `40_operations/templates/codebooks/dataset_codebook.md`.

#### data_extraction/ (systematic review / meta-analysis)
- **codebook.md**: Canonical definitions for study-level extraction variables. Extraction sheet column names must match `variable_name`. Seed from `40_operations/templates/codebooks/extraction_codebook.md`.

#### search_strings/
- **pubmed_search.txt**: PubMed search string
- **embase_search.txt**: Embase search string
- **cochrane_search.txt**: Cochrane Library search string
- **search_log.md**: Log of all searches
  - Search date
  - Number of results
  - Updates and modifications
  - Reasons for changes

**Search String File Format:**
```
# PubMed Search String
# Date: YYYY-MM-DD
# Database: PubMed
# Results: [number]

([search terms here])

# Notes:
# - [any relevant notes]
# - [modifications made]
```

---

### 02_analysis/

**Purpose:** All analysis scripts and working data

#### 40_operations/scripts/
- Numbered scripts in execution order
- Helper functions in `99_utils.R`
- Each script has header with:
  - Script purpose
  - Author
  - Date
  - Dependencies

**Template Header:**
```r
# ============================================================================
# Script Purpose: [Clear description]
# Author: [Name]
# Date: YYYY-MM-DD
# Dependencies: [List packages]
# Input: [Input files]
# Output: [Output files]
# ============================================================================
```

#### data/
- Working data used in analysis
- Intermediate results
- Do not commit to git if large

#### 40_operations/logs/
- Execution log files
- Error logs
- Execution time logs

---

### 03_output/

**Purpose:** All project outputs - figures, tables, manuscript sections

#### figures/
- **forest_plots/**: Forest plots for all outcomes
  - Naming: `forest_[outcome]_[date].pdf`
  - High resolution (300+ DPI or vector)

- **funnel_plots/**: Funnel plots
  - Naming: `funnel_[outcome]_[date].pdf`

- **sensitivity/**: Sensitivity analysis figures
  - Leave-one-out plots
  - Influence plots
  - Naming: `sensitivity_[type]_[outcome]_[date].pdf`

- **other/**: Other figures
  - PRISMA flow diagrams
  - Risk of bias figures
  - Other relevant figures

**Standards:**
- PDF format preferred (vector)
- Alternative: PNG/TIFF 300+ DPI
- Consistent naming
- Figure captions in separate `.txt` files

#### tables/
- **baseline/**: Baseline characteristics
  - Naming: `table_baseline_[description].csv`

- **results/**: Analysis results
  - Naming: `table_results_[outcome].csv`
  - Also Word format for formatted tables

- **supplementary/**: Supplementary tables
  - Naming: `table_supp_[number]_[description].csv`

**Standards:**
- CSV for data
- Word for formatted tables
- Consistent formatting

#### r_scripts/
- **Purpose**: R analysis scripts organized in execution order
- **Numbering**: Scripts numbered sequentially (01_, 02_, etc.) to indicate execution order
- **Working directory paths**: Each script MUST contain functional working directory paths to raw data files

**Script Requirements:**
- Each script must set working directory at the beginning
- Paths to raw data files (Excel/CSV) must be functional and relative to project root
- Scripts should be executable in sequence without manual path adjustments
- Include clear header with purpose, dependencies, and data file locations

**Template Header (Fully Functional):**
```r
# ============================================================================
# Script: [Number]_[Name].R
# Purpose: [Clear description of what this script does]
# Author: [Name]
# Date: YYYY-MM-DD
# Dependencies: [List required R packages]
# 
# Data Input:
#   - Raw data: 01_input/data/00_inbox/raw/[filename].xlsx (or .csv)
#   - Processed data: [if applicable]
# 
# Data Output:
#   - [Output file locations]
# 
# Execution Order: [Number] (run after [previous script])
# 
# How to Run in R Studio:
#   1. Open this script in R Studio
#   2. Set working directory: Session > Set Working Directory > To Source File Location
#   3. Or simply: Source this file (Ctrl+Shift+S / Cmd+Shift+S)
#   4. Script will automatically detect project root and set paths correctly
# ============================================================================

# ============================================================================
# SETUP: Working Directory and Paths
# ============================================================================

# Method 1: If running in R Studio (recommended)
# This automatically detects project root from script location
if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
  # Get the directory of this script
  script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)
  # Go up to project root (from 03_output/r_scripts/ to project root)
  project_root <- dirname(dirname(script_dir))
  setwd(project_root)
} else {
  # Method 2: Manual setting (if not in R Studio)
  # Set this to your project root directory
  project_root <- getwd()  # Adjust this path if needed
  setwd(project_root)
}

# Verify project root is correct (should contain 01_input, 02_analysis, etc.)
if (!dir.exists(file.path(project_root, "01_input"))) {
  stop("ERROR: Project root not found. Please set project_root manually.")
}

cat("Project root:", project_root, "\n")
cat("Working directory:", getwd(), "\n")

# ============================================================================
# DEFINE PATHS TO DATA FILES
# ============================================================================

# Raw data file path (adjust filename as needed)
raw_data_path <- file.path(project_root, "01_input", "data", "00_inbox/raw", "[filename].xlsx")
# Or for CSV:
# raw_data_path <- file.path(project_root, "01_input", "data", "00_inbox/raw", "[filename].csv")

# Check if data file exists
if (!file.exists(raw_data_path)) {
  warning("Data file not found: ", raw_data_path, "\n",
          "Please ensure data file is in: 01_input/data/00_inbox/raw/")
} else {
  cat("Data file found:", raw_data_path, "\n")
}

# Output paths (if saving results)
output_figures_path <- file.path(project_root, "03_output", "figures")
output_tables_path <- file.path(project_root, "03_output", "tables")

# ============================================================================
# LOAD REQUIRED PACKAGES
# ============================================================================

# Check and install packages if needed
required_packages <- c(
  "readxl",      # For reading Excel files
  # "readr",      # For reading CSV files (alternative)
  # Add other required packages here
)

# Install missing packages (optional - uncomment if needed)
# missing_packages <- required_packages[!required_packages %in% installed.packages()[,"Package"]]
# if (length(missing_packages) > 0) {
#   install.packages(missing_packages)
# }

# Load packages
for (pkg in required_packages) {
  if (!require(pkg, character.only = TRUE)) {
    stop("Package '", pkg, "' is required but not installed.")
  }
}

# ============================================================================
# LOAD DATA
# ============================================================================

# Load raw data
if (file.exists(raw_data_path)) {
  # For Excel files:
  data <- read_excel(raw_data_path)
  # Or for CSV files:
  # data <- read_csv(raw_data_path)
  
  cat("Data loaded successfully.\n")
  cat("Number of rows:", nrow(data), "\n")
  cat("Number of columns:", ncol(data), "\n")
} else {
  stop("Cannot proceed: Data file not found. Please add data file first.")
}

# ============================================================================
# ANALYSIS CODE STARTS HERE
# ============================================================================

# [Your analysis code here]

# ============================================================================
# SAVE RESULTS (if applicable)
# ============================================================================

# Example: Save results table
# write.csv(results_table, 
#           file = file.path(output_tables_path, "results_table.csv"),
#           row.names = FALSE)

cat("\nScript completed successfully!\n")
```

**Naming Convention:**
- `01_data_loading.R` - Load raw data from input folder
- `02_data_cleaning.R` - Clean and prepare data
- `03_descriptive.R` - Descriptive statistics
- `04_analysis.R` - Main statistical analysis
- `05_sensitivity.R` - Sensitivity analyses
- `06_visualization.R` - Create figures (if separate from analysis)
- `99_utils.R` - Helper functions (if needed)

**README.md in r_scripts folder:**
- Must document execution order
- List dependencies between scripts
- Document which data files each script requires
- Note any manual steps required

**Standards:**
- All paths must be functional and relative to project root
- Scripts must be executable in sequence without manual intervention
- Document all data file locations clearly
- Use consistent path structure across all scripts
- Scripts must work when opened directly in R Studio
- Include automatic project root detection
- Include file existence checks with helpful error messages

**How to Use Scripts in R Studio:**

1. **Open script**: Double-click script file in R Studio, or File > Open File
2. **Set working directory** (if needed):
   - Session > Set Working Directory > To Source File Location
   - Or script will auto-detect project root
3. **Run script**:
   - Source entire script: Ctrl+Shift+S (Windows/Linux) or Cmd+Shift+S (Mac)
   - Or run line by line: Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
4. **Verify**: Script should print project root and confirm data file found
5. **Check results**: Outputs will be saved to appropriate folders in `03_output/`

**Troubleshooting:**
- If "project root not found" error: Manually set `project_root` variable in script
- If "data file not found": Ensure data file is in `01_input/data/00_inbox/raw/` with correct filename
- If package errors: Install missing packages using `install.packages("package_name")`

#### manuscript/
- **abstract/**: Abstract
  - `abstract_draft_v[X].docx`
  - `abstract_final.docx`

- **introduction/**: Introduction
  - `introduction_draft_v[X].docx`

- **methods/**: Methods
  - `methods_draft_v[X].docx`
  - May be divided by sections

- **results/**: Results
  - `results_draft_v[X].docx`
  - May be divided by outcomes

- **discussion/**: Discussion
  - `discussion_draft_v[X].docx`

- **references/**: Verified references
  - `references_verified.csv`: Spreadsheet with verification
  - `references.bib`: BibTeX format
  - `references_ris.ris`: RIS format
  - `references_verification_log.md`: Verification log

**Reference Verification Log Format:**
```markdown
# Reference Verification Log

## [Author Year]

**Status**: ✅ Verified / ⚠️ Needs Review / ❌ Not Found

**Verification Date**: YYYY-MM-DD

**DOI**: [DOI if available]
**PMID**: [PMID if available]
**URL**: [URL if available]

**Verification Notes**:
- [Notes about verification]
- [Issues found]
- [Actions taken]

**Verified By**: [Name/Agent]
```

---

### 30_system/04_documentation/

**Purpose:** Project documentation

#### protocol/
- Study protocol
- PROSPERO registration (if applicable)
- Ethics approval documents

#### sap/
- Statistical analysis plan
- Pre-specified analyses
- Plan for handling missing data

#### meeting_notes/
- Meeting notes
- Naming: `meeting_YYYY-MM-DD.md`

#### correspondence/
- Email correspondence
- Communication with reviewers
- Communication with journals

#### journal_guidelines/
- Store journal-specific *Instructions for authors* when you reach submission
- One file per journal, e.g. `[JournalName]_author_instructions.md`, or a single `journal_guidelines.md` for current target
- Paste or summarise word limits, structure, reference style, figure/table rules; see `21_publishing_workflow.md`

---

### 05_version_control/

**Purpose:** Version tracking and changes

#### changelog.md

**Format:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Version] - YYYY-MM-DD

### Added
- [New features]

### Changed
- [Changes to existing features]

### Fixed
- [Bug fixes]

### Removed
- [Removed features]

### Notes
- [Additional notes]
```

#### versions/
- Archived versions of important files
- Each version in its own folder
- Backup before major changes

#### git/
- Git repository (if used)
- `.gitignore` configured for project
- Do not commit large data files

---

## Rules for Creating New Project

### Automatic Structure Creation

**When creating a new project, agent MUST:**

1. **Create basic folder structure**
   ```r
   # R script for creating structure
   create_project_structure <- function(project_name) {
     # Creates all necessary folders
   }
   ```

2. **Create README.md** with basic information
   - Project description
   - Objectives
   - Status
   - Contact information

3. **Create initial changelog.md**

4. **Create search_strings folder** with template files

5. **Create references folder** with verification log template

### README.md Template

```markdown
# [Project Name]

## Project Description

[Brief description]

## Objectives

- [Primary objective]
- [Secondary objectives]

## Status

- **Phase**: [Planning/Analysis/Writing/Submission]
- **Last updated**: YYYY-MM-DD

## Project Structure

[Brief overview of folder structure]

## Contact

[Contact information]
```

---

## Rules for References and Verification

### Reference Verification - Mandatory

**Before adding reference to manuscript:**

1. **Check existence**:
   - [ ] Paper exists in database (PubMed, Embase, etc.)
   - [ ] DOI/PMID is valid
   - [ ] URL is available (if relevant)

2. **Check accuracy**:
   - [ ] Authors are accurate
   - [ ] Year is accurate
   - [ ] Title is accurate
   - [ ] Journal is accurate
   - [ ] Volume, number, pages are accurate

3. **Check relevance**:
   - [ ] Paper actually supports the claim
   - [ ] Paper is not taken out of context
   - [ ] Paper is relevant to the claim

4. **Document verification**:
   - [ ] Add to `references_verification_log.md`
   - [ ] Record verification date
   - [ ] Record verification source
   - [ ] Record any problems

### Reference Verification Spreadsheet Format

**references_verified.csv** columns:
- `citation_number`: Citation number
- `authors`: Authors
- `year`: Year
- `title`: Title
- `journal`: Journal
- `doi`: DOI
- `pmid`: PMID
- `url`: URL
- `verification_date`: Verification date
- `verified_by`: Who verified
- `status`: Verified/Needs Review/Not Found
- `notes`: Notes

### Pre-Finalization Manuscript Checklist

- [ ] All references verified
- [ ] All DOIs/URLs functional
- [ ] Format consistent throughout entire document
- [ ] References match text
- [ ] Cited works support claims
- [ ] No fabricated references
- [ ] Verification log is current
- [ ] All references are in reference list

---

## Search String Rules

### Search String File Format

Each search string file must contain:

```markdown
# [Database Name] Search String
# Project: [Project Name]
# Date Created: YYYY-MM-DD
# Last Updated: YYYY-MM-DD
# Created By: [Name/Agent]

## Search Strategy

([actual search string here])

## Results
- Initial search: [number] results (YYYY-MM-DD)
- After deduplication: [number] results
- After screening: [number] results

## Modifications
- YYYY-MM-DD: [Description of modification and reason]

## Notes
- [Any relevant notes]
```

### Search String Rules

- [ ] **Document all searches**: Every search must be recorded
- [ ] **Reproducibility**: Search string must be reproducible
- [ ] **Updates**: Document all modifications and reasons
- [ ] **Results**: Record number of results at each step
- [ ] **Deduplication**: Document deduplication process

---

## Version Control Rules

### Changelog Updates

**Must update changelog.md when:**

- [ ] New analysis is added
- [ ] Analysis method is changed
- [ ] New data is added
- [ ] Project structure is changed
- [ ] Manuscript version is finalized

### Version Archiving

**Archive versions when:**

- [ ] Analysis version is finalized
- [ ] Manuscript is sent for review
- [ ] Revised version is returned
- [ ] Publication version is finalized

**Version format:**
- `v1.0`: First version
- `v1.1`: Minor changes
- `v2.0`: Major changes

---

## New Project Checklist

Before starting work on new project:

- [ ] Basic folder structure created
- [ ] README.md created
- [ ] changelog.md created
- [ ] search_strings folders created with templates
- [ ] references folder created with verification log template
- [ ] Output folders created (figures, tables, r_scripts, manuscript)
- [ ] r_scripts folder created with README.md template
- [ ] version_control folder created

---

## References

- **CONSORT**: For randomized trials
- **STROBE**: For observational studies
- **PRISMA**: For systematic reviews
- **CARE**: For case reports

---

**Version:** 1.0  
**Last updated:** 2024-12-31

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
