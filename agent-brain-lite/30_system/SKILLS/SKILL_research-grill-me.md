---
name: research-grill-me
description: Use for interview and design-tree alignment before a research spec or manuscript; NOT for software Grill-me before PRD (use grill-me) Triggers include: research grill-me, scholarly alignment, PICO interview, clarify study design, before research spec, manuscript scope.
version: 1.1
last_updated: 2026-03-30
domain: scholarly
tokens: ~550
triggers:
  - research grill-me
  - scholarly alignment
  - PICO interview
  - clarify study design
  - before research spec
  - manuscript scope
  - describe my task
  - opisujem zadatak
requires_packages: []
reference_files:
  - reference/scientific_thinking/hypothesis_generation_workflow.md
pipeline_position: []
---

# Skill: Research Grill-me (Shared Understanding for Scholarship)

## When to use

Before drafting a **research spec** or locking analysis and writing plans. Prevents rushing into statistics or prose when the study type, population, comparisons, and deliverables are unclear. Distinct from **SKILL_grill-me** (software design tree).

## Objective

Reach **shared understanding** with the user on: research question, study design, data sources, target outlet (journal type or book chapter), reporting standard (CONSORT, PRISMA, STROBE, etc.), and what “done” means.

## Method

0. **If `30_system/docs/research-spec.json` (or `.md`) is missing** and the user is describing a task: treat this as the opening phase. **Offer to create or draft** that file together using **SKILL_write-research-spec** (templates under `30_system/docs/templates/`). You can grill-me and fill the spec in the same session; the spec file is the concrete anchor for the rest of the conversation.

1. **Design tree (research):** Walk branches: PICO or equivalent, causal vs descriptive claims, primary outcome and time point, comparison group, handling of confounding/missing data, figure and table plan at a high level.
2. **Sources first:** If the answer is in the user’s protocol, dataset codebook, or repo docs, **read those** before asking.
3. **Unknown unknowns:** Surface risks (e.g. post-hoc outcomes, weak comparison) explicitly.
4. **Hypothesis framing (optional):** When RQs are still exploratory, load `reference/scientific_thinking/hypothesis_generation_workflow.md` for competing hypotheses and testability checks (do not skip PICO/spec steps).

## Outcome

Short agreed summary, a **draft `30_system/docs/research-spec.json`** with explicit TBDs where needed, or readiness to refine **SKILL_write-research-spec**. Early drafts are encouraged; unresolved items stay labeled TBD until closed.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Radim meta-analizu X; nije mi jasan PICO i primarni ishod."  
**Output:** "PICO i ishod razjašnjavam pitanjima; kada korisnik potvrdi, zapisujem `[EXTRACTED]`; bez odgovora ostaje `[BLANK]`."

## Verification

- [ ] Study type and primary comparison stated or deferred with label
- [ ] Reporting checklist family identified where applicable
- [ ] No redundant questions answerable from loaded project files

---

**Reference:** `SKILL_write-research-spec.md`, `30_system/behavior_rules/22_pipeline_and_refinement.md`, `30_system/docs/SCHOLARLY_WORKFLOW.md`

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[hypothesis_generation_workflow]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
