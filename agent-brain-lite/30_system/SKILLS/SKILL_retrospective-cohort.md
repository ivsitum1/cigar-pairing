---
name: retrospective-cohort
description: Use for writing or structuring retrospective cohort manuscripts; follow STROBE. For STROBE checklist check only use strobe-checklist; for case-control or cross-sectional use strobe-checklist with study-specific items. Triggers include: retrospective cohort, retrospektivna kohortna studija, kohortna studija, write cohort study, pisanje kohortne studije, observational cohort.
version: 1.1
last_updated: 2026-03-30
domain: writing
tokens: ~1400
triggers:
  - retrospective cohort
  - retrospektivna kohortna studija
  - kohortna studija
  - write cohort study
  - pisanje kohortne studije
  - observational cohort
  - cohort study manuscript
requires_packages: []
reference_files: []
pipeline_position: [1, 4]
---

# Skill: Writing Retrospective Cohort Studies

## When to use

Use this skill when:
- User wants to **write or structure** a **retrospective cohort study** (data already collected, e.g. from medical records or databases)
- Planning or drafting Methods, Results, and Discussion for a cohort manuscript
- Need guidance on design elements, reporting, and STROBE alignment for cohort studies

For **STROBE checklist compliance check** on an existing draft, use SKILL_strobe-checklist and `.cursor/rules/reporting-strobe.mdc`. For **statistical analysis** (Cox, regression, propensity score), see 30_system/behavior_rules/02_statistics.md and test-selection/analysis plans.

## Prerequisites

- Clear research question (exposure → outcome; often with time-to-event or binary outcome)
- Data source defined (registry, EHR, hospital records, cohort database)
- Pre-specified: eligibility, exposure, outcome, confounders, analysis plan (even if retrospective)

---

## Design: Retrospective cohort in short

- **Definition:** Exposure and outcome are identified from data already collected; no prospective follow-up at study design.
- **Key elements:** Index date (start of follow-up), exposure definition and period, outcome definition, follow-up until outcome or censoring (loss, end of data).
- **Effect measures:** Risk ratio (RR), rate ratio, or **hazard ratio (HR)** for time-to-event; 95% CI. Unadjusted and adjusted (confounders).
- **Limitations to state:** Selection bias, information bias, unmeasured confounding, generalisability; avoid causal language unless supported (e.g. target trial framework or explicit caveats).

---

## Manuscript structure (IMRaD + STROBE)

Follow **STROBE** for observational studies; cohort-specific items: 6a, 7a, 12e, 14c, 15a. Full checklist: `.cursor/rules/reporting-strobe.mdc`.

### Title and Abstract (STROBE Item 1)

- **Title/abstract:** Indicate **cohort design** (e.g. "retrospective cohort study"); balanced summary of what was done and what was found.
- Abstract: background, objectives, methods (setting, population, exposure, outcome, analysis), main results (effect estimate and 95% CI), conclusions, limitations.

### Introduction (Items 2–3)

- **Background:** Scientific rationale; why this exposure–outcome question; gap in evidence.
- **Objectives:** Primary and secondary objectives; pre-specified hypotheses if any.

### Methods (Items 4–12)

Present design early; then setting, population, variables, bias, size, statistics.

#### 4. Study design

- State clearly: **retrospective cohort study**; data source(s); period of data collection and follow-up.

#### 5. Setting and dates (Item 5)

- Setting, locations, relevant dates: recruitment/selection period, exposure period, start of follow-up (index date), end of follow-up/data lock.

#### 6. Participants (Item 6a – cohort)

- **Eligibility:** Inclusion and exclusion criteria.
- **Selection:** Sources of participants (e.g. hospital database, registry); methods of selection (e.g. all eligible patients in period).
- **Follow-up:** How follow-up was ascertained from existing data (e.g. linkage, repeated records); definition of end of follow-up (event, death, loss, administrative censoring).

#### 7. Matching (Item 7a – if applicable)

- If matched cohort: matching criteria and number of exposed and unexposed.

#### 8. Variables (Item 8)

- **Exposure:** Definition, measurement, timing (e.g. at index date, ever/never, time-varying).
- **Outcome:** Definition, diagnostic or operational criteria.
- **Confounders and effect modifiers:** List and define; justify choice (DAG or literature).

#### 9. Data sources and measurement (Item 9)

- For each variable: source (which records, codes, dates); method of assessment; comparability across groups if relevant.

#### 10. Bias (Item 10)

- Potential sources of bias (selection, information, confounding); efforts to address them (e.g. sensitivity analyses, multiple definitions).

#### 11. Study size (Item 11)

- How study size was determined (e.g. all eligible in period; post hoc power or precision if reported).

#### 12. Statistical methods (Item 12)

- **Quantitative variables:** Categorisation if used; rationale.
- **Primary analysis:** Model (e.g. Cox regression for time-to-event; logistic for binary); effect measure (HR, OR, RR with 95% CI); confounder adjustment.
- **Missing data:** Approach (complete case, imputation, sensitivity).
- **Cohort-specific (12e):** Loss to follow-up—how addressed (e.g. censoring, sensitivity).
- **Subgroups and interactions:** Pre-specified; method.
- **Sensitivity analyses:** Listed (e.g. different exposure/outcome definitions, exclusion of early follow-up).

### Results (Items 13–17)

#### 13. Flow (Item 13)

- Numbers at each stage: potentially eligible, assessed, eligible, included, with follow-up, analysed. Reasons for exclusions. **Flow diagram** recommended.

#### 14. Participants (Item 14)

- **Baseline characteristics table:** By exposure (and key subgroups); demographics, clinical variables, confounders. **Number with missing data** per variable. **Cohort-specific (14c):** Summarise follow-up time (e.g. median, IQR; total person-time).

#### 15. Outcomes (Item 15a – cohort)

- **Outcome events or summary over time:** Numbers of events; rates; time-to-event summaries (e.g. Kaplan–Meier); by exposure.

#### 16. Main estimates (Item 16)

- **Unadjusted and adjusted** effect estimates (HR/RR/OR) with 95% CI. State which confounders were adjusted for and why. If continuous variables were categorised, report boundaries.

#### 17. Other analyses (Item 17)

- Subgroups, interactions, sensitivity analyses.

### Discussion (Items 18–20)

- **Key results** with reference to objectives.
- **Interpretation:** Cautious; consider limitations, multiplicity, other evidence. Do not overstate causality if unmeasured confounding or bias likely.
- **Generalisability:** To whom and which settings the results may apply.
- **Limitations:** Explicitly discuss selection bias, information bias, confounding, missing data, retrospective nature.

### Other (Items 21–22)

- Funding; role of funder; ethical approval; consent/waiver (retrospective use of data).

---

## Statistical reporting rules

- **Effect measure:** Report **HR** (or RR/OR) with **95% CI**; avoid p-value alone (99_error_memory).
- **Descriptives:** Mean ± SD or median [IQR] per 99_error_memory; n (%) for categorical.
- **Time-to-event:** Prefer Cox; check proportional hazards (e.g. cox.zph); report follow-up and censoring.
- **Adjustment:** Pre-specified confounders; document in Methods.

---

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Retrospektivna kohorta iz registra; prvi draft glavnih sekcija."  
**Output:** "STROBE sekcije `[EXTRACTED]`; veličina uzorka i definicije `[EXTRACTED]` samo iz dostavljenog; nedostatak u registru `[BLANK]`."

## Verification

- [ ] Design stated as retrospective cohort; STROBE cohort items (6a, 7a, 12e, 14c, 15a) addressed.
- [ ] Index date, exposure, outcome, follow-up clearly defined; flow diagram or numbers; baseline table with missingness and follow-up time.
- [ ] Unadjusted and adjusted estimates with 95% CI; limitations (bias, confounding) discussed.
- [ ] Past tense in Methods; no AI-flagged phrasing (writing-avoid-ai.mdc).

## Related rules

- `.cursor/rules/reporting-strobe.mdc` (STROBE checklist)
- `30_system/behavior_rules/06_study_types.md` (Retrospective observational, Retrospective cohort)
- SKILL_strobe-checklist (compliance check)
- SKILL_manuscript-structure (general IMRaD)

## Learning integration

- **task_type:** writing
- **log_fields:** design_type (retrospective_cohort), strobe_cohort_items
- **post_step:** Suggest STROBE checklist pass (reporting-strobe.mdc or SKILL_strobe-checklist) before submission.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
