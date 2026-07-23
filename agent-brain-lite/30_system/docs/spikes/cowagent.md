# Spike: CowAgent memory and self-evolve

**Repo:** https://github.com/zhayujie/CowAgent  
**Machine US:** US-26 | **W27 verdict:** approved_spike  
**Notebook bridge:** loop-of-loops self-improving KB

## Take for agent-rules

| Pattern | Adopt | Notes |
|---------|-------|-------|
| Self-evolving skill/memory | **Partial** | Already: `self_harness_propose.py`, error_log, skill gap optimize |
| Dual registry agent+verifier | **Partial** | SkillLens / orchestrator-skilllens |
| Autonomous rule rewrite | **Reject** | machine-autonomy.mdc |

## Map to repo

- `memory_engine/` scoped SQLite
- `.cursor/errors/error_log.jsonl`
- Human gate every 3rd self-harness iteration (Harness SkillTree policy)

## Next step

Document overlap in `LOOP_OF_LOOPS_MAP.md` after grill gate.
