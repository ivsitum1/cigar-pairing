# Agent Benchmark Schema

## Purpose

Define a single manifest for trajectory, RAG, and reliability evaluation over live runs.

## Manifest Structure

```json
{
  "benchmark_id": "bench_2026_05_trajectory_full",
  "description": "Live-run benchmark profile",
  "runs": [
    {
      "run_id": "run_001",
      "trajectory_path": "path/to/run_001.jsonl",
      "golden_set_case_id": "case_001"
    }
  ],
  "gates": {
    "min_trajectory_score": 0.7,
    "min_rag_score": 0.7,
    "max_judge_variance": 0.08,
    "min_judge_consistency": 0.75,
    "min_golden_set_score": 0.8
  },
  "judges": {
    "judge_runs": 3
  },
  "output": {
    "results_json": "90_archive/artifacts/bench/latest.json",
    "results_md": "90_archive/artifacts/bench/latest.md",
    "trend_jsonl": "90_archive/artifacts/bench/trend.jsonl"
  }
}
```

## Field Notes

- `runs[*].trajectory_path`: JSONL run trace with supported event types.
- `runs[*].golden_set_case_id`: optional reference for golden-set compliance.
- `gates`: release-style thresholds. Any breach is a benchmark failure.
- `judges.judge_runs`: number of judge replicates used for variance and consistency.

## Golden Set Scoring

Each run can include expected constraints in final answer metadata:

- `final_answer.payload.golden_set_match` (bool), or
- `final_answer.payload.golden_set_score` (0-1)

Benchmark aggregates mean score across runs with golden references.

## Reliability Metrics

- `human_alignment_scoring`
- `judge_consistency_across_runs`
- `judge_output_variance`
- `golden_set_evaluation`

## Required Outputs

The unified benchmark runner must emit:

1. Machine report JSON
2. Human summary Markdown
3. Trend append JSONL (one line per execution)

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
