---
version: "0.1.0"
study_id: "[project_slug]"
last_reviewed: "[YYYY-MM-DD]"
codebook_type: dataset
---

# Dataset codebook (patient- or row-level data)

**Purpose:** Definitions for every column in the analysis dataset. Read this before EDA or inferential analysis.

**Linked files:**

- Raw data: `01_input/data/00_inbox/raw/`
- Processed: `01_input/data/processed/`
- SAP variable IDs: `30_system/04_documentation/sap/` (reference `variable_name` here; do not duplicate full definitions in SAP)

---

## Identifiers

| variable_name | type | label | unit | allowed_values | missing_code | source | derived_from | sap_id | notes |
|---------------|------|-------|------|----------------|--------------|--------|--------------|--------|-------|
| subject_id | string | Participant ID | — | unique | — | raw | — | — | no PHI in exports |

---

## Demographics

| variable_name | type | label | unit | allowed_values | missing_code | source | derived_from | sap_id | notes |
|---------------|------|-------|------|----------------|--------------|--------|--------------|--------|-------|
| age_years | numeric | Age | years | 0–120 | NA | raw | — | — | |
| sex | categorical | Sex | — | M; F; other; unknown | NA | raw | — | — | |

---

## Exposure / intervention

| variable_name | type | label | unit | allowed_values | missing_code | source | derived_from | sap_id | notes |
|---------------|------|-------|------|----------------|--------------|--------|--------------|--------|-------|
| group | categorical | Treatment group | — | intervention; control | — | raw | — | primary_group | |

---

## Outcomes

| variable_name | type | label | unit | allowed_values | missing_code | source | derived_from | sap_id | notes |
|---------------|------|-------|------|----------------|--------------|--------|--------------|--------|-------|
| primary_outcome | numeric | [define] | [unit] | — | NA | raw | — | primary_outcome | |

---

## Covariates

| variable_name | type | label | unit | allowed_values | missing_code | source | derived_from | sap_id | notes |
|---------------|------|-------|------|----------------|--------------|--------|--------------|--------|-------|
| | | | | | | | | | |

---

## Derived variables

| variable_name | type | label | unit | allowed_values | missing_code | source | derived_from | sap_id | notes |
|---------------|------|-------|------|----------------|--------------|--------|--------------|--------|-------|
| | | | | | | derived | col_a, col_b | | document formula in notes |

---

## Coding conventions

- **Types:** `numeric`, `integer`, `categorical`, `ordered`, `date`, `datetime`, `string`, `logical`.
- **Missing:** Use one scheme consistently (e.g. R `NA`, or explicit codes documented in `missing_code`).
- **Skewed continuous:** Note whether reporting uses mean (SD) or median (IQR) in SAP.
- **Do not** rename columns in analysis scripts without updating this file.

---

## Changelog

| version | date | change |
|---------|------|--------|
| 0.1.0 | [YYYY-MM-DD] | Initial template from brain |

## Semantic graph (auto)

- [[Graph connectivity map]]
- [40 operations INDEX](../../../30_system/docs/indexes/40_operations_INDEX.md)
- [AUTOMATION INDEX](../../../30_system/docs/AUTOMATION_INDEX.md)
- [FOLDER INDEX](../../../30_system/docs/FOLDER_INDEX.md)
