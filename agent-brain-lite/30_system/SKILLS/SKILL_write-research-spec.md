---
name: write-research-spec
description: Use for research/manuscript specification with passes flags (research-spec.json); NOT for software PRD (use write-prd) Triggers include: research spec, research-spec.json, manuscript spec, scholarly spec, SAP outline, write research spec.
version: 1.1
last_updated: 2026-03-30
domain: scholarly
tokens: ~700
triggers:
  - research spec
  - research-spec.json
  - manuscript spec
  - scholarly spec
  - SAP outline
  - write research spec
  - help create research-spec
  - make research-spec.json
requires_packages: []
reference_files:
  - 30_system/docs/templates/research-spec.schema.json
  - 30_system/docs/templates/research-spec.example.json
  - reference/scientific_thinking/hypothesis_generation_workflow.md
  - reference/scientific_thinking/evaluation_framework.md
pipeline_position: []
---

# Skill: Write-Research-Spec (Source of Truth for Analysis and Writing)

## When to use

After **SKILL_research-grill-me** (or in parallel with it). Produces a durable **research specification** as external memory: analogous to a software PRD, but for manuscripts, chapters, and statistical analysis plans. Not the same as **SKILL_write-prd** (product requirements for code).

## First steps when the user starts describing a task

When the user begins to describe a research or writing task (even before everything is clear):

1. **Check** whether `30_system/docs/research-spec.json` (or `30_system/docs/research-spec.md`) already exists in the **active project** repo.
2. **If missing:** Do **not** wait for a full grill-me. Immediately load `30_system/docs/templates/research-spec.example.json` and `30_system/docs/templates/research-spec.schema.json`, then **help the user co-create** the file: copy the example structure, fill in what you can from their description, leave `passes: false` on all trackable rows, and mark unknowns as `"TBD"` or short placeholders.
3. **Ask the minimum follow-up questions** needed to replace TBDs (primary outcome, design, comparator, or review type).
4. **Write** the result to `30_system/docs/research-spec.json` (or `.md`) in the project root when the user has agreed or when the draft is useful enough to iterate.

This makes `research-spec.json` an explicit early deliverable, not something only created after a long interview.

## Scope

- Default paths (project repo root): `30_system/docs/research-spec.json` **or** `30_system/docs/research-spec.md`.
- JSON recommended for `passes` flags; Markdown acceptable with explicit checkboxes per section.

## Structure (required content)

1. **Research question & background:** One clear question; scope and novelty in brief.
2. **Design & PICO (or PRISMA-style scope for reviews):** Population, intervention/exposure, comparator, outcomes; or review question and synthesis type.
3. **Analysis plan (SAP summary):** Primary analysis, secondary, pre-specified sensitivity; software and reproducibility notes (e.g. `set.seed`, paths).
4. **Writing & reporting plan:** Target structure (IMRaD, chapter outline), checklist (CONSORT / PRISMA / STROBE) as applicable.
5. **Milestones / deliverables:** Trackable items (tables, figures, sections) each with `"passes": false` until completed.

Before marking milestones complete, optional quality pass using `reference/scientific_thinking/evaluation_framework.md` (ScholarEval dimensions: problem, methods, analysis, writing).

## Loop iteration compatibility (research-spec + LOOP ON)

- Every trackable milestone MUST include `"passes": false` until verified.
- Optional `milestones[]` with `blocked_by`, `maps_to_sections` (see `30_system/docs/templates/research-spec.schema.json`).

## Procedure

1. Read `30_system/docs/templates/research-spec.example.json` and `30_system/docs/templates/research-spec.schema.json`.
2. Create or update `30_system/docs/research-spec.json` (or `.md`) in the **active research project** (not in a read-only brain-only attach of agent rules). If the file did not exist, say so and confirm the path you are creating.
3. Keep the spec concise to reduce token bleed in long sessions.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Izgradi research-spec.json za meta-analizu HRQoL ishoda."  
**Output:** "`passes`, PICO, definicije ishoda `[EXTRACTED]` nakon usklađivanja; verzije paketa `[VERIFIED]` iz `renv.lock` ako postoji."

## Verification

- [ ] Primary outcome and analysis approach are identifiable
- [ ] `passes` (or checkboxes) exist for iteration tracking
- [ ] Distinguished from software PRD (`write-prd`)

---

**Reference:** `SKILL_research-spec-to-milestones.md`, `30_system/docs/SCHOLARLY_WORKFLOW.md`, `SKILL_swiss-cheese.md`

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
- [[evaluation_framework]]
- [[research-spec.schema]]
- [[research-spec.example]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
