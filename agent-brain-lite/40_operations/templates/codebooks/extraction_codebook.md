---
version: "0.1.0"
study_id: "[project_slug]"
last_reviewed: "[YYYY-MM-DD]"
codebook_type: extraction
---

# Extraction codebook (SR / meta-analysis)

**Purpose:** Canonical definitions for variables extracted from included studies. Column names in extraction sheets must match `variable_name` exactly.

**Version control:** Bump `version` in front matter when fields or coding rules change; log in `30_system/04_documentation/context/log.md`.

---

## Study identification

| variable_name | type | definition | unit | allowed_values | missing_rule | notes |
|---------------|------|------------|------|----------------|--------------|-------|
| study_id | string | Unique label for included study (author_year) | — | — | required | e.g. Smith2023 |
| first_author | string | First author surname | — | — | required | |
| publication_year | integer | Year of publication | year | 1900–current | required | |
| country | string | Country/region of conduct | — | — | NR if not reported | |
| design | categorical | Study design | — | RCT; cohort; case-control; other | required | |

---

## Population

| variable_name | type | definition | unit | allowed_values | missing_rule | notes |
|---------------|------|------------|------|----------------|--------------|-------|
| n_total | integer | Total participants analysed | count | ≥1 | required | |
| n_intervention | integer | Participants in intervention arm | count | ≥0 | NA if not applicable | |
| n_control | integer | Participants in control/comparator arm | count | ≥0 | NA if not applicable | |
| population_description | text | Eligibility / setting as reported | — | — | NR | |

---

## Intervention and comparator

| variable_name | type | definition | unit | allowed_values | missing_rule | notes |
|---------------|------|------------|------|----------------|--------------|-------|
| intervention | text | Intervention as reported | — | — | required | |
| comparator | text | Comparator as reported | — | — | required | |

---

## Outcomes (repeat block per outcome)

| variable_name | type | definition | unit | allowed_values | missing_rule | notes |
|---------------|------|------------|------|----------------|--------------|-------|
| outcome_name | string | Outcome label (match SAP) | — | — | required | |
| outcome_type | categorical | Type of outcome | — | binary; continuous; time-to-event; count | required | |
| effect_measure | categorical | Reported or computed effect | — | OR; RR; RD; MD; SMD; HR; other | required | |
| effect_estimate | numeric | Point estimate | per effect_measure | — | NR if not extractable | |
| effect_ci_lower | numeric | Lower 95% CI | same | — | NR | |
| effect_ci_upper | numeric | Upper 95% CI | same | — | NR | |
| effect_se | numeric | Standard error | same | — | NR | compute if only CI given |
| p_value | numeric | Reported p-value | — | 0–1 | NR | do not impute |

---

## Risk of bias / quality

| variable_name | type | definition | unit | allowed_values | missing_rule | notes |
|---------------|------|------------|------|----------------|--------------|-------|
| rob_tool | categorical | RoB instrument used | — | RoB2; ROBINS-I; Newcastle-Ottawa; other | required | |
| rob_overall | categorical | Overall judgement | — | low; some_concerns; high; unclear | NR | per tool domains in separate columns if needed |

---

## Funding and conflicts

| variable_name | type | definition | unit | allowed_values | missing_rule | notes |
|---------------|------|------------|------|----------------|--------------|-------|
| funding | text | Funding source | — | — | NR | |
| conflicts | text | Conflicts of interest | — | — | NR | |

---

## Coding conventions

- **NR:** Not reported in source (do not guess).
- **NA:** Not applicable for this study design.
- **Missing at study level vs participant level:** This sheet is study-level unless IPD; do not mix without documentation.
- **Harmonization:** If two papers use different labels for the same construct, map both to one `variable_name` here and note aliases in `notes`.

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
