# Memory Self-Eval Report

- Generated: 2026-06-11T13:33:20.465789+00:00
- Source: `C:\Users\Ivan\OneDrive\Dokumenti\agent rules\.agent\memory\self_eval.jsonl`
- Total entries: 20168
- Malformed lines: 0
- Entries with failure_mode: 77
- Entries with ts: 224

## Insights

- Worker-only layers ['runtime'] not in log (expected unless the HTTP memory worker is exercised).
- Only 224/20168 entries carry `ts` — older rows predate timestamping; windowing/pruning are partial.
- Only 77/20168 entries carry a failure_mode tag — most rows predate that field and add little signal, so capping old lines is safe.
- 1 ingest entries flagged private_content_detected=True (markers present in payload). This indicates the redaction path engaged, not a leak. Confirm no raw '<private>' survives in raw_events.jsonl / memory.db.
- Real failure modes observed: storage=1, summary=2. These are the rows worth keeping/reviewing.

## Layer coverage

| Layer | Count | Avg score |
|---|---|---|
| ingest | 20021 | 0.95 |
| retrieval | 74 | 1.0 |
| injection | 73 | 1.0 |

## Score distribution

| Bucket | Count |
|---|---|
| <0.5 | 0 |
| 0.5-0.7 | 0 |
| 0.7-0.85 | 1 |
| 0.85-0.95 | 0 |
| >=0.95 | 20167 |

## Failure modes

| Mode | Count |
|---|---|
| unknown | 74 |
| summary | 2 |
| storage | 1 |

## Data-quality checks

- Private content detected (ingest): 1
- Summary-missing failures: 0

## Semantic graph (auto)

- [[Graph connectivity map]]
- [40 operations INDEX](../../30_system/docs/indexes/40_operations_INDEX.md)
- [AUTOMATION INDEX](../../30_system/docs/AUTOMATION_INDEX.md)
- [FOLDER INDEX](../../30_system/docs/FOLDER_INDEX.md)
