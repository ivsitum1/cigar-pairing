from memory_engine.ingest import MemoryIngestor
from memory_engine.models import MemoryEvent
from memory_engine.retrieval import MemoryRetriever
from memory_engine.store import MemoryStore


def test_search_cross_project_returns_both_scopes(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    ingestor = MemoryIngestor(store, tmp_path / "raw.jsonl")
    retriever = MemoryRetriever(store)

    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id="s-a",
            project_scope="project-a",
            payload={"result": "auth bug fixed"},
        )
    )
    ingestor.ingest(
        MemoryEvent(
            lifecycle="SessionEnd",
            session_id="s-b",
            project_scope="project-b",
            payload={"result": "meta-analysis section drafted"},
        )
    )

    scoped = retriever.search(query="meta", project_scope="project-a", limit=10)
    assert scoped["count"] == 0

    cross = retriever.search_cross_project(query="meta", limit=10)
    assert cross["count"] >= 1
    scopes = {item["project_scope"] for item in cross["items"]}
    assert "project-b" in scopes
