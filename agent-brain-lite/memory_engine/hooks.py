"""Lifecycle hook helpers for memory ingest and injection."""
from __future__ import annotations

from .config import load_config
from .ingest import MemoryIngestor
from .injection import ContextInjector
from .models import MemoryEvent
from .retrieval import MemoryRetriever
from .self_eval import MemorySelfEvaluator
from .store import MemoryStore


def _build_ingestor(config) -> MemoryIngestor:
    store = MemoryStore(config.sqlite_path)
    evaluator = MemorySelfEvaluator(config.self_eval_log_path)
    return MemoryIngestor(store, config.raw_events_path, self_evaluator=evaluator)


def _build_injector(config) -> ContextInjector:
    store = MemoryStore(config.sqlite_path)
    evaluator = MemorySelfEvaluator(config.self_eval_log_path)
    retriever = MemoryRetriever(store, self_evaluator=evaluator)
    return ContextInjector(
        retriever,
        context_cache_path=config.context_cache_path,
        max_chars=config.max_injection_chars,
        self_evaluator=evaluator,
    )


def ingest_hook(lifecycle: str, session_id: str, project_scope: str, payload: dict) -> dict:
    config = load_config()
    if not config.enabled:
        return {"inserted": False, "disabled": True}
    ingestor = _build_ingestor(config)
    event = MemoryEvent(lifecycle=lifecycle, session_id=session_id, project_scope=project_scope, payload=payload)
    return ingestor.ingest(event)


def session_start_injection(project_scope: str, query: str) -> str:
    config = load_config()
    if not config.enabled:
        return "# Memory Context\n- Disabled by AGENT_MEMORY_ENABLED=0."
    injector = _build_injector(config)
    context = injector.build_context(project_scope=project_scope, query=query, limit=10)
    injector.cache_context(context)
    return context


def hook_retrieval_injection_eval(project_scope: str, query: str) -> dict:
    """Log retrieval/injection self-eval on the live hook path (no user-visible inject)."""
    config = load_config()
    if not config.enabled:
        return {"logged": False, "disabled": True}
    injector = _build_injector(config)
    injector.build_context(project_scope=project_scope, query=query or "hook lifecycle", limit=5)
    return {"logged": True}

