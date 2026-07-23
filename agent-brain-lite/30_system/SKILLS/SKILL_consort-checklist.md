---
name: consort-checklist
description: Use for CONSORT compliance check on RCT manuscripts; for writing RCT structure use rct-manuscript. Triggers include: CONSORT, RCT checklist, randomized trial reporting.
version: 1.1
last_updated: 2026-03-30
domain: methodology
tokens: ~1400
triggers:
  - CONSORT
  - RCT checklist
  - randomized trial reporting
requires_packages: []
reference_files:
  - reference/consort_checklist_items.md
  - reference/medical_research/reporting-guideline-compliance-checker/hard-rules.md
pipeline_position: [4]
---

# Skill: CONSORT Compliance Check

## When to use

Use this skill when:
- Writing randomized controlled trial (RCT)
- Need to ensure CONSORT 2010 compliance
- Preparing manuscript for submission

## Prerequisites

- RCT manuscript
- Access to CONSORT 2010 checklist

## Step-by-step procedure

1. **Load CONSORT checklist:**
   - See `.cursor/rules/reporting-consort.mdc`
   - Or use official CONSORT 2010 checklist

2. **Go through each section:**
   - Title and Abstract (Item 1a-1b)
   - Introduction (Item 2a-2b)
   - Methods (Item 3a-12)
   - Results (Item 13a-18)
   - Discussion (Item 19-21)
   - Other Information (Item 22-25)

3. **CONSORT Flow Diagram (MANDATORY):**
   - Create flow diagram showing:
     - Enrollment
     - Allocation
     - Follow-up
     - Analysis
   - Use CONSORT 2010 template
   - Include in manuscript

4. **Check each item:**
   - Mark as complete if present
   - Note location in manuscript
   - Identify missing items
   - **When listing gaps:** Always name them explicitly (e.g. **allocation concealment** if not described; **protocol registration** / PROSPERO / ClinicalTrials.gov; **sample size** calculation). Use wording such as "nedostaje", "nije naveden", "missing", "incomplete", "nepotpun". Reference CONSORT items (e.g. item 1b, sequence generation). Never state that all items are present ("sve stavke su prisutne", "zadovoljava sve") without a full item-by-item check.
   - **Open-label RCT:** Acknowledge "open-label"; mention performance bias and detection bias; recommend blinding of outcome assessor where applicable. Use "primjenjivo", "nije primjenjivo", "applicable" as appropriate. Do not claim "blinding je obavezan" or "studija ne zadovoljava" when blinding is impossible by design.
   - **Claims of full compliance:** Do not endorse "fully compliant" or "u potpunosti zadovoljava" without verifying all items; note common gaps (protocol registration, sample size, etc.) and use "insufficient", "nedovoljan", "provjeriti".

5. **Check CONSORT extensions (if applicable):**
   - **CONSORT-NPT:** Non-pharmacological treatments
   - **CONSORT-Cluster:** Cluster randomized trials
   - **CONSORT-Non-inferiority:** Non-inferiority trials
   - **CONSORT-Pragmatic:** Pragmatic trials
   - **CONSORT-Pilot:** Pilot trials

6. **Address missing items:**
   - Add missing information
   - Revise sections as needed
   - Ensure all applicable items completed

7. **Final check:**
   - Verify all 25 items addressed
   - Check flow diagram included (MANDATORY)
   - Check extensions if applicable
   - Ensure checklist ready for submission

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Je li RCT manuskript kompletan za CONSORT prije slanja?"  
**Output:** "Za svaku stavku: status i lokacija u MS `[EXTRACTED]`; ako tekst nije dostupan, stavke su `[BLANK]` uz popis što učitati."

## Verification

- [ ] All 25 CONSORT items checked
- [ ] CONSORT flow diagram included (MANDATORY)
- [ ] Extensions checked (if applicable)
- [ ] All applicable items completed
- [ ] Missing items addressed
- [ ] Checklist ready for submission

## Learning integration

- **task_type:** validation
- **log_fields:** items_checked, compliance_status
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules

- `.cursor/rules/reporting-consort.mdc`
- `30_system/behavior_rules/06_study_types.md` (RCT section)

## Learning integration

This skill logs:
- Common missing items
- Extension-specific patterns
- Successful compliance strategies

Improves by:
- Learning common gaps
- Suggesting extension-specific improvements
- Adapting to different trial types

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[consort_checklist_items]]
- [[hard-rules]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
