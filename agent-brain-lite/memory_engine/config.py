"""Configuration and path resolution for memory engine."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MemoryConfig:
    workspace_root: Path
    data_dir: Path
    sqlite_path: Path
    raw_events_path: Path
    context_cache_path: Path
    self_eval_log_path: Path
    worker_host: str
    worker_port: int
    enabled: bool
    max_injection_chars: int
    raw_event_ttl_days: int
    observation_ttl_days: int
    prune_min_confidence: float


def _default_workspace_root() -> Path:
    explicit = os.environ.get("WORKSPACE_ROOT")
    if explicit:
        return Path(explicit).resolve()
    brain_root = Path(__file__).resolve().parent.parent
    ops_python = brain_root / "40_operations" / "python"
    if ops_python.is_dir():
        ops_str = str(ops_python)
        if ops_str not in sys.path:
            sys.path.insert(0, ops_str)
        try:
            from common.workspace_scope import resolve_workspace_root

            return resolve_workspace_root(cwd=Path.cwd(), script_path=Path(__file__))
        except ImportError:
            pass
    return brain_root


def load_config() -> MemoryConfig:
    workspace = _default_workspace_root()
    data_dir = workspace / ".agent" / "memory"
    return MemoryConfig(
        workspace_root=workspace,
        data_dir=data_dir,
        sqlite_path=data_dir / "memory.db",
        raw_events_path=data_dir / "raw_events.jsonl",
        context_cache_path=data_dir / "last_injected_context.md",
        self_eval_log_path=data_dir / "self_eval.jsonl",
        worker_host=os.environ.get("AGENT_MEMORY_HOST", "127.0.0.1"),
        worker_port=int(os.environ.get("AGENT_MEMORY_PORT", "37777")),
        enabled=os.environ.get("AGENT_MEMORY_ENABLED", "1").strip() in {"1", "true", "TRUE"},
        max_injection_chars=int(os.environ.get("AGENT_MEMORY_MAX_INJECTION_CHARS", "7000")),
        raw_event_ttl_days=int(os.environ.get("AGENT_MEMORY_RAW_TTL_DAYS", "30")),
        observation_ttl_days=int(os.environ.get("AGENT_MEMORY_OBS_TTL_DAYS", "180")),
        prune_min_confidence=float(os.environ.get("AGENT_MEMORY_PRUNE_MIN_CONFIDENCE", "0.2")),
    )
