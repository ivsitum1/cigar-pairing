# Trajectory emit protocol

How agents and hooks record live-run trajectories for [TRAJECTORY_EVAL_SPEC.md](TRAJECTORY_EVAL_SPEC.md) and [TRAJECTORY_RL_POLICY.md](TRAJECTORY_RL_POLICY.md).

## Artifact path

Each run writes:

`90_archive/artifacts/<run_id>/trajectory.jsonl`

Session pointer: `.agent/memory/trajectory_session.json` (`run_id`, `trace_path`).

## Event format

One JSON object per line:

```json
{"run_id":"run_20260527_demo_001","ts":"2026-05-27T12:00:00+00:00","event_type":"tool_selected","payload":{"selected_tool":"pubmed/search","expected_tool":"pubmed/search","plan_step_id":"lit_search"}}
```

Supported `event_type` values: `plan_step`, `tool_selected`, `tool_args`, `tool_result`, `state_snapshot`, `final_answer`, `atdp_step`.

## ATDP-lite (`atdp_step`)

Agent Trajectory Data Protocol tuple for replay and contrastive reflection. One object per line inside `payload`:

```json
{
  "run_id": "run_20260708_080000_ab12",
  "ts": "2026-07-08T08:00:00+00:00",
  "event_type": "atdp_step",
  "payload": {
    "o": "tool_result success=true",
    "h": "plan_step=session_start",
    "a": "pubmed/search_pubmed",
    "y": "success",
    "r": 1,
    "m": {"hook": "postToolUse", "tool_correct": true}
  }
}
```

| Field | Meaning | PHI |
|-------|---------|-----|
| `o` | Observation (tool output summary) | Must be scrubbed |
| `h` | Hidden status (plan id, prescreen hint) | No patient identifiers |
| `a` | Action (tool/server name) | Safe |
| `y` | Outcome label | Scrubbed |
| `r` | Reward (+1/-1 or float) | Safe |
| `m` | Metadata (latency, model id, harness version) | Technical only |

Implementation: `40_operations/python/trajectory_rl/atdp.py`, `append_atdp_event()` in `emit.py`. Hooks emit on `postToolUse`.

**Forbidden in `m`:** `patient_name`, `mrn`, `oib`, `free_text_note`, `user_prompt`.

## Safety (no PHI)

Payloads must **not** contain patient identifiers, free-text clinical notes, or full user prompts. Allowed:

- tool/server names
- booleans (`schema_valid`, `tool_correct`, `context_ok`)
- hashed or relative paths only when needed
- `expected_tool` for benchmark golden runs

## Agent obligation (complex runs)

At the start of a multi-tool task, emit a `plan_step` with `has_goal`, `has_rationale`, `has_acceptance_criteria` (or `quality_score`).

After each tool use, ensure `tool_selected` includes `expected_tool` when running a benchmark case.

At task end, optional `final_answer` with `golden_set_score` (0–1) for benchmark manifests.

## CLI

```bash
python 40_operations/scripts/trajectory_emit.py --init-session --json
python 40_operations/scripts/trajectory_emit.py --event-type plan_step --payload '{"step_id":"s1","has_goal":true,"has_rationale":true,"has_acceptance_criteria":true}'
python 40_operations/scripts/trajectory_emit.py --atdp --observation "esearch 35 hits" --action "pubmed/search_pubmed" --outcome success --reward 1
```

Disable hooks/emit: `TRAJECTORY_RL_DISABLED=1`.

## Hooks

[`.cursor/hooks/trajectory_lifecycle.py`](../.cursor/hooks/trajectory_lifecycle.py) runs on `sessionStart`, `postToolUse`, `sessionEnd`, and `stop` (see [`.cursor/hooks.json`](../.cursor/hooks.json)).

## Related

- [14_learning_loop.md](../behavior_rules/14_learning_loop.md) — LEARNING_BLOCK for task outcomes
- [AGENT_BENCHMARK_SCHEMA.md](AGENT_BENCHMARK_SCHEMA.md)
- `40_operations/scripts/trajectory_eval_runner.py`
