import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import self_eval_learning_loop as loop


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def test_build_candidates_window_excludes_old_and_legacy_ts(tmp_path, monkeypatch):
    monkeypatch.setattr(loop, "WORKSPACE", tmp_path)
    monkeypatch.setattr(loop, "SELF_EVAL_LOG", tmp_path / ".agent" / "memory" / "self_eval.jsonl")
    monkeypatch.setattr(loop, "MEMORY_EVENTS_LOG", tmp_path / ".agent" / "memory" / "raw_events.jsonl")
    monkeypatch.setattr(loop, "ERROR_LOG", tmp_path / ".cursor" / "errors" / "error_log.jsonl")
    monkeypatch.setattr(loop, "SKILLS_DIR", tmp_path / "30_system/SKILLS")
    monkeypatch.setattr(loop, "RULES_DIR", tmp_path / ".cursor" / "rules")

    recent = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    _write_jsonl(
        loop.SELF_EVAL_LOG,
        [
            {"ts": recent, "score": 0.5, "layer": "ingest"},
            {"ts": old, "score": 0.1, "layer": "ingest"},
            {"score": 0.2, "layer": "ingest"},
        ],
    )

    threshold = datetime.now(timezone.utc) - timedelta(days=1)
    rows = [x for x in loop._read_jsonl(loop.SELF_EVAL_LOG) if loop._in_window(x, threshold)]
    assert len(rows) == 1
    assert rows[0]["score"] == 0.5


def test_build_candidates_from_error_and_self_eval(tmp_path, monkeypatch):
    monkeypatch.setattr(loop, "WORKSPACE", tmp_path)
    monkeypatch.setattr(loop, "SELF_EVAL_LOG", tmp_path / ".agent" / "memory" / "self_eval.jsonl")
    monkeypatch.setattr(loop, "EVAL_EVENTS_LOG", tmp_path / ".agent" / "memory" / "eval_events.jsonl")
    monkeypatch.setattr(loop, "ERROR_LOG", tmp_path / ".cursor" / "errors" / "error_log.jsonl")
    monkeypatch.setattr(loop, "SKILLS_DIR", tmp_path / "30_system/SKILLS")
    monkeypatch.setattr(loop, "RULES_DIR", tmp_path / ".cursor" / "rules")
    monkeypatch.setattr(loop, "ARTIFACTS_DIR", tmp_path / "90_archive" / "artifacts")

    (tmp_path / "30_system/SKILLS").mkdir(parents=True, exist_ok=True)
    (tmp_path / "30_system/SKILLS" / "SKILL_test-selection.md").write_text("# skill", encoding="utf-8")

    _write_jsonl(
        loop.SELF_EVAL_LOG,
        [
            {"ts": "2026-04-30T10:00:00+00:00", "score": 0.6},
            {"ts": "2026-04-30T10:01:00+00:00", "score": 0.7},
        ],
    )
    _write_jsonl(
        loop.ERROR_LOG,
        [
            {"ts": "2026-04-30T10:00:00+00:00", "ctx": "test-selection failed", "cat": "code", "sev": "high", "tags": ["test-selection"]},
            {"ts": "2026-04-30T10:02:00+00:00", "ctx": "test-selection failed", "cat": "code", "sev": "high", "tags": ["test-selection"]},
            {"ts": "2026-04-30T10:03:00+00:00", "ctx": "test-selection failed", "cat": "code", "sev": "high", "tags": ["test-selection"]},
        ],
    )

    candidates = loop.build_candidates(window_days=365)
    assert candidates
    assert any(c.target_type == "skill" and c.target_path.name == "SKILL_test-selection.md" for c in candidates)


def test_propose_mode_writes_proposal_and_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(loop, "WORKSPACE", tmp_path)
    monkeypatch.setattr(loop, "SELF_EVAL_LOG", tmp_path / ".agent" / "memory" / "self_eval.jsonl")
    monkeypatch.setattr(loop, "EVAL_EVENTS_LOG", tmp_path / ".agent" / "memory" / "eval_events.jsonl")
    monkeypatch.setattr(loop, "ERROR_LOG", tmp_path / ".cursor" / "errors" / "error_log.jsonl")
    monkeypatch.setattr(loop, "LEDGER_JSONL", tmp_path / "30_system/docs" / "LEARNING_UPDATES.jsonl")
    monkeypatch.setattr(loop, "LEDGER_MD", tmp_path / "30_system/docs" / "LEARNING_UPDATES.md")
    monkeypatch.setattr(loop, "TASK_DIR", tmp_path / ".agent" / "task")
    monkeypatch.setattr(loop, "SKILLS_DIR", tmp_path / "30_system/SKILLS")
    monkeypatch.setattr(loop, "RULES_DIR", tmp_path / ".cursor" / "rules")
    monkeypatch.setattr(loop, "ARTIFACTS_DIR", tmp_path / "90_archive" / "artifacts")

    (tmp_path / "30_system/SKILLS").mkdir(parents=True, exist_ok=True)
    (tmp_path / "30_system/SKILLS" / "SKILL_test-selection.md").write_text("# skill", encoding="utf-8")
    _write_jsonl(loop.SELF_EVAL_LOG, [{"ts": "2026-04-30T10:00:00+00:00", "score": 0.5}])
    _write_jsonl(
        loop.ERROR_LOG,
        [
            {"ts": "2026-04-30T10:00:00+00:00", "ctx": "test-selection failed", "cat": "code", "sev": "high", "tags": ["test-selection"]},
            {"ts": "2026-04-30T10:01:00+00:00", "ctx": "test-selection failed", "cat": "code", "sev": "high", "tags": ["test-selection"]},
            {"ts": "2026-04-30T10:02:00+00:00", "ctx": "test-selection failed", "cat": "code", "sev": "high", "tags": ["test-selection"]},
        ],
    )

    out = loop.run_learning_loop(
        mode="propose",
        window_days=365,
        max_candidates=2,
        allow_rule_apply=False,
        dry_run=False,
        gate=loop.GateConfig(),
        weights=loop.ScoreWeights(),
        seed=42,
        resume_run_id=None,
    )
    assert out["candidates"] >= 1
    assert loop.LEDGER_JSONL.exists()
    assert loop.LEDGER_MD.exists()
    assert loop.TASK_DIR.exists()

