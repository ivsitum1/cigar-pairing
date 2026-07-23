"""Observation composer with lightweight, verifiable compression."""
from __future__ import annotations

import json
import re
from hashlib import sha256

from .models import MemoryEvent, Observation


PRIVATE_PATTERN = re.compile(r"<private>.*?</private>", re.IGNORECASE | re.DOTALL)
FAILURE_MODES = frozenset({"summary", "storage", "retrieval", "unknown"})

# Memory-poisoning guard (ref: "Agent-Native Immune System", arXiv 2606.28270,
# surfaced in our own 2026-W28 ai_news digest). A fully aligned agent is still
# vulnerable to runtime hijacking via poisoned memory: injected instructions
# that get stored, retrieved, and re-injected on later sessions. We refuse such
# payloads at ingest so they never enter the retrievable store.
POISON_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore (?:all |the )?(?:previous|prior|above) (?:instructions|context|rules)",
        r"disregard (?:all |the )?(?:previous|prior|above|system)",
        r"forget (?:everything|all previous|your instructions)",
        r"you are now (?:a|an|in) ",
        r"new (?:system )?(?:prompt|instructions?)\s*[:=]",
        r"override (?:the )?(?:system|safety|guardrails?)",
        r"(?:reveal|print|exfiltrate|leak) (?:the )?(?:system prompt|secrets?|api[_ ]?keys?|credentials)",
        r"</?(?:system|instructions?)>",  # smuggled role tags
    )
)


class ObservationComposer:
    def sanitize_payload(self, payload: dict) -> dict:
        as_json = json.dumps(payload, ensure_ascii=False)
        scrubbed = PRIVATE_PATTERN.sub("[PRIVATE]", as_json)
        return json.loads(scrubbed)

    def event_hash(self, event: MemoryEvent) -> str:
        key = {
            "lifecycle": event.lifecycle,
            "session_id": event.session_id,
            "project_scope": event.project_scope,
            "payload": self.sanitize_payload(event.payload),
            "ts": event.ts[:19],
        }
        raw = json.dumps(key, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return sha256(raw).hexdigest()

    def build_observation(self, event: MemoryEvent, event_hash: str) -> tuple[str, Observation]:
        safe_payload = self.sanitize_payload(event.payload)
        payload_str = json.dumps(safe_payload, ensure_ascii=False)
        payload_preview = payload_str[:800]
        summary = f"{event.lifecycle}: {payload_preview[:160]}"
        detail = f"Lifecycle={event.lifecycle}\nSession={event.session_id}\nPayload={payload_preview}"
        source_ref = f"{event.session_id}:{event.lifecycle}:{event.ts}"
        observation_id = event_hash[:20]
        tags = self._infer_tags(payload_str, event.lifecycle, safe_payload)
        observation = Observation(
            session_id=event.session_id,
            project_scope=event.project_scope,
            event_hash=event_hash,
            lifecycle=event.lifecycle,
            summary=summary,
            detail=detail,
            source_ref=source_ref,
            confidence=0.8,
            tags=tags,
            mem_type=self.infer_mem_type(safe_payload, event.lifecycle),
            ts=event.ts,
        )
        return observation_id, observation

    def infer_mem_type(self, payload: dict, lifecycle: str) -> str:
        """Classify into a brain-inspired memory domain (see models.MEM_TYPES).

        Heuristic and verifiable: relations → associative; inferred patterns and
        recurring corrections → implicit; everything else (stated facts,
        decisions, outcomes) → explicit (default).
        """
        text = json.dumps(payload, ensure_ascii=False).lower()
        if any(k in text for k in ("relation", "related_to", "depends_on", "links_to", "association")):
            return "associative"
        if payload.get("failure_mode") not in (None, "unknown") or any(
            k in text for k in ("correction", "prefer", "pattern", "always", "never ", "reminder")
        ):
            return "implicit"
        return "explicit"

    def is_poisoned(self, payload: dict) -> tuple[bool, str]:
        """Return (poisoned, reason) if payload contains a memory-injection attack."""
        text = json.dumps(payload, ensure_ascii=False)
        for pattern in POISON_PATTERNS:
            match = pattern.search(text)
            if match:
                return True, f"poison_pattern:{match.re.pattern[:40]}"
        return False, ""

    def infer_failure_mode(self, payload: dict) -> str:
        explicit = payload.get("failure_mode")
        if isinstance(explicit, str) and explicit in FAILURE_MODES:
            return explicit
        text = json.dumps(payload, ensure_ascii=False).lower()
        if any(k in text for k in ("retrieve", "recall", "not found", "missing memory")):
            return "retrieval"
        if any(k in text for k in ("store", "persist", "write failed", "sqlite")):
            return "storage"
        if any(k in text for k in ("summar", "compress", "abstract", "truncate")):
            return "summary"
        return "unknown"

    def _infer_tags(self, payload: str, lifecycle: str, payload_dict: dict | None = None) -> list[str]:
        tags = {lifecycle.lower()}
        if payload_dict is not None:
            fm = self.infer_failure_mode(payload_dict)
            tags.add(f"failure_mode:{fm}")
        if "error" in payload.lower():
            tags.add("error")
        if "test" in payload.lower():
            tags.add("test")
        if "plan" in payload.lower():
            tags.add("plan")
        return sorted(tags)

