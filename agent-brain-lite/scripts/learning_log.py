#!/usr/bin/env python3
"""Lite learning log — append JSONL, ingest LEARNING_BLOCK, no SQLite."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = BRAIN_ROOT / ".agent" / "learning.jsonl"
BLOCK_RE = re.compile(
    r"##\s*LEARNING_BLOCK\s*\n(.*?)\n##\s*END_LEARNING_BLOCK",
    re.DOTALL | re.IGNORECASE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_event(event: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if "timestamp" not in event:
        event["timestamp"] = utc_now()
    if "source" not in event:
        event["source"] = "learning_log.py"
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def parse_learning_block(text: str) -> dict:
    match = BLOCK_RE.search(text)
    if not match:
        raise ValueError("LEARNING_BLOCK not found in text")
    payload = json.loads(match.group(1).strip())
    if not isinstance(payload, dict):
        raise ValueError("LEARNING_BLOCK body must be a JSON object")
    for key in ("task_type", "task_description", "approach", "status"):
        if key not in payload:
            raise ValueError(f"Missing required field: {key}")
    return payload


def read_events(limit: int | None = None) -> list[dict]:
    if not LOG_PATH.is_file():
        return []
    events: list[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if limit is not None:
        return events[-limit:]
    return events


def cmd_append(args: argparse.Namespace) -> int:
    payload = json.loads(args.json)
    if not isinstance(payload, dict):
        raise SystemExit("JSON must be an object")
    append_event(payload)
    print(f"Appended to {LOG_PATH}")
    return 0


def cmd_ingest_block(args: argparse.Namespace) -> int:
    if args.stdin:
        text = sys.stdin.read()
    elif args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        raise SystemExit("Provide --stdin or --file")
    block = parse_learning_block(text)
    append_event({"event": "learning_block", "block": block})
    print(f"Ingested LEARNING_BLOCK ({block.get('task_type')}) -> {LOG_PATH}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    events = read_events(args.recent)
    for event in events:
        print(json.dumps(event, ensure_ascii=False))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    events = read_events()
    if not events:
        print("No learning events yet.")
        return 0
    by_status: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for event in events:
        block = event.get("block") if event.get("event") == "learning_block" else event
        if not isinstance(block, dict):
            continue
        status = str(block.get("status", event.get("status", "unknown")))
        task_type = str(block.get("task_type", event.get("task_type", "unknown")))
        by_status[status] = by_status.get(status, 0) + 1
        by_type[task_type] = by_type.get(task_type, 0) + 1
    print(f"Total events: {len(events)}")
    print(f"By status: {by_status}")
    print(f"By task_type: {by_type}")
    print(f"Log: {LOG_PATH}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lite learning log (JSONL)")
    sub = parser.add_subparsers(dest="command", required=True)

    append_p = sub.add_parser("append", help="Append raw JSON event")
    append_p.add_argument("--json", required=True, help="JSON object string")
    append_p.set_defaults(func=cmd_append)

    ingest_p = sub.add_parser("ingest-block", help="Parse LEARNING_BLOCK from text")
    ingest_p.add_argument("--file", help="File containing LEARNING_BLOCK")
    ingest_p.add_argument("--stdin", action="store_true", help="Read from stdin")
    ingest_p.set_defaults(func=cmd_ingest_block)

    list_p = sub.add_parser("list", help="List recent events")
    list_p.add_argument("--recent", type=int, default=10)
    list_p.set_defaults(func=cmd_list)

    summary_p = sub.add_parser("summary", help="Summarize learning log")
    summary_p.set_defaults(func=cmd_summary)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
