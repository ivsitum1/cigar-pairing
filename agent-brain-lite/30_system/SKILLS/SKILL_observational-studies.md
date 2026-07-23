---
name: observational-studies
description: Use for writing case-control or cross-sectional manuscripts; STROBE by design. For cohort use prospective-cohort or retrospective-cohort; for checklist check use strobe-checklist. Triggers include: observational study, opservacijska studija, write observational study, pisanje opservacijske studije, case-control, cross-sectional.
version: 1.1
last_updated: 2026-03-30
domain: writing
tokens: ~1500
triggers:
  - observational study
  - opservacijska studija
  - write observational study
  - pisanje opservacijske studije
  - case-control
  - cross-sectional
  - presječna studija
  - studija slučaj-kontrola
requires_packages: []
reference_files: []
pipeline_position: [1, 4]
---

# Skill: Writing Observational Studies (Cohort, Case-Control, Cross-Sectional)

## When to use

Use this skill when:
- User wants to **write or structure** an **observational study** and the design is cohort, case-control, or cross-sectional
- Need guidance on which design to report and how (STROBE by design type)
- Drafting Methods, Results, and Discussion for observational manuscripts

For **prospective cohort** specifically use SKILL_prospective-cohort; for **retrospective cohort** use SKILL_retrospective-cohort. For **STROBE checklist compliance check** use SKILL_strobe-checklist and `.cursor/rules/reporting-strobe.mdc`.

---

## Design choice (when to use which)

| Design | Use when | Direction | Typical effect measure |
|--------|----------|-----------|-------------------------|
| **Cohort** | Follow exposure → outcome over time; incidence | Exposure → Outcome | RR, HR, rate ratio |
| **Case-control** | Outcome is rare; start from cases and controls | Outcome → Exposure (backward) | OR |
| **Cross-sectional** | Snapshot; prevalence or association at one time | No temporal direction | Prevalence, PR, OR |

- **Cohort (prospective/retrospective):** See SKILL_prospective-cohort and SKILL_retrospective-cohort for full structure.
- **Case-control and cross-sectional:** Structure below; STROBE items 6b/7b/12f/12g/15b (case-control) or 6c/15c (cross-sectional).

---

## Common structure (all observational) – STROBE

All three designs follow **STROBE** (22 items). Full checklist: `.cursor/rules/reporting-strobe.mdc`.

### Title and Abstract (Item 1)

- Indicate study design in title or abstract (e.g. "case-control study", "cross-sectional study").
- Balanced summary of what was done and what was found.

### Introduction (Items 2–3)

- **Background:** Rationale for the investigation.
- **Objectives:** Specific objectives; pre-specified hypotheses if any.

### Methods (Items 4–12)

- **4.** Present key elements of study design early.
- **5.** Setting, locations, dates (recruitment, exposure, follow-up or survey period).
- **6–7.** **Design-specific** (see below).
- **8.** Define outcomes, exposures, predictors, confounders, effect modifiers; diagnostic criteria if applicable.
- **9.** Data sources and methods of assessment for each variable.
- **10.** Efforts to address bias.
- **11.** How study size was arrived at.
- **12.** Statistical methods; handling of quantitative variables, confounding, missing data, subgroups, sensitivity; **design-specific** 12e/12f/12g (see below).

### Results (Items 13–17)

- **13.** Numbers at each stage; reasons for non-participation; flow diagram where helpful.
- **14.** Participant characteristics; missing data per variable; **cohort only (14c):** follow-up time.
- **15.** **Design-specific** (see below).
- **16.** Unadjusted and adjusted estimates with 95% CI; confounders stated; category boundaries if variables categorised.
- **17.** Other analyses (subgroups, sensitivity).

### Discussion (Items 18–20)

- Key results; interpretation; limitations; generalisability.

### Other (Items 21–22)

- Funding; ethics; consent.

---

## Case-control – design-specific (STROBE 6b, 7b, 12f, 12g, 15b)

### Methods

- **Item 6b:** Eligibility; sources and methods of **case ascertainment** and **control selection**; rationale for choice of cases and controls.
- **Item 7b:** If matched: matching criteria and **number of controls per case**.
- **Item 12f:** If matching was used, how it was addressed in analysis.
- **Item 12g:** Analytical methods for matched design (e.g. conditional logistic regression).

### Results

- **Item 15b:** Numbers in each **exposure category** (or summary measures of exposure) for cases and controls.

### Effect measure

- **Odds ratio (OR)** with 95% CI; unadjusted and adjusted (confounders). No causal language without appropriate caveats.

### Reporting rules

- Baseline/characteristics table: cases vs controls (exposure and confounders). Mean ± SD or median [IQR]; n (%) (99_error_memory).
- Clearly state that design does not allow incidence; OR approximates RR when outcome is rare.

---

## Cross-sectional – design-specific (STROBE 6c, 15c)

### Methods

- **Item 6c:** Eligibility; sources and methods of selection of participants (single time point or survey period).
- No follow-up; one measurement (or period) for exposure and outcome.

### Results

- **Item 15c:** Numbers of outcome events or summary measures (e.g. prevalence, prevalence ratio).

### Effect measure

- **Prevalence**, prevalence ratio (PR), or OR for association; 95% CI. No temporal direction; avoid causal language.

### Reporting rules

- Describe when and how data were collected (single time point or window). No follow-up time.

---

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Pišem case-control o riziku Y; treba STROBE usklađen nacrt."  
**Output:** "Odjeljci po STROBE-u `[EXTRACTED]`; matching i kontrole `[BLANK]` ako nisu definirani."

## Verification

- [ ] Design (cohort / case-control / cross-sectional) stated; correct STROBE design-specific items addressed (6a/7a/12e/14c/15a for cohort; 6b/7b/12f/12g/15b for case-control; 6c/15c for cross-sectional).
- [ ] Effect measure appropriate (RR/HR for cohort; OR for case-control; prevalence/PR/OR for cross-sectional); 95% CI; limitations discussed.
- [ ] Past tense in Methods; no AI-flagged phrasing (writing-avoid-ai.mdc).

## Related rules

- `.cursor/rules/reporting-strobe.mdc`
- `30_system/behavior_rules/06_study_types.md`
- SKILL_prospective-cohort, SKILL_retrospective-cohort (cohort writing)
- SKILL_strobe-checklist (compliance check)

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
