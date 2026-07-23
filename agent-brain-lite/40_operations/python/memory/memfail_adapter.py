"""Thin MemFail harness API over memory_engine + trajectory store."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]


class MemFailBrainAdapter:
    """Implements MemFail 3-fn API: store_conversation, retrieve_memories, get_all_memories."""

    def __init__(self, *, db_path: Path | None = None) -> None:
        from memory_engine.config import load_config
        from memory_engine.retrieval import MemoryRetriever
        from memory_engine.store import MemoryStore

        config = load_config()
        self._db_path = db_path or config.sqlite_path
        self._store = MemoryStore(self._db_path)
        self._retriever = MemoryRetriever(self._store)
        self._trajectory_dir = WORKSPACE / ".agent" / "memory"

    def store_conversation(self, conversation: list[dict[str, Any]] | dict[str, Any]) -> None:
        """Store a multi-turn conversation as memory observations."""
        from memory_engine.ingest import MemoryIngestor
        from memory_engine.models import MemoryEvent

        from memory.failure_mode_tags import tag_event

        turns = conversation if isinstance(conversation, list) else conversation.get("turns") or []
        session_id = "memfail"
        failure_mode = None
        if isinstance(conversation, dict):
            if conversation.get("session_id"):
                session_id = str(conversation["session_id"])
            failure_mode = conversation.get("failure_mode")
        ingestor = MemoryIngestor(self._store, self._trajectory_dir / "raw_events.jsonl")
        for i, turn in enumerate(turns):
            role = turn.get("role", "user")
            content = turn.get("content", "")
            payload = tag_event(
                {"role": role, "content": content, "turn_index": i},
                failure_mode=failure_mode,
            )
            event = MemoryEvent(
                lifecycle="memfail_store",
                session_id=session_id,
                project_scope="memfail_benchmark",
                payload=payload,
            )
            ingestor.ingest(event)

    def retrieve_memories(
        self,
        query: str,
        conversation: list[dict[str, Any]] | dict[str, Any] | None = None,
        k: int = 5,
    ) -> list[str]:
        """Return top-k memory summaries relevant to query."""
        _ = conversation
        result = self._retriever.search(query=query, project_scope="memfail_benchmark", limit=k)
        out: list[str] = []
        for obs in result.get("items") or []:
            summary = obs.get("summary") if isinstance(obs, dict) else getattr(obs, "summary", "")
            if summary:
                out.append(str(summary))
        if not out:
            traj = self._trajectory_dir / "trajectory_session.json"
            if traj.is_file():
                try:
                    data = json.loads(traj.read_text(encoding="utf-8"))
                    recent = str(data.get("last_event") or data.get("summary") or "")
                    if recent and query.lower() in recent.lower():
                        out.append(recent[:500])
                except json.JSONDecodeError:
                    pass
        return out[:k]

    def get_all_memories(self) -> list[str]:
        """Return all stored memory summaries for diagnostic grading."""
        rows = self._store.timeline(project_scope="memfail_benchmark", limit=500) or []
        summaries: list[str] = []
        for row in rows:
            if isinstance(row, dict):
                summaries.append(str(row.get("summary") or ""))
            else:
                summaries.append(str(getattr(row, "summary", "")))
        return [s for s in summaries if s.strip()]
