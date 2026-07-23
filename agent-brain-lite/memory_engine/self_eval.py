"""Self-evaluation utilities for memory pipeline quality control."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemorySelfEvaluator:
    def __init__(self, eval_log_path: Path) -> None:
        self.eval_log_path = eval_log_path
        self.eval_log_path.parent.mkdir(parents=True, exist_ok=True)

    def evaluate_ingest(self, payload: dict[str, Any], summary: str) -> dict[str, Any]:
        payload_json = json.dumps(payload, ensure_ascii=False)
        has_private = "<private>" in payload_json.lower() or "[PRIVATE]" in payload_json
        has_summary = bool(summary.strip())
        confidence = 0.95 if has_summary and not has_private else 0.8
        return {
            "layer": "ingest",
            "score": round(confidence, 3),
            "checks": {
                "has_summary": has_summary,
                # True when private markers survived into the payload (redaction path engaged).
                "private_content_detected": has_private,
            },
        }

    def evaluate_retrieval(self, query: str, count: int, limit: int) -> dict[str, Any]:
        has_query = bool(query.strip())
        ratio = min(1.0, count / max(1, limit))
        score = 0.6 + (0.2 if has_query else 0.0) + (0.2 * ratio)
        return {
            "layer": "retrieval",
            "score": round(min(score, 1.0), 3),
            "checks": {
                "query_non_empty": has_query,
                "result_count": count,
                "limit": limit,
            },
        }

    def evaluate_injection(self, context: str, max_chars: int) -> dict[str, Any]:
        within_budget = len(context) <= max_chars
        has_source = "source:" in context
        score = 0.7 + (0.15 if within_budget else 0.0) + (0.15 if has_source else 0.0)
        return {
            "layer": "injection",
            "score": round(min(score, 1.0), 3),
            "checks": {
                "within_budget": within_budget,
                "has_source_references": has_source,
                "chars": len(context),
                "max_chars": max_chars,
            },
        }

    def evaluate_endpoint(self, endpoint: str, ok: bool) -> dict[str, Any]:
        return {
            "layer": "runtime",
            "score": 1.0 if ok else 0.5,
            "checks": {"endpoint": endpoint, "ok": ok},
        }

    def log(self, entry: dict[str, Any]) -> None:
        # Stamp a UTC timestamp so the log is time-prunable and so the
        # window filter in self_eval_learning_loop.py works (it keys off `ts`).
        if "ts" not in entry:
            entry = {**entry, "ts": datetime.now(timezone.utc).isoformat()}
        with open(self.eval_log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

