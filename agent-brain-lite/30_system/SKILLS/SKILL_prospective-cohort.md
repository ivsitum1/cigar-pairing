---
name: prospective-cohort
description: Use for writing or structuring prospective cohort manuscripts; follow STROBE. For retrospective cohort use retrospective-cohort; for checklist check use strobe-checklist. Triggers include: prospective cohort, prospektivna kohortna studija, write prospective cohort, pisanje prospektivne kohortne studije, longitudinal cohort.
version: 1.1
last_updated: 2026-03-30
domain: writing
tokens: ~1200
triggers:
  - prospective cohort
  - prospektivna kohortna studija
  - write prospective cohort
  - pisanje prospektivne kohortne studije
  - longitudinal cohort
requires_packages: []
reference_files: []
pipeline_position: [1, 4]
---

# Skill: Writing Prospective Cohort Studies

## When to use

Use this skill when:
- User wants to **write or structure** a **prospective cohort study** (participants enrolled and then followed forward in time; data collected after enrollment)
- Planning or drafting Methods, Results, and Discussion for a prospective cohort manuscript
- Need guidance on design elements, reporting, and STROBE alignment for cohort studies

For **STROBE checklist compliance check** use SKILL_strobe-checklist and `.cursor/rules/reporting-strobe.mdc`. For **retrospective** cohort (data already collected) use SKILL_retrospective-cohort.

## Prerequisites

- Clear research question (exposure → outcome)
- Prospective design: enrollment defined, follow-up planned a priori
- Pre-specified: eligibility, exposure, outcome, confounders, analysis plan

---

## Design: Prospective cohort in short

- **Definition:** Participants are enrolled (exposed/unexposed or single cohort with exposure assessed) and followed forward in time; outcomes and covariates are collected during or at the end of follow-up.
- **Key elements:** Recruitment period and setting; eligibility; exposure definition and assessment; outcome definition and assessment over time; follow-up procedures and loss to follow-up.
- **Effect measures:** Risk ratio (RR), rate ratio, or **hazard ratio (HR)** for time-to-event; 95% CI. Unadjusted and adjusted for confounders.
- **Advantages over retrospective:** Clear temporal sequence; planned outcome assessment; often better data quality and less selection bias from pre-existing records.

---

## Manuscript structure (IMRaD + STROBE)

Follow **STROBE**; cohort-specific items: 6a, 7a, 12e, 14c, 15a. Full checklist: `.cursor/rules/reporting-strobe.mdc`.

### Title and Abstract (STROBE Item 1)

- **Title/abstract:** Indicate **prospective cohort** (e.g. "prospective cohort study"); balanced summary of what was done and what was found.
- Abstract: background, objectives, methods (setting, population, exposure, outcome, follow-up, analysis), main results (effect estimate and 95% CI), conclusions, limitations.

### Introduction (Items 2–3)

- **Background:** Scientific rationale; why this exposure–outcome question; gap in evidence.
- **Objectives:** Primary and secondary objectives; pre-specified hypotheses if any.

### Methods (Items 4–12)

#### 4. Study design

- State clearly: **prospective cohort study**; participants enrolled and followed over time; data collected prospectively.

#### 5. Setting and dates (Item 5)

- Setting, locations; **periods of recruitment**, exposure assessment, **follow-up**, and data collection.

#### 6. Participants (Item 6a – cohort)

- **Eligibility:** Inclusion and exclusion criteria.
- **Selection:** Sources and methods of recruitment (e.g. clinics, population register); how exposed and unexposed were identified or how exposure was assessed in a single cohort.
- **Follow-up:** Methods of follow-up (visits, linkage, registries); frequency and duration; definition of end of follow-up (event, death, loss, administrative end).

#### 7. Matching (Item 7a – if applicable)

- If matched: matching criteria and number of exposed and unexposed.

#### 8. Variables (Item 8)

- **Exposure:** Definition, timing of assessment (baseline or time-varying).
- **Outcome:** Definition, diagnostic/operational criteria, when assessed.
- **Confounders and effect modifiers:** List, define, justify.

#### 9–12. Data sources, bias, study size, statistical methods

- As in STROBE; **Item 12e (cohort):** How loss to follow-up was addressed (e.g. censoring, sensitivity analysis, multiple imputation).

### Results (Items 13–17)

- **Flow (Item 13):** Numbers at each stage; reasons for non-participation; **flow diagram** recommended.
- **Participants (Item 14):** Baseline characteristics table; missing data per variable; **Item 14c (cohort):** Summarise follow-up time (median, IQR; person-time).
- **Outcomes (Item 15a):** Numbers of events or summary measures over time by exposure.
- **Estimates (Item 16):** Unadjusted and adjusted effect estimates (HR/RR/OR) with 95% CI; confounders adjusted for.
- **Other (Item 17):** Subgroups, sensitivity analyses.

### Discussion (Items 18–20)

- Key results; cautious interpretation; limitations (loss to follow-up, confounding, measurement error); generalisability.

### Other (Items 21–22)

- Funding; ethics; consent.

---

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Outline prospektivne kohorte za podnošenje časopisu."  
**Output:** "STROBE-usklađene sekcije `[EXTRACTED]`; definicija follow-upa `[BLANK]` ako korisnik nije dao timeline."

## Verification

- [ ] Design stated as prospective cohort; STROBE cohort items (6a, 7a, 12e, 14c, 15a) addressed.
- [ ] Recruitment and follow-up periods and procedures clearly described; flow and baseline table; follow-up time reported.
- [ ] Effect estimates with 95% CI; limitations discussed.

## Related rules

- `.cursor/rules/reporting-strobe.mdc`
- `30_system/behavior_rules/06_study_types.md`
- SKILL_retrospective-cohort (for retrospective design)
- SKILL_strobe-checklist (compliance check)

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
