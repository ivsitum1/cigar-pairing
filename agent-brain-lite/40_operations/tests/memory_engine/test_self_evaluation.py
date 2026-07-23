from pathlib import Path

from memory_engine.config import load_config
from memory_engine.hooks import hook_retrieval_injection_eval
from memory_engine.ingest import MemoryIngestor
from memory_engine.models import MemoryEvent
from memory_engine.retrieval import MemoryRetriever
from memory_engine.self_eval import MemorySelfEvaluator
from memory_engine.store import MemoryStore


def test_self_eval_logged_for_ingest_and_retrieval(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    cfg = load_config()
    store = MemoryStore(cfg.sqlite_path)
    evaluator = MemorySelfEvaluator(cfg.self_eval_log_path)
    ingestor = MemoryIngestor(store=store, raw_events_path=cfg.raw_events_path, self_evaluator=evaluator)
    retriever = MemoryRetriever(store=store, self_evaluator=evaluator)

    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id="self-eval-1",
            project_scope="agent-rules",
            payload={"note": "verify self evaluation logging"},
        )
    )
    data = retriever.search(query="self", project_scope="agent-rules", limit=10)
    assert "self_eval" in data
    assert cfg.self_eval_log_path.exists()
    assert "retrieval" in cfg.self_eval_log_path.read_text(encoding="utf-8")
    summary = store.self_eval_summary()
    assert "ingest" in summary
    assert summary["ingest"]["count"] >= 1


def test_evaluate_ingest_private_content_detected():
    evaluator = MemorySelfEvaluator(Path("/tmp/unused.jsonl"))
    result = evaluator.evaluate_ingest({"note": "[PRIVATE] redacted"}, summary="ok")
    assert result["checks"]["private_content_detected"] is True


def test_hook_retrieval_injection_eval_logs_layers(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    cfg = load_config()
    store = MemoryStore(cfg.sqlite_path)
    evaluator = MemorySelfEvaluator(cfg.self_eval_log_path)
    ingestor = MemoryIngestor(store=store, raw_events_path=cfg.raw_events_path, self_evaluator=evaluator)
    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id="hook-eval-1",
            project_scope="agent-rules",
            payload={"note": "hook retrieval injection eval"},
        )
    )
    out = hook_retrieval_injection_eval(project_scope="agent-rules", query="hook")
    assert out["logged"] is True
    log_text = cfg.self_eval_log_path.read_text(encoding="utf-8")
    assert '"layer": "retrieval"' in log_text
    assert '"layer": "injection"' in log_text

