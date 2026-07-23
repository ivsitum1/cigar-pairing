---
name: scholarly-iteration-loop
description: Use for spec-driven scholarly iterations with Swiss Cheese and progress logs; NOT for software Ralph/TDD loop (use ralph-loop) Triggers include: LOOP ON, LOOP OFF, run loop, research iteration loop, PROMISE COMPLETE loop, scholarly loop.
version: 1.1
last_updated: 2026-03-30
domain: scholarly
tokens: ~950
triggers:
  - LOOP ON
  - LOOP OFF
  - run loop
  - research iteration loop
  - PROMISE COMPLETE loop
  - scholarly loop
requires_packages: []
reference_files:
  - 30_system/docs/templates/scholarly-progress.template.txt
  - reference/scientific_thinking/evaluation_framework.md
pipeline_position: []
---

# Skill: Scholarly Iteration Loop (Research Analogue of Ralph)

## When to use

When the user enables **LOOP** mode (**LOOP ON**) for structured, spec-driven work on statistics and manuscript or book chapters. Default remains **LOOP OFF** unless the user says otherwise. This is **not** the software **Ralph** loop (`SKILL_ralph-loop`); it does not use TDD for application code.

## Scope

- Operates in the repo where `30_system/docs/research-spec.json` (or `.md`) and `30_system/docs/scholarly-progress.txt` live (or project `30_system/04_documentation/context/log.md` by team convention; prefer dedicated `scholarly-progress.txt` for clarity).
- If agent rules is only a **read-only** brain folder, do not write the spec here; work in the research project workspace.

## Mode switch

| Mode | Trigger | Behavior |
|------|---------|----------|
| **LOOP OFF** | Default or "LOOP OFF" | Normal collaboration; no multi-step autonomous loop. |
| **LOOP ON** | "LOOP ON", "run loop", optional iteration cap | One milestone per iteration: Select → Execute → Validate → Record. |
| **Exploration** | User says exploration for research | Spikes, extra models; log everything in progress file. |

**Loop controls (ECC continuous-agent-loop pattern):** default max **10** iterations per LOOP session unless user sets a cap; pause with one concrete blocker after **3** failed attempts on the same milestone; never skip Swiss Cheese on critical statistics milestones.

## Before each iteration

1. Read `30_system/docs/research-spec.json` (or `.md`) and append-only progress (`30_system/docs/scholarly-progress.txt` or agreed log).
2. Pick the highest-priority milestone with `passes: false` and satisfied `blocked_by`.

## Step 1 — Select

One milestone only per iteration.

## Step 2 — Execute

- **Statistics:** Follow project stats rules and `statistics-test-selection` / design-appropriate SKILL (e.g. meta-analysis, test-selection). Reproducible code, effect sizes + CI, assumptions where required.
- **Writing:** Use **SKILL_manuscript-structure**, reporting checklists as needed; no fabricated citations.

## Step 3 — Validate (not unit 40_operations/tests)

- **Critical analyses / primary outcome / pooled estimates / transition to writing:** run or apply **SKILL_swiss-cheese** when mandatory per `verification.mdc` and orchestrator.
- Self-assessment ≥9/10 where project rules require it.
- Numbers in text match tables; claims match cited sources.

## Step 4 — Record

1. Set completed milestone (and related spec items) to `passes: true`.
2. **Append** to `30_system/docs/scholarly-progress.txt` (see `30_system/docs/templates/scholarly-progress.template.txt`): datetime, milestone id, summary, commands, open risks.
3. Git commit when appropriate and repo allows.

## Step 5 — Fresh context

After a large milestone, suggest a new chat or clear context to avoid context rot.

## Exit

Output **`PROMISE COMPLETE`** when all tracked milestones in the spec are passing, unless the user expands scope.

## Stop conditions

Stop and ask the human if: drift from the spec; inconsistency unresolved after **two** focused attempts; or missing ethical/citation integrity.

## Distinction from engineering Ralph

| Engineering (`ralph-loop`) | Scholarly (this skill) |
|----------------------------|-------------------------|
| `30_system/docs/prd.json`, TDD | `30_system/docs/research-spec.json`, validation + reproducibility |
| `harness_tdd.mdc` | Swiss Cheese, stats workflow, reporting checklist |

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "LOOP ON: iteracija 2 nakon recenzijskih komentara."  
**Output:** "Swiss Cheese prije zatvaranja iteracije `[VERIFIED]`; promjene u MS `[EXTRACTED]` iz diffa; neusklađen spec `[BLANK]`."

## Verification

- [ ] Swiss Cheese invoked when mandatory for the milestone type
- [ ] Progress file append-only; spec updated
- [ ] LOOP OFF unless user re-enables

---

**Reference:** `30_system/docs/SCHOLARLY_WORKFLOW.md`, `SKILL_write-research-spec.md`, `SKILL_swiss-cheese.md`, `.cursor/rules/harness_tdd.mdc` (only if the milestone includes code with 40_operations/tests)

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[scholarly-progress.template]]
- [[evaluation_framework]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
