from memory_engine.models import MemoryEvent
from memory_engine.ingest import MemoryIngestor
from memory_engine.store import MemoryStore


def test_ingest_deduplicates_events(tmp_path):
    db_path = tmp_path / "memory.db"
    raw_path = tmp_path / "raw.jsonl"
    store = MemoryStore(db_path)
    ingestor = MemoryIngestor(store, raw_path)

    event = MemoryEvent(
        lifecycle="PostToolUse",
        session_id="s-1",
        project_scope="agent-rules",
        payload={"tool": "ReadFile", "status": "ok"},
    )
    first = ingestor.ingest(event)
    second = ingestor.ingest(event)

    assert first["inserted"] is True
    assert second["deduplicated"] is True


def test_search_returns_observations(tmp_path):
    db_path = tmp_path / "memory.db"
    raw_path = tmp_path / "raw.jsonl"
    store = MemoryStore(db_path)
    ingestor = MemoryIngestor(store, raw_path)

    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id="s-2",
            project_scope="agent-rules",
            payload={"note": "fixed memory bug in retrieval"},
        )
    )

    results = store.search("memory", "agent-rules", limit=5)
    assert len(results) >= 1
    assert "observation_id" in results[0]

