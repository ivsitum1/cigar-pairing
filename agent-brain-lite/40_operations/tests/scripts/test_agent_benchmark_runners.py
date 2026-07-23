import json
from pathlib import Path

import rag_eval_runner as rag
import reliability_eval_runner as reliability
import trajectory_eval_runner as trajectory


def _write_trace(path: Path) -> None:
    events = [
        {
            "run_id": "run_test",
            "ts": "2026-05-06T08:00:00+00:00",
            "event_type": "run_metadata",
            "payload": {"ideal_step_count": 4},
        },
        {
            "run_id": "run_test",
            "ts": "2026-05-06T08:00:01+00:00",
            "event_type": "plan_step",
            "payload": {
                "step_id": "s1",
                "has_goal": True,
                "has_rationale": True,
                "has_acceptance_criteria": True,
            },
        },
        {
            "run_id": "run_test",
            "ts": "2026-05-06T08:00:02+00:00",
            "event_type": "tool_selected",
            "payload": {
                "selected_tool": "rg",
                "expected_tool": "rg",
                "plan_step_id": "s1",
            },
        },
        {
            "run_id": "run_test",
            "ts": "2026-05-06T08:00:03+00:00",
            "event_type": "tool_args",
            "payload": {"schema_valid": True},
        },
        {
            "run_id": "run_test",
            "ts": "2026-05-06T08:00:04+00:00",
            "event_type": "state_snapshot",
            "payload": {"context_ok": True},
        },
        {
            "run_id": "run_test",
            "ts": "2026-05-06T08:00:05+00:00",
            "event_type": "final_answer",
            "payload": {
                "rag_metrics": {
                    "context_precision": 0.9,
                    "faithfulness": 0.8,
                    "answer_relevancy": 0.85,
                    "context_recall": 0.75,
                },
                "human_alignment_score": 0.82,
                "golden_set_score": 0.9,
                "judge_runs": [
                    {"score": 0.8, "label": "pass"},
                    {"score": 0.78, "label": "pass"},
                    {"score": 0.79, "label": "pass"},
                ],
            },
        },
    ]
    path.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n", encoding="utf-8")


def test_trajectory_eval(tmp_path):
    trace = tmp_path / "run.jsonl"
    _write_trace(trace)
    result = trajectory.evaluate_trajectory(trajectory._load_events(trace))
    assert result["run_id"] == "run_test"
    assert result["trajectory_score"] is not None
    assert result["metrics"]["tool_correctness"] == 1.0


def test_rag_eval(tmp_path):
    trace = tmp_path / "run.jsonl"
    _write_trace(trace)
    result = rag.evaluate_rag(rag._load_events(trace))
    assert result["run_id"] == "run_test"
    assert result["rag_score"] is not None
    assert result["metrics"]["faithfulness"] == 0.8


def test_reliability_eval(tmp_path):
    trace = tmp_path / "run.jsonl"
    _write_trace(trace)
    result = reliability.evaluate_reliability(reliability._load_events(trace), judge_runs=3)
    assert result["run_id"] == "run_test"
    assert result["metrics"]["golden_set_evaluation"] == 0.9
    assert result["metrics"]["judge_consistency_across_runs"] == 1.0

