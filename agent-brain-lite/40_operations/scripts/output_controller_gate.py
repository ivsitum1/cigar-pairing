#!/usr/bin/env python3
"""CLI: zero-tolerance output gate before deliverable release."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from brain_assist.output_controller_gate import run_output_gate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Output Controller gate (zero tolerance; WARN=FAIL)"
    )
    parser.add_argument("path", nargs="?", help="File to check (omit for stdin)")
    parser.add_argument(
        "--domain",
        choices=("statistics", "writing", "code", "methodology"),
        default="writing",
        help="Domain rubric for Layer 1",
    )
    parser.add_argument(
        "--project",
        default="",
        help="Project id for author_claims pack under 10_projects/projects/<id>/",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="Exit 1 if any check fails (zero tolerance)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_id = args.project.strip() or None
    text: str | None = None
    path: Path | None = None

    if args.path:
        path = Path(args.path)
        if not path.is_file():
            print(f"File not found: {path}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()

    report = run_output_gate(
        path=path,
        text=text,
        domain=args.domain,
        project_id=project_id,
    )
    payload = report.to_dict()

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if payload["pass"] else "FAIL"
        print(f"output_controller_gate: {status} ({payload['failed_count']} failed)")
        for chk in payload["checks"]:
            mark = "ok" if chk["pass"] else "FAIL"
            print(f"  [{mark}] {chk['id']}: {chk['message']}")

    if args.gate and not payload["pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
