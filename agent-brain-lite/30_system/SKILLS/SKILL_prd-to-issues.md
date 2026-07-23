---
name: prd-to-issues
description: Use to break a PRD into vertical slices and blockers; load after write-prd when planning execution Triggers include: PRD to issues, vertical slice, vertical slices, decompose PRD, tracer bullet, task breakdown.
version: 1.1
last_updated: 2026-03-30
domain: engineering
tokens: ~600
triggers:
  - PRD to issues
  - vertical slice
  - vertical slices
  - decompose PRD
  - tracer bullet
  - task breakdown
requires_packages: []
reference_files: []
pipeline_position: []
---

# Skill: PRD-to-Issues (Vertical Slices)

## When to use

After a PRD exists (`30_system/docs/prd.json` or `30_system/docs/prd.md`). Converts requirements into **small, executable vertical slices** instead of horizontal layers (e.g. "only DB" then "only API").

## Principles

1. **Vertical slice:** Each task cuts through the stack needed to deliver user-visible or integration-verifiable value (e.g. DB + API + UI slice, or end-to-end script + test for a pipeline).
2. **Tracer bullets:** Order work to **reduce unknown unknowns** early: spikes and integration-risk tasks before polish.
3. **Blocking:** Record explicit dependencies (e.g. Task B blocked by Task A). Encode in PRD `issues[].blocked_by` when using JSON, or a short table in Markdown.
4. **One feature at a time:** Slices should be small enough for a single Ralph iteration or a short session.

## Procedure

1. Read the current PRD.
2. List candidate slices; merge or split until each slice is independently valuable and testable.
3. Assign priority (P0, P1, …) and blockers.
4. Update `30_system/docs/prd.json` (recommended: `issues` array) or add a **Tasks** section to `30_system/docs/prd.md` with the same information.
5. Ensure each slice still maps to user stories and keeps `passes` accurate at the story level when slices complete.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Razbij PRD u vertical slice-ove za prvi sprint."  
**Output:** "Slice-ovi vezani uz `passes` u PRD-u `[EXTRACTED]`; ovisnosti `[INFERRED]`; nedostajući acceptance `[BLANK]`."

## Verification

- [ ] No slice is "horizontal only" unless the PRD is infra-only and user agreed
- [ ] Integration-risk items appear early where possible
- [ ] Blockers are explicit

---

**Reference:** `30_system/SKILLS/SKILL_ralph-loop.md`, `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
