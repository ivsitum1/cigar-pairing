"""Ingest pipeline for lifecycle events."""
from __future__ import annotations

import json
from pathlib import Path

from .compression import ObservationComposer
from .models import MemoryEvent
from .self_eval import MemorySelfEvaluator
from .store import MemoryStore


class MemoryIngestor:
    def __init__(
        self,
        store: MemoryStore,
        raw_events_path: Path,
        composer: ObservationComposer | None = None,
        self_evaluator: MemorySelfEvaluator | None = None,
    ) -> None:
        self.store = store
        self.raw_events_path = raw_events_path
        self.raw_events_path.parent.mkdir(parents=True, exist_ok=True)
        self.composer = composer or ObservationComposer()
        self.self_evaluator = self_evaluator

    def ingest(self, event: MemoryEvent) -> dict:
        event_hash = self.composer.event_hash(event)
        inserted = self.store.upsert_event(
            event_hash=event_hash,
            session_id=event.session_id,
            project_scope=event.project_scope,
            lifecycle=event.lifecycle,
            payload=self.composer.sanitize_payload(event.payload),
            ts=event.ts,
        )
        if not inserted:
            return {"inserted": False, "deduplicated": True, "event_hash": event_hash}

        self._append_raw_event(event_hash, event)

        # Immune-system gate: refuse memory-poisoning payloads before they enter
        # the retrievable store. The raw event is kept above for audit, but no
        # observation is created, so a poisoned instruction can never be
        # retrieved or re-injected into a later session.
        poisoned, reason = self.composer.is_poisoned(event.payload)
        if poisoned:
            if self.self_evaluator:
                quarantine_eval = {"score": 0.0, "quarantined": True, "reason": reason}
                self.self_evaluator.log(quarantine_eval)
                self.store.insert_self_eval("ingest_quarantine", 0.0, quarantine_eval, event.ts)
            return {
                "inserted": True,
                "deduplicated": False,
                "quarantined": True,
                "reason": reason,
                "event_hash": event_hash,
            }

        observation_id, observation = self.composer.build_observation(event, event_hash)
        failure_mode = self.composer.infer_failure_mode(event.payload)
        eval_result = self.self_evaluator.evaluate_ingest(event.payload, observation.summary) if self.self_evaluator else {}
        eval_result = {**eval_result, "failure_mode": failure_mode}
        self.store.insert_observation(observation_id, observation, self_eval=eval_result)
        if self.self_evaluator:
            self.self_evaluator.log(eval_result)
            self.store.insert_self_eval("ingest", float(eval_result.get("score", 0.0)), eval_result, event.ts)
        return {
            "inserted": True,
            "deduplicated": False,
            "event_hash": event_hash,
            "observation_id": observation_id,
            "self_eval": eval_result,
        }

    def _append_raw_event(self, event_hash: str, event: MemoryEvent) -> None:
        safe_payload = self.composer.sanitize_payload(event.payload)
        line = {
            "event_hash": event_hash,
            "lifecycle": event.lifecycle,
            "session_id": event.session_id,
            "project_scope": event.project_scope,
            "payload": safe_payload,
            "failure_mode": self.composer.infer_failure_mode(safe_payload),
            "ts": event.ts,
        }
        with open(self.raw_events_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")

