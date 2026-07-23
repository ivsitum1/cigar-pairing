# Wargame blueprint protocol

Action–Reaction–Counteraction planning before complex agent tasks (from NotebookLM *The AI Frontier news*, Fable 5 wargaming).

## When to use

- Multi-step pipeline (`@pipeline`, MIXED STATISTICS→WRITING)
- Refactors touching orchestrator, hooks, or MCP
- Any task with ≥3 tool calls and irreversible file writes

## Workflow

1. **Use Tier P** (planner model) to draft the blueprint — see `model-tier-routing.mdc`.
2. Copy `.agent/templates/wargame_blueprint.md` → `.agent/task/wargame_<run_id>.md`
3. Fill goal, acceptance criteria, and the ARC table (action / observation / failure / counter)
4. **Switch to Tier E** for execution; follow the table; on failure signal, apply counter-action before improvising
5. Log divergences via ATDP (`trajectory_emit.py --atdp`)

## Skill

Load `SKILL_wargame-blueprint.md` when user says "wargame", "ARC blueprint", or before `@autonomous` complex runs.

## Related

- [[TRAJECTORY_EMIT_PROTOCOL]]
- [[Skill trust tiers]]
- `30_system/SKILLS/SKILL_wargame-blueprint.md`
