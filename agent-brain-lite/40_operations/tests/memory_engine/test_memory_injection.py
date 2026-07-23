from memory_engine.ingest import MemoryIngestor
from memory_engine.injection import ContextInjector
from memory_engine.models import MemoryEvent
from memory_engine.retrieval import MemoryRetriever
from memory_engine.store import MemoryStore


def test_context_injection_is_budget_aware(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    ingestor = MemoryIngestor(store, tmp_path / "raw.jsonl")
    retriever = MemoryRetriever(store)
    injector = ContextInjector(retriever, tmp_path / "context.md", max_chars=250)

    ingestor.ingest(
        MemoryEvent(
            lifecycle="UserPromptSubmit",
            session_id="s-3",
            project_scope="agent-rules",
            payload={"prompt": "Please refactor retrieval with timeline and get_observations"},
        )
    )

    context = injector.build_context(project_scope="agent-rules", query="retrieval")
    assert len(context) <= 250
    assert context.startswith("# Memory Context")

