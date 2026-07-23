"""Cross-machine learning-exchange roundtrip: export filters noise, import merges peers."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "40_operations" / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

from memory_engine.models import Observation  # noqa: E402
from memory_engine.store import MemoryStore  # noqa: E402


def _seed(db: Path) -> None:
    store = MemoryStore(db)
    store.insert_observation("good-1", Observation(
        session_id="s", project_scope="p", event_hash="h1", lifecycle="PostToolUse",
        summary="PostToolUse: checked proportional-hazards before Cox model",
        detail="lesson", source_ref="ref", confidence=0.9, tags=["stats"], ts="2026-07-05T09:00:00+00:00"))
    store.insert_observation("noise-1", Observation(
        session_id="s", project_scope="p", event_hash="h2", lifecycle="unknown",
        summary='unknown: {"raw_input": "﻿{...}"}',
        detail='Payload={"raw_input": "..."}', source_ref="ref", confidence=0.8,
        ts="2026-07-05T09:01:00+00:00"))


@pytest.mark.unit
def test_export_filters_noise_and_import_merges(tmp_path, monkeypatch):
    import memory_sync

    local_db = tmp_path / "local.db"
    exchange = tmp_path / "exchange"
    monkeypatch.setattr(memory_sync, "MEM_DB", local_db)
    monkeypatch.setattr(memory_sync, "EXCHANGE_DIR", exchange)
    monkeypatch.setenv("AGENT_MACHINE_ID", "machine-a")

    _seed(local_db)

    exported = memory_sync.export_digest()
    assert exported["exported"] == 1, "opaque 'unknown:' dump should be filtered out"
    digest = exchange / "machine-a" / "digest.jsonl"
    assert digest.exists()

    # Relabel machine-a's digest as a foreign peer and import into a FRESH
    # local db (new machine bootstrapping from peers).
    (exchange / "machine-b").mkdir()
    (exchange / "machine-b" / "digest.jsonl").write_text(
        digest.read_text(encoding="utf-8"), encoding="utf-8")
    fresh_db = tmp_path / "fresh.db"
    monkeypatch.setattr(memory_sync, "MEM_DB", fresh_db)
    monkeypatch.setenv("AGENT_MACHINE_ID", "machine-c")  # neither peer is us

    result = memory_sync.import_peers()
    assert result["imported"] == 2  # machine-a + machine-b copies, both the good obs
    assert set(result["peers"]) == {"machine-a", "machine-b"}

    rows = MemoryStore(fresh_db).get_observations(["good-1"])
    assert rows and "federated:" in rows[0]["source_ref"]
