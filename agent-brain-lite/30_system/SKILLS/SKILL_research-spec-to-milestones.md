---
name: research-spec-to-milestones
description: Use to break research spec into milestones for statistics and writing; NOT for software vertical slices (use prd-to-issues) Triggers include: research milestones, decompose research spec, spec to milestones, analysis milestones, chapter order, tracer bullet research.
version: 1.1
last_updated: 2026-03-30
domain: scholarly
tokens: ~600
triggers:
  - research milestones
  - decompose research spec
  - spec to milestones
  - analysis milestones
  - chapter order
  - tracer bullet research
requires_packages: []
reference_files: []
pipeline_position: []
---

# Skill: Research-Spec-to-Milestones (Ordered Work Units)

## When to use

After `30_system/docs/research-spec.json` (or `.md`) exists. Breaks the spec into **ordered milestones** that mix analysis and writing where useful (vertical integration for scholarship: e.g. “Table 2 + Results paragraph” rather than “all tables first, all text later”), unless the user prefers a strict phase order.

## Principles

1. **Integration risk first:** Early milestones that validate data pipeline, primary analysis, or review screening reduce unknown unknowns (“tracer bullets”).
2. **Blocking:** Encode `blocked_by` (milestone ids) when B cannot start until A is done (e.g. sensitivity analyses after primary).
3. **One focus per iteration:** Size milestones for one **scholarly iteration** (see **SKILL_scholarly-iteration-loop**).
4. **Checklist linkage:** Map milestones to CONSORT/PRISMA/STROBE items when applicable.

## Procedure

1. Read the research spec.
2. List milestones; split or merge until each is verifiable and has a clear “done” definition.
3. Update `milestones` in `30_system/docs/research-spec.json` or a **Milestones** section in `30_system/docs/research-spec.md`.
4. Align `passes` on parent sections when milestones complete.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Od research-spec.json napravi redoslijed milestonea: analiza pa pisanje."  
**Output:** "Milestone-i vezani uz `passes` u specu `[EXTRACTED]`; trajanje `[ASSUMPTION]` ako nije u specu."

## Verification

- [ ] Dependencies explicit
- [ ] No milestone is purely “horizontal” without user agreement (e.g. all statistics with zero draft text if they asked for integrated delivery)

---

**Reference:** `SKILL_scholarly-iteration-loop.md`, `30_system/behavior_rules/22_pipeline_and_refinement.md`

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
