"""Search and timeline retrieval for memory data."""
from __future__ import annotations

from pathlib import Path

from .federation import federated_cross_project_search
from .models import utc_now_iso
from .self_eval import MemorySelfEvaluator
from .store import MemoryStore


class MemoryRetriever:
    def __init__(self, store: MemoryStore, self_evaluator: MemorySelfEvaluator | None = None) -> None:
        self.store = store
        self.self_evaluator = self_evaluator

    @staticmethod
    def _workspace_root_for_store(db_path: Path) -> Path | None:
        if db_path.name == "memory.db" and db_path.parent.name == "memory" and db_path.parent.parent.name == ".agent":
            return db_path.parent.parent.parent.resolve()
        return None

    def search(self, query: str, project_scope: str, limit: int = 10) -> dict:
        items = self.store.search(query=query, project_scope=project_scope, limit=limit)
        eval_result = self.self_evaluator.evaluate_retrieval(query=query, count=len(items), limit=limit) if self.self_evaluator else {}
        if self.self_evaluator:
            self.self_evaluator.log(eval_result)
            self.store.insert_self_eval("retrieval", float(eval_result.get("score", 0.0)), eval_result, utc_now_iso())
        return {"query": query, "project_scope": project_scope, "count": len(items), "items": items, "self_eval": eval_result}

    def timeline(self, project_scope: str, limit: int = 25) -> dict:
        items = self.store.timeline(project_scope=project_scope, limit=limit)
        return {"project_scope": project_scope, "count": len(items), "items": items}

    def get_observations(self, ids: list[str]) -> dict:
        items = self.store.get_observations(ids)
        return {"requested": len(ids), "count": len(items), "items": items}

    def search_cross_project(self, query: str, limit: int = 10) -> dict:
        workspace_root = self._workspace_root_for_store(self.store.db_path)
        if workspace_root is None:
            items = self.store.search_cross_project(query=query, limit=limit)
            result = {
                "query": query,
                "cross_project": True,
                "federated": False,
                "sources_queried": ["local"],
                "count": len(items),
                "items": items,
            }
        else:
            result = federated_cross_project_search(
                query=query,
                limit=limit,
                workspace_root=workspace_root,
            )
        eval_result = (
            self.self_evaluator.evaluate_retrieval(query=query, count=result["count"], limit=limit)
            if self.self_evaluator
            else {}
        )
        if self.self_evaluator:
            self.self_evaluator.log(eval_result)
            self.store.insert_self_eval(
                "retrieval_cross_project",
                float(eval_result.get("score", 0.0)),
                eval_result,
                utc_now_iso(),
            )
        result["self_eval"] = eval_result
        return result

