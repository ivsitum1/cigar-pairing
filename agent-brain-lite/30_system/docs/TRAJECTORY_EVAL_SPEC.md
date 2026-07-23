# Trajectory Eval Specification

## Purpose

This specification defines trajectory-first evaluation for live agent runs.
The goal is to score decisions across the full execution path, not only the final answer.

## Event Model

Each run is a JSONL stream where each line is one event object.

Required top-level fields:

- `run_id` (string)
- `ts` (ISO-8601 timestamp)
- `event_type` (string)
- `payload` (object)

Supported `event_type` values:

- `plan_step`
- `tool_selected`
- `tool_args`
- `tool_result`
- `state_snapshot`
- `final_answer`

## Trajectory Metrics

All metrics are normalized to `[0.0, 1.0]`.

### 1) Tool Correctness

Definition:

- Did the agent choose the expected tool for the subtask?

Data contract:

- `tool_selected.payload.selected_tool`
- `tool_selected.payload.expected_tool` (optional but recommended)

Scoring:

- If `expected_tool` exists, score is exact-match ratio.
- If missing, fallback to `tool_selected.payload.tool_correct` if provided.
- If no evidence exists, metric is `null` and reported as missing signal.

### 2) Argument Correctness

Definition:

- Were tool parameters valid against schema/constraints?

Data contract:

- `tool_args.payload.schema_valid` (preferred boolean)
- or `tool_args.payload.args_valid` (boolean fallback)

Scoring:

- Mean of validity flags over all `tool_args` events.
- If no evidence exists, metric is `null`.

### 3) Plan Quality

Definition:

- Was execution strategy coherent before actions started?

Data contract:

- `plan_step.payload.has_goal` (bool)
- `plan_step.payload.has_rationale` (bool)
- `plan_step.payload.has_acceptance_criteria` (bool)
- optional `plan_step.payload.quality_score` (0-1 float)

Scoring:

- If `quality_score` present, mean of those values.
- Else deterministic structural score over required fields:
  - +1/3 for goal
  - +1/3 for rationale
  - +1/3 for acceptance criteria

### 4) Plan Adherence

Definition:

- Did the agent execute actions aligned with its declared plan?

Data contract:

- Plan declaration: `plan_step.payload.step_id`
- Execution mapping: `tool_selected.payload.plan_step_id`
- optional `tool_selected.payload.unplanned` (boolean)

Scoring:

- Executed steps linked to declared plan steps / total executed steps.
- Unplanned flagged events are counted as non-adherent.

### 5) Step Efficiency

Definition:

- How much unnecessary reasoning/tool churn happened?

Data contract:

- optional `run_metadata.ideal_step_count`
- per event optional `payload.unnecessary`

Scoring:

- If `ideal_step_count` exists:
  - `max(0, 1 - (actual_steps - ideal_steps) / max(ideal_steps,1))`
- Else:
  - `1 - (unnecessary_events / total_step_events)`

### 6) State Tracking

Definition:

- Did context and memory survive across steps?

Data contract:

- `state_snapshot.payload.required_keys` (list[str], optional)
- `state_snapshot.payload.state` (object)
- optional `state_snapshot.payload.context_ok` (bool)

Scoring:

- Prefer explicit `context_ok` mean when available.
- Else compute required-key retention ratio across snapshots.

## Aggregation

- `trajectory_score` is the arithmetic mean of non-null trajectory metrics.
- Every report must include:
  - per-metric score
  - coverage (how many events contributed)
  - missing-signal flags

## Output Contract

Each runner emits JSON with:

- `run_id`
- `metrics`
- `coverage`
- `missing_signals`
- `trajectory_score`
- `issues` (list of machine-readable diagnostics)

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
