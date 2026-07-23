# Trajectory RL policy (agent-rules brain)

Bridge document for trajectory-first reinforcement-style learning **without** LLM fine-tuning. Canonical DL boundaries: [DEEP_LEARNING_POLICY.md](DEEP_LEARNING_POLICY.md).

## Model

| RL concept | Implementation here |
|------------|---------------------|
| State | Memory signals, benchmark traces, skill id |
| Action | Single discrete patch to `SKILL_*.md` (or rule proposal) |
| Reward | `composite_score` delta (skill eval pass rate + optional `trajectory_score`) |
| Policy | Text in skills/rules, not neural weights |

## Data flow

1. **Emit** — `90_archive/artifacts/<run_id>/trajectory.jsonl` per [TRAJECTORY_EMIT_PROTOCOL.md](TRAJECTORY_EMIT_PROTOCOL.md); hooks: `.cursor/hooks/trajectory_lifecycle.py`.
2. **Score** — `40_operations/scripts/trajectory_eval_runner.py` → `trajectory_score` in `[0,1]`.
3. **Benchmark** — `40_operations/scripts/run_agent_benchmark.py` + manifest (e.g. [AGENT_BENCHMARK_RL_DEMO.json](AGENT_BENCHMARK_RL_DEMO.json)).
4. **Candidates** — `trajectory_rl.candidates.scan_manifest` / `40_operations/scripts/trajectory_rl_bridge.py --scan`.
5. **Update** — `40_operations/scripts/self_eval_learning_loop.py` (accept/revert) and optional [SKILL_OPTIMIZATION_AGENT.md](SKILL_OPTIMIZATION_AGENT.md) for binary evals.

## Phase memory consolidation

Inspired by NotebookLM REC/phase-transition themes (UNVERIFIED empirically). Implementation:

- `trajectory_rl.emit.append_event` increments `event_count` in `.agent/memory/trajectory_session.json`
- When `event_count % TRAJECTORY_CONSOLIDATE_THRESHOLD == 0` (default **25**), append compact summary to `.agent/MEMORY.md`
- MCP prescreen hints logged on failed `postToolUse` via `trajectory_lifecycle` hook

See [LIFEHARNESS_4_LAYER.md](LIFEHARNESS_4_LAYER.md) Layer 4.

## Episodic-first policy

Inspired by Beyond Intelligence / MemFail themes (diagnostic memory failures, not aggregate recall alone).

1. **Trajectory is primary evidence** — `trajectory.jsonl` and raw hook payloads outrank abstracted summaries for debugging and learning.
2. **MEMORY.md consolidation** — append compact summaries only on **milestones** (pipeline phase complete, user `@sync context`, or `event_count % TRAJECTORY_CONSOLIDATE_THRESHOLD == 0`). Do not batch-consolidate mid-session.
3. **No force-abstract** — do not rewrite episodic traces into `.agent/MEMORY.md` without eval gate (`skill_gap_optimize_gate.py` or explicit user approval).
4. **Failure attribution** — tag ingest with `failure_mode:summary|storage|retrieval|unknown` when promoting memory observations (see [MEMORY_MIXTURE_ROUTING.md](MEMORY_MIXTURE_ROUTING.md)).

## Composite reward

When `trajectory_trace` is present on a learning candidate:

```
composite = 0.30 * (trajectory_score * 100)
          + 0.385 * eval_pass_rate_pct
          + 0.175 * tests_score
          + 0.07 * lint + 0.07 * stability
```

(Weights renormalized in code via `ScoreWeights.normalized()`.)

Accept only if `delta >= accept_threshold` (default `+0.10` on 0–100 scale). Otherwise revert patch.

## Skill-gap integration

After user correction:

1. `skill_gap_ingest.py append-eval` (unchanged)
2. `skill_gap_optimize_gate.py` (unchanged arming)
3. Optional: `python 40_operations/scripts/trajectory_rl_bridge.py --propose-learning`

Trajectory failures from the demo manifest auto-merge into `build_candidates()` in the learning loop.

## Safety

- No PHI in trajectory payloads ([Skill optimization safety gates](../20_knowledge/wiki/concepts/Skill optimization safety gates.md)).
- No auto-apply on `core-principles.mdc` or `00_orchestrator_agent.mdc`.
- Clinical gold stays human-verified; trajectory only checks **process** (tools, plan), not medical truth.

## Commands

```bash
python 40_operations/scripts/trajectory_emit.py --init-session --json
python 40_operations/scripts/run_agent_benchmark.py --manifest 30_system/docs/AGENT_BENCHMARK_RL_DEMO.json --json
python 40_operations/scripts/trajectory_rl_bridge.py --scan --json
python 40_operations/scripts/self_eval_learning_loop.py --mode propose --json
```

## Related

- [TRAJECTORY_EVAL_SPEC.md](TRAJECTORY_EVAL_SPEC.md)
- [SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md](SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md)
- [autoresearch_hybrid_spec.md](autoresearch_hybrid_spec.md)
- [SKILL_GAP_PIPELINE.md](SKILL_GAP_PIPELINE.md)
- Wiki: [[Trajectory reinforcement learning]]
