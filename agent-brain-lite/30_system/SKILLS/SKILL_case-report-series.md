---
name: case-report-series
description: Use for writing or structuring case reports and case series; follow CARE. For CARE checklist check only use reporting-care.mdc; for general article structure use manuscript-structure. Triggers include: case report, case series, prikaz slučaja, serija slučajeva, write case report, write case series.
version: 1.1
last_updated: 2026-03-30
domain: writing
tokens: ~1200
triggers:
  - case report
  - case series
  - prikaz slučaja
  - serija slučajeva
  - write case report
  - write case series
  - CARE checklist
  - case report structure
requires_packages: []
reference_files: []
pipeline_position: [1]
---

# Skill: Writing Case Reports and Case Series

## When to use

Use this skill when:
- User wants to write or structure a **case report** (single or very few cases with unusual or instructive features)
- User wants to write or structure a **case series** (series of patients with the same condition or intervention, no control group)
- User asks for CARE checklist compliance or case report/series structure

For **reporting check only** on an existing draft, use `.cursor/rules/reporting-care.mdc` (CARE checklist). For **manuscript structure** in general (IMRaD), use SKILL_manuscript-structure.

## Prerequisites

- Clinical information available (de-identified)
- Informed consent for publication (required for case reports/series)
- Clear rationale: why this case or series adds to the literature (teaching, rare condition, adverse event, new intervention, etc.)

---

## Distinction: Case report vs case series

| | Case report | Case series |
|--|-------------|-------------|
| **N** | 1 or very few (e.g. 2–3) | Several patients, same condition/intervention |
| **Focus** | Single case narrative, timeline, diagnostic/therapeutic reasoning | Group description + individual variation; summary table |
| **Statistics** | Descriptive only; no tests | Descriptive only: mean ± SD or median [IQR], n (%). **No p-values, no inferential tests** |
| **Title** | Include "case report" | Include "case series" |

---

## Part I: Case report – structure and content

Follow **CARE** (Consensus-based Clinical Case Reporting Guideline). Full checklist: `.cursor/rules/reporting-care.mdc`.

### 1. Title and keywords

- Title: include **"case report"** and the clinical focus (e.g. "…: a case report").
- Keywords: 2–5 terms for indexing.

### 2. Abstract

- **Introduction:** What is unique; what the case adds to the literature.
- **Case presentation:** Main symptoms and key clinical findings.
- **Conclusion:** Main take-away lesson.
- Length per journal (often 150–250 words); no citations in abstract.

### 3. Introduction

- Brief background: why this case is important (rare, novel, educational, safety signal).
- One to two short paragraphs; state the learning objective.

### 4. Case presentation (CARE Items 5–21)

Present in logical order; all patient data **de-identified**.

- **Patient information:** Demographics, main symptoms, relevant medical/family/psychosocial history, past interventions and outcomes.
- **Clinical findings:** Relevant physical examination.
- **Timeline:** Dates and sequence of care (table or narrative).
- **Diagnostic assessment:** Methods (labs, imaging, etc.), challenges, differential and diagnostic reasoning, prognostic features if relevant.
- **Therapeutic intervention:** Type, dosing/duration, changes with rationale.
- **Follow-up and outcomes:** Outcomes (clinician- and patient-reported), key follow-up results, adherence/tolerability, adverse or unanticipated events.

### 5. Discussion

- Strengths and limitations of the approach.
- Comparison with relevant literature.
- Rationale for conclusions.
- **Primary take-away lessons** (1–3 clear points).

### 6. Patient perspective (if applicable)

- Patient’s perspective or experience (with consent).

### 7. Informed consent

- **Mandatory:** Explicit statement that informed consent for publication was obtained (written or verbal per journal policy).

### 8. Limitations

- State clearly: single case, no control group, no generalisation, no statistical inference.

---

## Part II: Case series – structure and content

Use CARE where applicable; adapt for multiple patients.

### 1. Title and keywords

- Title: include **"case series"** and the condition or intervention.
- Keywords: 2–5 terms.

### 2. Abstract

- Introduction (why this series matters), case series presentation (setting, period, main findings across cases), conclusion (take-away).

### 3. Introduction

- Rationale for the series; clinical question or teaching aim.

### 4. Case series presentation

- **Characteristics table:** All cases – demographics, key clinical variables, intervention, outcome (mean ± SD or median [IQR] for continuous; n (%) for categorical). **No p-values or inferential statistics.**
- **Narrative:** Per-case description or thematic summary; timeline if relevant.
- **Descriptive statistics only:** Summarise across cases (e.g. mean age, proportion with outcome). Do **not** perform significance tests or compare with external control groups as primary analysis; comparisons with literature are narrative.

### 5. Discussion

- Summary of findings; comparison with literature; strengths and limitations (no control group, selection bias, limited generalisability).

### 6. Informed consent

- Statement that informed consent for publication was obtained for all cases.

### 7. Limitations

- Explicit: no control group, no randomisation, descriptive only, selection bias, limited generalisability.

---

## Statistical and reporting rules

- **Case report:** No statistical tests; descriptive presentation only.
- **Case series:** Descriptive only. Use mean ± SD or median [IQR] per 99_error_memory; n (%) for categorical. **Never** report p-values or inferential tests for group comparisons within the series (no control group).
- **References:** Verify every citation; never fabricate (core-principles).
- **Writing:** Past tense for case presentation and methods; avoid AI-flagged phrasing (see writing-avoid-ai.mdc).

---

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Strukturiraj CARE case report za komplikaciju nakon regionalne anestezije."  
**Output:** "Outline slijedi CARE stavke `[EXTRACTED]`; identifikacija pacijenta i detalji slučaja samo ako ih korisnik da, inače `[BLANK]`."

## Verification

- [ ] Title includes "case report" or "case series".
- [ ] CARE checklist used (reporting-care.mdc); all applicable items addressed.
- [ ] Patient data de-identified; informed consent stated.
- [ ] No inferential statistics; descriptive only; limitations stated.
- [ ] Discussion includes take-away lessons and literature context.

## Related rules

- `.cursor/rules/reporting-care.mdc` (CARE checklist)
- `30_system/behavior_rules/06_study_types.md` (Case report, Case series)
- SKILL_manuscript-structure (general structure)
- SKILL_avoid-ai-formulations (prose quality)

## Learning integration

- **task_type:** writing
- **log_fields:** case_report_or_series, care_compliance
- **post_step:** Suggest CARE checklist pass before submission.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
