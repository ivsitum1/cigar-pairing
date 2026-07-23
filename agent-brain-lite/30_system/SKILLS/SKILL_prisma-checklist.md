---
name: prisma-checklist
description: Audits an existing systematic review or meta-analysis manuscript for PRISMA 2020 compliance item-by-item. Use when users need submission readiness checks, missing-item detection, or PRISMA flow validation.
version: 1.1
last_updated: 2026-03-30
domain: methodology
tokens: ~1400
triggers:
  - PRISMA
  - systematic review checklist
  - PRISMA 2020
requires_packages: []
reference_files:
  - reference/scientific_thinking/peer_review_checklist.md
  - reference/scientific_thinking/literature_review_phases.md
  - reference/medical_research/reporting-guideline-compliance-checker/hard-rules.md
pipeline_position: [4]
---

# Skill: PRISMA 2020 Compliance Check

## When to use

Use this skill when:
- You have an *existing* systematic review or meta-analysis manuscript and need to *check* it against PRISMA 2020
- Preparing manuscript for submission (compliance check)

**Not this skill:** To *conduct* a full systematic review or meta-analysis (protocol, search, pooling, etc.) use SKILL_meta-analysis. This skill is for the PRISMA *checklist compliance check* only.

## Prerequisites

- Systematic review or meta-analysis manuscript
- Access to PRISMA 2020 checklist

## Honesty and grounding checkpoints

- Label checklist conclusions as `[EXTRACTED]` when tied to explicit manuscript text/sections.
- Use `[VERIFIED]` only when each claimed item is cross-checked against PRISMA criteria.
- If a section cannot be assessed from available material, mark it `[BLANK]` and specify missing document parts.
- Do not mark an item complete without manuscript location evidence.

## Step-by-step procedure

1. **Load PRISMA checklist:**
   - See `.cursor/rules/reporting-prisma.mdc`
   - Or use official PRISMA 2020 checklist

2. **Go through each section:**
   - Title and Abstract (Item 1-2)
   - Introduction (Item 3-4)
   - Methods (Item 5-15)
   - Results (Item 16-24)
   - Discussion (Item 25-27)
   - Other Information (Item 28-29)

3. **Check each item:**
   - Mark as complete if present
   - Note location in manuscript
   - Identify missing items

4. **PRISMA Flow Diagram (MANDATORY):**
   - Create flow diagram showing:
     - Records identified
     - Records screened
     - Records excluded
     - Reports assessed
     - Studies included
   - Use PRISMA 2020 template
   - Include in manuscript

5. **Address missing items:**
   - Add missing information
   - Revise sections as needed
   - Ensure all applicable items completed

6. **Final check:**
   - Verify all items addressed
   - Check flow diagram included
   - Ensure checklist completed

## Verification

- [ ] All 27 PRISMA items checked
- [ ] PRISMA flow diagram included (MANDATORY)
- [ ] All applicable items completed
- [ ] Missing items addressed
- [ ] Checklist ready for submission

## Examples

**Input:** "Provjeri moj SR manuskript za PRISMA compliance prije slanja."  
**Output:** "Za svaki item navodim status i lokaciju u tekstu `[EXTRACTED]`; stavke bez dokaza ili bez flow dijagrama označavam `[BLANK]` uz točan popis što treba dopuniti."

## PRISMA Extensions (if applicable)

- **PRISMA-NMA:** Network meta-analysis
- **PRISMA-IPD:** Individual patient data
- **PRISMA-DTA:** Diagnostic test accuracy
- **PRISMA-ScR:** Scoping reviews

Use appropriate extension if applicable.

## Learning integration

- **task_type:** validation
- **log_fields:** items_checked, compliance_status
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules

- `.cursor/rules/reporting-prisma.mdc`
- `30_system/behavior_rules/03_scientific_writing.md`

## Learning integration

This skill logs:
- Common missing items
- User preferences for reporting
- Successful compliance patterns

Improves by:
- Learning common gaps
- Suggesting improvements
- Adapting to different review types

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
- [[literature_review_phases]]
- [[peer_review_checklist]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
