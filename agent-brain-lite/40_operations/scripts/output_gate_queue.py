#!/usr/bin/env python3
"""Queue a deliverable for automatic Output Controller gate on sessionEnd."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from brain_assist.output_gate_session import (  # noqa: E402
    MANUAL_QUEUE,
    flag_deliverable,
    gate_root,
    flush_gates,
)


def _cmd_add(args: argparse.Namespace) -> int:
    flag_deliverable(
        args.path,
        domain=args.domain,
        project_id=args.project.strip() or None,
        source="cli",
    )
    if args.json:
        print(json.dumps({"queued": args.path, "via": "session_queue"}, indent=2))
    else:
        print(f"flagged: {args.path}")
    return 0


def _cmd_append_file(args: argparse.Namespace) -> int:
    entry = {
        "path": args.path,
        "domain": args.domain,
        "project_id": args.project.strip() or None,
    }
    queue = gate_root() / MANUAL_QUEUE
    with queue.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    if args.json:
        print(json.dumps({"appended": args.path, "queue": str(queue)}, indent=2))
    else:
        print(f"appended to {queue}: {args.path}")
    return 0


def _cmd_flush(args: argparse.Namespace) -> int:
    summary = flush_gates()
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(
            f"gate flush: {summary.get('passed')} pass, {summary.get('failed')} fail, "
            f"{summary.get('skipped')} skipped"
        )
    return 1 if int(summary.get("failed", 0)) > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Output gate manual queue / flush")
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name, handler in (("add", _cmd_add), ("append", _cmd_append_file), ("flush", _cmd_flush)):
        p = sub.add_parser(name, help=f"{name} deliverable to gate queue")
        p.add_argument("path", nargs="?", help="Deliverable path (required for add/append)")
        p.add_argument(
            "--domain",
            choices=("statistics", "writing", "code", "methodology"),
            default="writing",
        )
        p.add_argument("--project", default="", help="Project id for author_claims pack")
        p.add_argument("--json", action="store_true")
        p.set_defaults(handler=handler)

    args = parser.parse_args()
    if args.cmd in {"add", "append"} and not args.path:
        parser.error("path required for add/append")
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
