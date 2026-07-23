---
name: rct-manuscript
description: Use for writing or structuring RCT manuscripts; follow CONSORT. For CONSORT checklist compliance check only use consort-checklist. Triggers include: RCT, randomized controlled trial, randomizirana kontrolirana studija, write RCT, pisanje RCT-a, clinical trial manuscript.
version: 1.1
last_updated: 2026-03-30
domain: writing
tokens: ~1500
triggers:
  - RCT
  - randomized controlled trial
  - randomizirana kontrolirana studija
  - write RCT
  - pisanje RCT-a
  - clinical trial manuscript
  - CONSORT writing
requires_packages: []
reference_files: []
pipeline_position: [1, 4]
---

# Skill: Writing Randomized Controlled Trial (RCT) Manuscripts

## When to use

Use this skill when:
- User wants to **write or structure** an **RCT** manuscript (parallel, factorial, crossover, cluster, etc.)
- Planning or drafting Title, Abstract, Introduction, Methods, Results, Discussion in line with CONSORT
- Need guidance on mandatory elements (randomization, allocation concealment, flow diagram, registration)

For **CONSORT checklist compliance check** on an existing draft use SKILL_consort-checklist and `.cursor/rules/reporting-consort.mdc`. For **protocol** (SPIRIT) use reporting-spirit and protocol-writing guidance.

## Prerequisites

- Trial completed or in progress; protocol (and registration) available
- Pre-specified: primary and secondary outcomes; analysis plan; sample size rationale
- CONSORT 2010 as reporting standard; extensions if applicable (cluster, non-inferiority, pragmatic, pilot, harms)

---

## Manuscript structure (CONSORT 2010)

Full checklist: `.cursor/rules/reporting-consort.mdc`. Flow diagram is **mandatory**.

### Title and Abstract (Items 1a–1b)

- **Title (1a):** Identify as a **randomized trial** (e.g. "randomized controlled trial", "RCT").
- **Abstract (1b):** Structured summary: design, methods, results, conclusions. Use CONSORT for abstracts if journal requests.

### Introduction (Items 2a–2b)

- **Background (2a):** Scientific background and rationale for the trial.
- **Objectives (2b):** Specific objectives or hypotheses (primary and key secondary).

### Methods (Items 3a–12b)

- **3a.** Trial design (e.g. parallel, factorial); allocation ratio.
- **3b.** Any important changes to methods after trial commencement, with reasons.
- **4a–4b.** Eligibility criteria; settings and locations.
- **5.** Interventions for each group (sufficient detail for replication); how and when administered.
- **6a–6b.** Pre-specified primary and secondary outcomes; how and when assessed; any changes with reasons.
- **7a–7b.** How sample size was determined; interim analyses and stopping guidelines if applicable.
- **8a–8b.** **Randomization:** Method to generate allocation sequence; type of randomization; any restriction (blocking, block size).
- **9.** **Allocation concealment:** Mechanism to implement allocation (e.g. sequentially numbered containers); steps to conceal sequence until assignment.
- **10.** Who generated sequence, who enrolled participants, who assigned to interventions (separation of roles).
- **11a–11b.** **Blinding:** Who was blinded (participants, care providers, outcome assessors) and how; if unblinded, similarity of interventions (e.g. appearance).
- **12a–12b.** Statistical methods for primary and secondary outcomes; methods for subgroup and adjusted analyses. **Pre-specified vs exploratory** clearly distinguished (99_error_memory).

### Results (Items 13a–18)

- **13a–13b.** **Flow:** For each group—randomly assigned, received intended treatment, analysed for primary outcome; losses and exclusions after randomization with reasons. **CONSORT flow diagram (mandatory).**
- **14a–14b.** Dates of recruitment and follow-up; why trial ended or was stopped.
- **15.** **Baseline table:** Demographic and clinical characteristics by group.
- **16a–16c.** For each outcome: denominator per group; results per group; **effect size and precision (95% CI)**; for binary outcomes, absolute and relative effect sizes recommended. No p-value alone (99_error_memory).
- **17a–17b.** Other analyses (subgroups, adjusted); **pre-specified vs exploratory** (reporting-consort, 99_error_memory).
- **18.** **Harms:** All important harms or unintended effects per group (CONSORT for harms if applicable).

### Discussion (Items 19–21)

- **19.** Limitations (bias, imprecision, multiplicity).
- **20.** Generalisability (external validity).
- **21.** Interpretation consistent with results; benefits and harms; other evidence.

### Other Information (Items 22–25)

- **22.** **Trial registration** number and registry name (e.g. ClinicalTrials.gov, EudraCT).
- **23.** Where full protocol can be accessed.
- **24.** Funding and other support; role of funders.
- **25.** Ethical approval; informed consent.

---

## Mandatory elements (never omit)

- **Randomization:** Sequence generation (8a) and allocation concealment (9).
- **Flow diagram:** Enrollment → allocation → follow-up → analysis; numbers and reasons at each step.
- **Registration:** Protocol registration (22); state if registered before first enrollment.
- **Primary outcome:** Clearly defined; results with effect size and 95% CI (16b).
- **Pre-specified vs exploratory:** All subgroup and adjusted analyses labelled (17a–17b, 99_error_memory).

---

## CONSORT extensions (if applicable)

- **Cluster RCT:** CONSORT-Cluster.
- **Non-inferiority:** CONSORT-Non-inferiority.
- **Pragmatic:** CONSORT-Pragmatic.
- **Pilot/feasibility:** CONSORT-Pilot.
- **Non-pharmacological:** CONSORT-NPT.
- **Harms:** CONSORT-Harms.

Use the relevant extension in addition to main CONSORT when drafting.

---

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "RCT manuskript: randomizacija, ITT, CONSORT flow."  
**Output:** "Mapiranje na CONSORT sekcije `[INFERRED]`; brojevi iz protokola `[EXTRACTED]` ako su dati; flow brojevi bez podataka `[BLANK]`."

## Verification

- [ ] Title identifies randomized trial; flow diagram included; registration stated.
- [ ] Randomization (sequence + concealment) and blinding clearly described.
- [ ] Primary outcome results with effect size and 95% CI; pre-specified vs exploratory distinguished; harms reported.
- [ ] Past tense in Methods; no AI-flagged phrasing (writing-avoid-ai.mdc).

## Related rules

- `.cursor/rules/reporting-consort.mdc`
- `30_system/behavior_rules/06_study_types.md`
- SKILL_consort-checklist (compliance check)
- SKILL_manuscript-structure (general IMRaD)

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
