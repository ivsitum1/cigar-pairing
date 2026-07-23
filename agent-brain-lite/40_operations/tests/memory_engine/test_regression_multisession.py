from memory_engine.ingest import MemoryIngestor
from memory_engine.injection import ContextInjector
from memory_engine.models import MemoryEvent
from memory_engine.retrieval import MemoryRetriever
from memory_engine.store import MemoryStore


def test_multisession_retrieval_stays_scoped(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    ingestor = MemoryIngestor(store, tmp_path / "raw.jsonl")
    retriever = MemoryRetriever(store)
    injector = ContextInjector(retriever, tmp_path / "context.md", max_chars=6000)

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

    context_a = injector.build_context(project_scope="project-a", query="auth")
    context_b = injector.build_context(project_scope="project-b", query="meta-analysis")

    assert "auth bug fixed" in context_a
    assert "meta-analysis section drafted" in context_b
    assert "meta-analysis section drafted" not in context_a

