---
name: strobe-checklist
description: Use for observational studies (cohort, case-control, cross-sectional); for RCTs use consort-checklist; for systematic reviews use prisma-checklist Triggers include: STROBE, observational study checklist, cohort reporting, case-control reporting.
version: 1.1
last_updated: 2026-03-30
domain: methodology
tokens: ~1300
triggers:
  - STROBE
  - observational study checklist
  - cohort reporting
  - case-control reporting
requires_packages: []
reference_files:
  - reference/medical_research/reporting-guideline-compliance-checker/hard-rules.md
pipeline_position: [4]
---

# Skill: STROBE Compliance Check

## When to use

Use this skill when:
- Writing observational study (cohort, case-control, cross-sectional)
- Need to ensure STROBE compliance
- Preparing manuscript for submission

## Prerequisites

- Observational study manuscript
- Access to STROBE checklist

## Step-by-step procedure

1. **Load STROBE checklist:**
   - See `.cursor/rules/reporting-strobe.mdc`
   - Or use official STROBE checklist

2. **Go through each section:**
   - Title and Abstract (Item 1)
   - Introduction (Item 2-3)
   - Methods (Item 4-12)
   - Results (Item 13-17)
   - Discussion (Item 18-20)
   - Other Information (Item 21-22)

3. **Check study-specific items:**
   - **Cohort study:** Items 6a, 7a, 12e, 14c, 15a
   - **Case-control study:** Items 6b, 7b, 12f, 12g, 15b
   - **Cross-sectional study:** Items 6c, 15c

4. **Check each item:**
   - Mark as complete if present
   - Note location in manuscript
   - Identify missing items

5. **Address missing items:**
   - Add missing information
   - Revise sections as needed
   - Ensure all applicable items completed

6. **Final check:**
   - Verify all 22 items addressed
   - Check study-specific items completed
   - Ensure checklist ready for submission

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Je li kohortni manuskript pokrio STROBE stavke za cohort dizajn?"  
**Output:** "Po stavci: status i lokacija u tekstu `[EXTRACTED]`; bez punog teksta stavke `[BLANK]`."

## Verification

- [ ] All 22 STROBE items checked
- [ ] Study-specific items completed (cohort/case-control/cross-sectional)
- [ ] All applicable items completed
- [ ] Missing items addressed
- [ ] Checklist ready for submission

## STROBE Extensions (if applicable)

- **STROBE-ME:** Molecular epidemiology
- **STROBE-Vet:** Veterinary studies

Use appropriate extension if applicable.

## Learning integration

- **task_type:** validation
- **log_fields:** items_checked, compliance_status
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules

- `.cursor/rules/reporting-strobe.mdc`
- `30_system/behavior_rules/06_study_types.md`

## Learning integration

This skill logs:
- Common missing items
- Study type-specific patterns
- Successful compliance strategies

Improves by:
- Learning common gaps by study type
- Suggesting study-specific improvements
- Adapting to different observational designs

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[hard-rules]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
