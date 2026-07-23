"""Session-start context injection with budget control."""
from __future__ import annotations

from pathlib import Path

from .models import utc_now_iso
from .self_eval import MemorySelfEvaluator
from .retrieval import MemoryRetriever


class ContextInjector:
    def __init__(
        self,
        retriever: MemoryRetriever,
        context_cache_path: Path,
        max_chars: int = 7000,
        self_evaluator: MemorySelfEvaluator | None = None,
    ) -> None:
        self.retriever = retriever
        self.context_cache_path = context_cache_path
        self.context_cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_chars = max_chars
        self.self_evaluator = self_evaluator

    def build_context(self, project_scope: str, query: str, limit: int = 10) -> str:
        search_data = self.retriever.search(query=query, project_scope=project_scope, limit=limit)
        ids = [item["observation_id"] for item in search_data["items"]]
        details = self.retriever.get_observations(ids).get("items", [])
        blocks = []
        for entry in details:
            block = (
                f"- [{entry['observation_id']}] {entry['summary']}\n"
                f"  source: {entry['source_ref']}\n"
                f"  detail: {entry['detail'][:320]}"
            )
            blocks.append(block)
        payload = "# Memory Context\n" + ("\n".join(blocks) if blocks else "- No relevant memory yet.")
        if len(payload) > self.max_chars:
            payload = payload[: self.max_chars - 3] + "..."
        if self.self_evaluator:
            eval_result = self.self_evaluator.evaluate_injection(context=payload, max_chars=self.max_chars)
            self.self_evaluator.log(eval_result)
            self.retriever.store.insert_self_eval("injection", float(eval_result.get("score", 0.0)), eval_result, utc_now_iso())
        return payload

    def cache_context(self, context: str) -> None:
        self.context_cache_path.write_text(context + "\n", encoding="utf-8")

