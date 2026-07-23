#!/usr/bin/env python3
"""Maintenance commands for memory store."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from memory_engine.config import load_config
from memory_engine.store import MemoryStore


def prune_raw(days: int) -> int:
    cfg = load_config()
    if not cfg.raw_events_path.exists():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    kept = []
    removed = 0
    for line in cfg.raw_events_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        # Tolerate malformed/legacy lines: keep them rather than crash the prune.
        try:
            obj = json.loads(line)
            ts = datetime.fromisoformat(str(obj["ts"]).replace("Z", "+00:00"))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            kept.append(line)
            continue
        if ts >= cutoff:
            kept.append(line)
        else:
            removed += 1
    cfg.raw_events_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    return removed


def prune_db(days: int) -> dict[str, int]:
    cfg = load_config()
    if not cfg.sqlite_path.exists():
        return {"observations": 0, "events": 0, "self_evaluations": 0}
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    store = MemoryStore(cfg.sqlite_path)
    return store.cleanup_old(cutoff)


def cap_self_eval(max_lines: int) -> int:
    """Keep only the most recent ``max_lines`` entries of self_eval.jsonl.

    Self-eval entries carry no timestamp, so they cannot be time-pruned; this
    caps the append-only analytics log by line count. Returns lines removed.
    """
    cfg = load_config()
    path = cfg.self_eval_log_path
    if not path.exists() or max_lines <= 0:
        return 0
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) <= max_lines:
        return 0
    removed = len(lines) - max_lines
    kept = lines[-max_lines:]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return removed


def export_snapshot(output_path: str) -> None:
    cfg = load_config()
    store = MemoryStore(cfg.sqlite_path)
    payload = {
        "timeline": store.timeline(project_scope="default", limit=5000),
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def rebuild_index() -> None:
    cfg = load_config()
    store = MemoryStore(cfg.sqlite_path)
    with store._connect() as conn:  # pylint: disable=protected-access
        conn.execute("DELETE FROM observations_fts")
        rows = conn.execute("SELECT observation_id, project_scope, summary, detail, tags_json FROM observations").fetchall()
        for row in rows:
            tags = ",".join(json.loads(row["tags_json"]))
            conn.execute(
                "INSERT INTO observations_fts(observation_id, project_scope, summary, detail, tags) VALUES(?,?,?,?,?)",
                (row["observation_id"], row["project_scope"], row["summary"], row["detail"], tags),
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory maintenance commands")
    sub = parser.add_subparsers(dest="command", required=True)

    p_prune = sub.add_parser("prune")
    p_prune.add_argument("--days", type=int, default=30)
    p_prune.add_argument(
        "--self-eval-max-lines",
        type=int,
        default=20000,
        help="Cap self_eval.jsonl to most recent N lines (0 disables).",
    )
    p_prune.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be pruned without writing.",
    )

    p_export = sub.add_parser("export")
    p_export.add_argument("--output", required=True)

    sub.add_parser("rebuild-index")

    args = parser.parse_args()
    if args.command == "prune":
        if args.dry_run:
            cfg = load_config()
            raw_count = 0
            if cfg.raw_events_path.exists():
                cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
                for line in cfg.raw_events_path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                        ts = datetime.fromisoformat(str(obj["ts"]).replace("Z", "+00:00"))
                        if ts < cutoff:
                            raw_count += 1
                    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                        pass
            se_lines = 0
            if cfg.self_eval_log_path.exists() and args.self_eval_max_lines > 0:
                total = len(cfg.self_eval_log_path.read_text(encoding="utf-8").splitlines())
                se_lines = max(0, total - args.self_eval_max_lines)
            print(f"[dry-run] Would remove ~{raw_count} raw events older than {args.days}d")
            print(f"[dry-run] Would cap self_eval.jsonl by ~{se_lines} lines (max {args.self_eval_max_lines})")
            print("[dry-run] DB prune counts require live run (skipped)")
            return
        removed = prune_raw(args.days)
        db_removed = prune_db(args.days)
        se_removed = cap_self_eval(args.self_eval_max_lines)
        print(f"Removed {removed} raw events")
        print(
            f"Pruned DB rows older than {args.days}d: "
            f"observations={db_removed['observations']}, "
            f"events={db_removed['events']}, "
            f"self_evaluations={db_removed['self_evaluations']}"
        )
        print(f"Capped self_eval.jsonl: removed {se_removed} old lines")
        return
    if args.command == "export":
        export_snapshot(args.output)
        print(f"Exported snapshot to {args.output}")
        return
    rebuild_index()
    print("Rebuilt FTS index")


if __name__ == "__main__":
    main()

