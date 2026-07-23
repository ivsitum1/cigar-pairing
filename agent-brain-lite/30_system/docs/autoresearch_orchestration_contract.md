# Autoresearch Orchestration Contract

## Purpose

Standardize handoff between autonomous roles in the experimentation loop:
- Proposer
- Executor
- Critic
- Auditor

## Shared Inputs

All roles receive:
- `run_id`
- `candidate_id`
- `target_path`
- `goal`
- `constraints`
- latest metrics and decision context

## Role Responsibilities

### Proposer
- Proposes one single-file, single-intent patch.
- Defines hypothesis and expected metric direction.
- Writes patch plan artifact only, no direct execution.

### Executor
- Applies the proposed patch.
- Runs mandatory evaluation command.
- Produces baseline, candidate scores, and raw outputs.
- Never skips evaluation in `apply` mode.

### Critic
- Reviews the change rationale and metric evidence.
- Verifies no policy boundary violations.
- Flags risk level and recommends accept/revert.

### Auditor
- Issues final structured decision record.
- Verifies artifact completeness and reproducibility metadata.
- Publishes concise run summary for human review.

## Handoff Template

Use this payload between roles:

```json
{
  "run_id": "run_YYYYMMDD_HHMMSS",
  "candidate_id": "cand_...",
  "from_role": "proposer",
  "to_role": "executor",
  "completed": "One sentence",
  "next_step": "One sentence",
  "30_system/context": {
    "target_path": "30_system/SKILLS/SKILL_x.md",
    "hypothesis": "Expected pass-rate increase",
    "constraints": [
      "single-file",
      "single-intent"
    ]
  }
}
```

## Minimal Decision Packet

Auditor output must contain:
- decision (`accept`|`revert`|`skip`)
- decision_reason
- baseline_score
- candidate_score
- delta
- artifact paths

## Guardrails

- No silent acceptance without metric packet.
- No patch expansion beyond declared target file.
- No auto-apply to high-risk rules.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[27_rule_maintenance]]
- [[SKILL_swiss-cheese]]
- [[15b_agent_subagent_system]]
- [[Skill optimization safety gates]]
- [[25_capability_registry]]
