#!/usr/bin/env python3
"""Cross-machine learning exchange for the brain.

Different machines each run their own brain with a local, uncommitted
``memory.db``. This tool reconciles what they have *learned* without shipping
the raw 80 MB database or any secrets: each machine exports a small, git-tracked
**learning digest** (curated, meaningful observations only) under a per-machine
namespace, and imports its peers' digests into the local store.

Transport is git (already shared across the machines). Skills/rules learned by
the loop reconcile through normal commits; this handles the memory layer.

Flow (see run_monthly_learning_sync.ps1):
    git pull  ->  --import  ->  --export  ->  commit + push

Idempotent: observations dedupe by observation_id (INSERT OR REPLACE), so
re-running never duplicates.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from memory_engine.models import Observation  # noqa: E402
from memory_engine.store import MemoryStore  # noqa: E402

MEM_DB = REPO_ROOT / ".agent" / "memory" / "memory.db"
EXCHANGE_DIR = REPO_ROOT / "20_knowledge" / "learning_exchange"
# Cap per-machine digest so the git-tracked artifact stays small.
MAX_EXPORT = 3000


def machine_id() -> str:
    raw = os.environ.get("AGENT_MACHINE_ID") or platform.node() or "unknown-machine"
    return "".join(c if (c.isalnum() or c in "-_") else "-" for c in raw).strip("-").lower() or "unknown-machine"


def _is_meaningful(summary: str, detail: str) -> bool:
    """Skip opaque capture dumps; only share observations with real content."""
    s = (summary or "").strip().lower()
    if not s or s.startswith("unknown:"):
        return False
    if "raw_input" in (detail or "")[:200]:
        return False
    return True


def export_digest() -> dict:
    if not MEM_DB.exists():
        return {"exported": 0, "reason": "no local memory.db"}
    conn = sqlite3.connect(MEM_DB)
    try:
        rows = conn.execute(
            """
            SELECT observation_id, event_hash, session_id, project_scope, lifecycle,
                   summary, detail, source_ref, confidence, tags_json, mem_type, ts
            FROM observations
            ORDER BY ts DESC
            """
        ).fetchall()
    finally:
        conn.close()

    mid = machine_id()
    out_dir = EXCHANGE_DIR / mid
    out_dir.mkdir(parents=True, exist_ok=True)
    digest = out_dir / "digest.jsonl"

    kept = 0
    with digest.open("w", encoding="utf-8") as fh:
        for r in rows:
            if kept >= MAX_EXPORT:
                break
            summary, detail = r[5], r[6]
            if not _is_meaningful(summary, detail):
                continue
            try:
                tags = json.loads(r[9]) if r[9] else []
            except json.JSONDecodeError:
                tags = []
            fh.write(json.dumps({
                "observation_id": r[0], "event_hash": r[1], "session_id": r[2],
                "project_scope": r[3], "lifecycle": r[4], "summary": summary,
                "detail": detail, "source_ref": r[7], "confidence": r[8],
                "tags": tags, "mem_type": r[10], "ts": r[11],
            }, ensure_ascii=False) + "\n")
            kept += 1

    (out_dir / "meta.json").write_text(json.dumps({
        "machine_id": mid,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "observations": kept,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        digest_ref = str(digest.relative_to(REPO_ROOT))
    except ValueError:
        digest_ref = str(digest)
    return {"exported": kept, "machine_id": mid, "digest": digest_ref}


def import_peers() -> dict:
    if not EXCHANGE_DIR.exists():
        return {"imported": 0, "peers": [], "reason": "no exchange dir"}
    store = MemoryStore(MEM_DB)
    mine = machine_id()
    imported = 0
    peers: list[str] = []
    for peer_dir in sorted(EXCHANGE_DIR.iterdir()):
        if not peer_dir.is_dir() or peer_dir.name == mine:
            continue
        digest = peer_dir / "digest.jsonl"
        if not digest.exists():
            continue
        peers.append(peer_dir.name)
        for line in digest.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            obs = Observation(
                session_id=str(d.get("session_id", "")),
                project_scope=str(d.get("project_scope", "")),
                event_hash=str(d.get("event_hash", "")),
                lifecycle=str(d.get("lifecycle", "")),
                summary=str(d.get("summary", "")),
                detail=str(d.get("detail", "")),
                # Tag provenance so federated memory is traceable to its origin.
                source_ref=f"federated:{peer_dir.name}:{d.get('source_ref', '')}",
                confidence=float(d.get("confidence", 0.8)),
                tags=list(d.get("tags", [])) + [f"federated:{peer_dir.name}"],
                mem_type=str(d.get("mem_type", "explicit")),
                ts=str(d.get("ts", "")),
            )
            store.insert_observation(str(d.get("observation_id", "")), obs,
                                     self_eval={"federated_from": peer_dir.name})
            imported += 1
    return {"imported": imported, "peers": peers}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--export", action="store_true", help="Write local learning digest.")
    g.add_argument("--import", dest="do_import", action="store_true", help="Merge peer digests into local memory.db.")
    g.add_argument("--reconcile", action="store_true", help="Import peers then export local (git handled by runner).")
    args = ap.parse_args()

    result: dict = {}
    if args.reconcile:
        result["import"] = import_peers()
        result["export"] = export_digest()
    elif args.do_import:
        result = import_peers()
    else:
        result = export_digest()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
