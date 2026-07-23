# Skill gap pipeline (system bridge)

Obsidian graph hub: [[Skill gap pipeline]] in `20_knowledge/wiki/concepts/Skill gap pipeline.md`.

Safety gates: [[Skill optimization safety gates]].

## Orchestration entrypoints (Python)

- `python 40_operations/scripts/skill_gap_ingest.py append-eval ...`
- `python 40_operations/scripts/skill_gap_ingest.py wiki-log ...`
- `python 40_operations/scripts/skill_gap_optimize_gate.py --json ...` — composite score, default cutoff **72** (`SKILL_GAP_OPTIMIZE_COMPOSITE_CUTOFF`); loop runs when `run_optimization_loop` is true (see `SKILL_GAP_OPTIMIZE_AUTO` / `SKILL_GAP_OPTIMIZE_LOOP`). Izlaz uključuje `reminders` kad je prag prođen ali arm nije postavljen (visok score, petlja off).
- `python 40_operations/scripts/skill_eval_runner.py --skill-id <id> --outputs ... --json`
- `python 40_operations/scripts/trajectory_rl_bridge.py --scan --json` — low `trajectory_score` runs from benchmark manifest → skill candidates ([[Trajectory reinforcement learning]])
- `python 40_operations/scripts/trajectory_emit.py` — manual/agent JSONL append ([TRAJECTORY_EMIT_PROTOCOL.md](TRAJECTORY_EMIT_PROTOCOL.md))
- `python 40_operations/scripts/contrastive_reflection.py` — success vs failure trajectory diff → error_log + wiki ([CONTRASTIVE_REFLECTION.md](CONTRASTIVE_REFLECTION.md))
- `python 40_operations/scripts/skill_trust_audit.py` / `skill_auditor.py` — trust tier and SkillGuard-lite audit ([TRUST_TIER_POLICY.md](TRUST_TIER_POLICY.md))

## Canonical agent rule

`.cursor/rules/00_orchestrator_agent.mdc` → section **Skill gap branch (automatic)**.
