# Artifact Policy

## Scope

This policy defines run outputs under `90_archive/artifacts/<run_id>/`.

## Required Artifacts

- `manifest.json`: run-level metadata and thresholds.
- `metrics.json`: structured result collection for all processed candidates.
- `decision.md`: human-readable decision trail.

## Optional Artifacts

- `metrics.jsonl`: event stream for each candidate.
- `state.json`: resumable state (`processed_candidate_ids`).
- `report.md`: generated summary report.

## Retention

- Keep last 100 run directories by default.
- Keep all runs created in the last 14 days.
- Never delete runs marked with `.keep` file.

## Cleanup Recommendation

Implement periodic cleanup as a separate script:
1. scan `90_archive/artifacts/`;
2. preserve `.keep` and recent runs;
3. remove older runs beyond retention cap;
4. write cleanup summary into `30_system/docs/CHANGELOG_AUTO.md` when used in CI.

## Integrity Rules

- Required artifacts must exist for a run to be marked healthy.
- If a run is incomplete, state should permit safe resume.
- Decision logs and metrics must agree on candidate IDs and decisions.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[SKILL_write-prd]]
- [[SKILL_write-research-spec]]
- [[SKILL_scholarly-iteration-loop]]
- [[13_agentic_workflow]]
- [[SKILL_setup-project]]
