#!/usr/bin/env python3
"""Smoke test MemFail adapter on a minimal offline conversation subset."""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))
sys.path.insert(0, str(WORKSPACE))

from memory.memfail_adapter import MemFailBrainAdapter  # noqa: E402


SAMPLE = {
    "session_id": "memfail_smoke_001",
    "turns": [
        {"role": "user", "content": "My favorite anesthesia journal is Anesthesia & Analgesia."},
        {"role": "assistant", "content": "Noted your preference."},
        {"role": "user", "content": "What journal did I mention?"},
    ],
}


def main() -> int:
    adapter = MemFailBrainAdapter()
    adapter.store_conversation(SAMPLE)
    query = "What journal did I mention?"
    memories = adapter.retrieve_memories(query, SAMPLE["turns"], k=3)
    all_mem = adapter.get_all_memories()
    result = {
        "store_ok": len(all_mem) >= 1,
        "retrieve_count": len(memories),
        "retrieve_preview": memories[:2],
        "all_memory_count": len(all_mem),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["store_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
