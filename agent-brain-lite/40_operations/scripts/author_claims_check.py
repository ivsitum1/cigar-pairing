#!/usr/bin/env python3
"""CLI: deterministic author-claims gate before manuscript/clinical retry."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from brain_assist.author_claims_gate import (  # noqa: E402
    check_file,
    check_text,
    gate_before_retry,
    list_project_packs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Author claims deterministic gate")
    parser.add_argument("path", nargs="?", help="File to check (default: stdin)")
    parser.add_argument("--categories", default="", help="Comma-separated: clinical,writing,methodology")
    parser.add_argument(
        "--project",
        default="",
        help="Load project pack from 10_projects/projects/<id>/author_claims/rules.json",
    )
    parser.add_argument("--list-projects", action="store_true", help="List project packs with rules.json")
    parser.add_argument("--gate", action="store_true", help="Exit 1 if high-severity blocks retry")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.list_projects:
        packs = list_project_packs()
        if args.json:
            print(json.dumps({"projects": packs}, indent=2))
        else:
            for p in packs:
                print(p)
        return 0

    cats = [c.strip() for c in args.categories.split(",") if c.strip()] or None
    project_id = args.project.strip() or None

    if args.path:
        report = check_file(Path(args.path), categories=cats, project_id=project_id)
        if args.gate:
            text = Path(args.path).read_text(encoding="utf-8", errors="replace")
            gate = gate_before_retry(text, project_id=project_id)
            report["gate"] = gate
            report["pass"] = gate["allow_retry"]
    else:
        text = sys.stdin.read()
        violations = check_text(text, categories=cats, project_id=project_id)
        report = {
            "path": "<stdin>",
            "project_id": project_id,
            "pass": len(violations) == 0,
            "violation_count": len(violations),
            "violations": [v.__dict__ for v in violations],
        }
        if args.gate:
            gate = gate_before_retry(text, project_id=project_id)
            report["gate"] = gate
            report["pass"] = gate["allow_retry"]

    if args.json:
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
        print(payload)
    else:
        if report["pass"]:
            scope = f" (project={project_id})" if project_id else " (brain only)"
            print(f"PASS: no blocking violations{scope}")
        else:
            print(f"FAIL: {report['violation_count']} violation(s)")
            for v in report.get("violations", []):
                print(f"  [{v['severity']}] {v.get('scope', 'brain')} {v['rule_id']}: {v['message']}")

    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
