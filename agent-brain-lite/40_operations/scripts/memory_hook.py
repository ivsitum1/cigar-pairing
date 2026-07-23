#!/usr/bin/env python3
"""CLI entrypoint for lifecycle hook ingest and session injection."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Repo root (parent of 40_operations/), so top-level `memory_engine` package resolves
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from memory_engine.hooks import ingest_hook, session_start_injection


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory lifecycle hook")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("--lifecycle", required=True)
    ingest_parser.add_argument("--session-id", required=True)
    ingest_parser.add_argument("--project-scope", required=True)
    ingest_parser.add_argument("--payload", default="{}", help="JSON payload")

    inject_parser = subparsers.add_parser("inject")
    inject_parser.add_argument("--project-scope", required=True)
    inject_parser.add_argument("--query", default="recent context")

    args = parser.parse_args()

    if args.command == "ingest":
        payload = json.loads(args.payload)
        result = ingest_hook(
            lifecycle=args.lifecycle,
            session_id=args.session_id,
            project_scope=args.project_scope,
            payload=payload,
        )
        print(json.dumps(result, ensure_ascii=False))
        return

    context = session_start_injection(project_scope=args.project_scope, query=args.query)
    print(context)


if __name__ == "__main__":
    main()

