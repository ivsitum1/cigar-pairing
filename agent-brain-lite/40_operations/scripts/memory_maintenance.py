#!/usr/bin/env python3
"""Bounded-growth maintenance for the agent memory store.

The memory pipeline appends to JSONL telemetry logs and a ``self_evaluations``
SQLite table with no size ceiling, so both grow without bound (14 MB / 121k
lines observed for self_eval.jsonl). This job keeps them bounded *without losing
data*: the overflow is gzip-archived under ``.agent/memory/archive/`` before the
live file/table is trimmed to a recent window. It also VACUUMs the DB to reclaim
space after churn.

Idempotent and safe to run on a schedule. Default thresholds are conservative;
override via flags.
"""
from __future__ import annotations

import argparse
import gzip
import shutil
import sqlite3
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MEM_DIR = REPO_ROOT / ".agent" / "memory"
ARCHIVE_DIR = MEM_DIR / "archive"

# Append-only JSONL telemetry logs to rotate (keep last `keep_lines` live).
ROTATE_LOGS = ("self_eval.jsonl", "raw_events.jsonl")


def rotate_jsonl(path: Path, keep_lines: int, dry_run: bool) -> str:
    if not path.exists():
        return f"skip {path.name} (absent)"
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        lines = fh.readlines()
    if len(lines) <= keep_lines:
        return f"ok   {path.name} ({len(lines)} lines, under {keep_lines})"
    overflow = lines[:-keep_lines]
    keep = lines[-keep_lines:]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    archive = ARCHIVE_DIR / f"{path.stem}-{stamp}.jsonl.gz"
    if dry_run:
        return f"DRY  {path.name}: would archive {len(overflow)} lines, keep {len(keep)}"
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(archive, "at", encoding="utf-8") as gz:
        gz.writelines(overflow)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(keep), encoding="utf-8")
    tmp.replace(path)
    return f"ROT  {path.name}: archived {len(overflow)} -> {archive.name}, kept {len(keep)}"


def trim_self_evaluations(db: Path, keep_rows: int, dry_run: bool) -> str:
    if not db.exists():
        return "skip memory.db (absent)"
    conn = sqlite3.connect(db)
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "self_evaluations" not in tables:
            return "skip self_evaluations (table absent)"
        total = conn.execute("SELECT COUNT(*) FROM self_evaluations").fetchone()[0]
        if total <= keep_rows:
            return f"ok   self_evaluations ({total} rows, under {keep_rows})"
        cutoff_id = conn.execute(
            "SELECT id FROM self_evaluations ORDER BY id DESC LIMIT 1 OFFSET ?", (keep_rows,)
        ).fetchone()
        if cutoff_id is None:
            return f"ok   self_evaluations ({total} rows)"
        cutoff = cutoff_id[0]
        overflow = conn.execute(
            "SELECT id, layer, score, payload_json, ts FROM self_evaluations WHERE id <= ? ORDER BY id",
            (cutoff,),
        ).fetchall()
        if dry_run:
            return f"DRY  self_evaluations: would archive/trim {len(overflow)} of {total} rows"
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        archive = ARCHIVE_DIR / f"self_evaluations-{stamp}.jsonl.gz"
        import json
        with gzip.open(archive, "at", encoding="utf-8") as gz:
            for row in overflow:
                gz.write(json.dumps(
                    {"id": row[0], "layer": row[1], "score": row[2],
                     "payload_json": row[3], "ts": row[4]}, ensure_ascii=False) + "\n")
        conn.execute("DELETE FROM self_evaluations WHERE id <= ?", (cutoff,))
        conn.commit()
        return f"TRIM self_evaluations: archived {len(overflow)} -> {archive.name}, kept {keep_rows}"
    finally:
        conn.close()


def vacuum(db: Path, dry_run: bool) -> str:
    if not db.exists():
        return "skip vacuum (db absent)"
    before = db.stat().st_size
    if dry_run:
        return f"DRY  vacuum (current {before/1e6:.1f} MB)"
    conn = sqlite3.connect(db)
    try:
        conn.execute("VACUUM")
    finally:
        conn.close()
    after = db.stat().st_size
    return f"VAC  memory.db {before/1e6:.1f} -> {after/1e6:.1f} MB"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--keep-lines", type=int, default=5000, help="Live JSONL tail length.")
    ap.add_argument("--keep-evals", type=int, default=25000, help="Live self_evaluations rows.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    results = []
    for name in ROTATE_LOGS:
        results.append(rotate_jsonl(MEM_DIR / name, args.keep_lines, args.dry_run))
    results.append(trim_self_evaluations(MEM_DIR / "memory.db", args.keep_evals, args.dry_run))
    results.append(vacuum(MEM_DIR / "memory.db", args.dry_run))
    for r in results:
        print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
