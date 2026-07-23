---
name: ralph-loop
description: Use for PRD-driven iterative execution with TDD and progress logging; NOT for research statistics pipelines unless user explicitly names Ralph mode Triggers include: Ralph ON, Ralph OFF, Ralph loop, Ralph Wiggum, PROMISE COMPLETE, Exploration Mode.
version: 1.1
last_updated: 2026-03-30
domain: engineering
tokens: ~900
triggers:
  - Ralph ON
  - Ralph OFF
  - Ralph loop
  - Ralph Wiggum
  - PROMISE COMPLETE
  - Exploration Mode
  - autonomous execution
requires_packages: []
reference_files:
  - 30_system/docs/templates/progress.template.txt
pipeline_position: []
---

# Skill: Ralph Wiggum Loop (Autonomous Execution)

## When to use

When the user explicitly enables **Ralph mode** or asks for iterative PRD-driven execution with TDD and external memory. Default chat behavior remains **Ralph OFF** unless the user says otherwise.

## Scope and workspace

- Operate on the **application repository** where `30_system/docs/prd.json` (or `30_system/docs/prd.md`) and `30_system/docs/progress.txt` live.
- If the current workspace is **agent rules as read-only brain**, do not mutate brain files; instruct the user to run Ralph in the app project or switch workspace.

## Mode switch

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Ralph OFF** | Default, or "Ralph OFF" | Normal pair programming. Use Grill-me / Write-PRD to prepare work; no multi-step autonomous loop. |
| **Ralph ON** | "Ralph ON", "Run Ralph loop", optional "N iterations" | Execute one slice per iteration: Select → TDD → Record → suggest fresh context. |
| **Exploration Mode** | User says "Exploration Mode" | Spikes, MVPs, research; still append learnings to `30_system/docs/progress.txt`; lower bar for throwaway code only if user accepts. |

## Before each iteration

1. Read `30_system/docs/prd.json` (or `30_system/docs/prd.md`) and **append-only** `30_system/docs/progress.txt`.
2. Pick the **highest-priority** incomplete item (`passes: false` or unchecked).

## Step 1 — Select

Choose one task or story; do not parallelize multiple features in one iteration.

## Step 2 — TDD (mandatory)

Follow `.cursor/rules/harness_tdd.mdc`:

1. **Red:** Write a failing test that expresses the requirement.
2. **Green:** Minimal implementation to pass.
3. **Refactor:** Only with all relevant tests green.

**Anti-poisoning:** Do not weaken tests or change assertions to fake success. If the test does not encode the requirement, fix the test **conceptually** only with the same user-visible behavior in mind.

## Step 3 — Record

After the slice is truly done:

1. Set the corresponding PRD entries to `"passes": true` (or mark in Markdown).
2. **Append** (never overwrite) to `30_system/docs/progress.txt` using the format in `30_system/docs/templates/progress.template.txt`: timestamp, task id, summary, commands run, follow-ups.
3. **Git:** Commit with a message that names the slice (when git is available and the repo is not read-only).

## Step 4 — Fresh context

After a large change, **suggest** a new chat or context clear so the next iteration does not sit in a degraded "dumb zone" (very long threads).

## Exit criteria

- When all PRD-tracked items are `passes: true`, output **`PROMISE COMPLETE`** and stop the loop unless the user adds scope.
- **Stop and escalate** if tests stay red after **two** focused fix iterations, or if implementation drifts from the PRD: ask the human before continuing.

## Risk controls

- **Token bleed:** Keep PRD and progress entries short and structured.
- **Atomic focus:** One feature or slice per iteration.
- **No unbounded autonomy:** Respect iteration limits if the user sets them.

## MCP (optional)

When configured in the project’s `.cursor/mcp.json`, prefer **filesystem** / **git** for PRD and progress. **Playwright** (UI verification) and **GitHub Issues** (Kanban) are optional; document usage in `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md` — add servers locally if needed.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Ralph ON: issue #12 iz PRD-a, TDD."  
**Output:** "Log i testovi `[VERIFIED]` iz izvršenja; zeleni suite prije PROMISE COMPLETE; ako padaju testovi, završetak `[BLANK]`."

## Verification

- [ ] harness_tdd.mdc honored (red → green → refactor)
- [ ] PRD and progress updated; progress is append-only
- [ ] Ralph OFF behavior restored unless user asked for another iteration

---

**Reference:** `.cursor/rules/harness_tdd.mdc`, `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`, `30_system/SKILLS/SKILL_write-prd.md`

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[progress.template]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
