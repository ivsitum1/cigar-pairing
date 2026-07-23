---
name: wargame-blueprint
description: Wargame complex agent tasks with Action-Reaction-Counteraction blueprints before execution. Use before multi-step pipelines, orchestrator refactors, @autonomous runs, or when user says wargame, ARC blueprint, fight the mission on paper, failure counter-move.
version: 1.0
last_updated: 2026-07-08
domain: engineering
tokens: ~350
triggers:
  - wargame
  - ARC blueprint
  - action reaction counteraction
  - fight the mission on paper
  - failure counter-move
  - pre-mortem agent plan
requires_packages: []
reference_files:
  - 30_system/docs/WARGAME_BLUEPRINT.md
  - .agent/templates/wargame_blueprint.md
conflicts_with: []
disambiguation: Planning-only skill before execution; not grill-me (requirements) or swiss-cheese (validation after).
---

# Skill: Wargame blueprint

## When to use

- Task has ≥3 dependent tool steps or touches rules/MCP/hooks
- User enables `@autonomous` on a non-trivial change
- Prior attempt failed and you need structured recovery paths

## Procedure

1. Read `30_system/docs/WARGAME_BLUEPRINT.md`.
2. Copy template to `.agent/task/wargame_<YYYYMMDD>_<topic>.md`.
3. Fill ARC table: every planned action maps to expected observation, failure signal, counter-action.
4. Present blueprint to user for one-line confirm on high-risk steps (trust tier 3 tools).
5. Execute; on failure signal hit first counter-action from table before replanning.
6. Emit ATDP for each divergence: `python 40_operations/scripts/trajectory_emit.py --atdp ...`

## Honesty

- Counter-actions must be concrete (command, file, rollback), not "try again".
- If failure signal unknown, mark `[TO_CONFIRM]` and ask once.

## Related

- [[Wargame blueprint protocol]]
- `SKILL_grill-me.md` (requirements before design)
- `SKILL_swiss-cheese.md` (post-hoc validation)
