---
name: grade-assessment
description: Use for GRADE certainty-of-evidence assessment across outcomes; NOT for individual study risk-of-bias tools Triggers include: GRADE, quality of evidence, certainty assessment, evidence grading.
version: 1.1
last_updated: 2026-03-30
domain: methodology
tokens: ~700
triggers:
  - GRADE
  - quality of evidence
  - certainty assessment
  - evidence grading
requires_packages: []
reference_files:
  - reference/scientific_critical_thinking/validity_framework.md
pipeline_position: [4]
---

# Skill: GRADE Assessment

## When to use

Use this skill when:
- User requests "GRADE", "quality of evidence", "certainty assessment", "evidence grading"
- Assessing certainty of evidence for outcomes (e.g. in systematic reviews or guidelines)
- Reporting risk of bias and quality across studies

## Prerequisites

- Understanding of PICO and outcomes
- Access to GRADE guidance (GRADE Handbook; Guyatt et al.)

## Step-by-step procedure

1. **Define outcomes:** List critical and important outcomes for the question.

2. **Assess risk of bias:** Per study and across studies (e.g. RoB 2 for RCTs; ROBINS-I for NRSI).

3. **Apply GRADE domains:**
   - Risk of bias
   - Inconsistency
   - Indirectness
   - Imprecision
   - Other (e.g. publication bias, large effect, dose-response)

4. **Rate certainty:** High / Moderate / Low / Very low per outcome. Justify downgrades/upgrades.

5. **Report:** Summary of findings table; justify each downgrade/upgrade in text.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "GRADE za dva ishoda u istom sustavnom pregledu."  
**Output:** "Ocjena sigurnosti po ishodu s razlogom (bias, imprecision) `[INFERRED]` uz tablice `[EXTRACTED]`; brojke studija ne izmišljam."

## Verification

- [ ] All critical/important outcomes assessed
- [ ] Each domain considered and documented
- [ ] Summary of findings table consistent with text

## Related

- Reporting: PRISMA, CONSORT (reporting guidelines)
- Reference: GRADE Working Group; Cochrane Handbook (GRADE for intervention reviews)

## Learning integration

- **task_type:** validation
- **log_fields:** outcomes_assessed, certainty_ratings
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[validity_framework]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
