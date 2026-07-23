#!/usr/bin/env python3
"""
CLI for quality_validation (self-assessment + Swiss Cheese).

Adds 40_operations/python to sys.path so imports work from any cwd.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
_PY_ROOT = _SCRIPT.parents[1] / "python"
if _PY_ROOT.is_dir():
    sys.path.insert(0, str(_PY_ROOT))

from quality_validation import (  # noqa: E402
    evaluate_rubric_domain,
    mandatory_self_assess,
    validate_with_swiss_cheese,
)


def _cmd_assess(args: argparse.Namespace) -> int:
    res = mandatory_self_assess(
        args.text,
        domain=args.domain,
        max_iterations=args.max_iterations,
    )
    if args.json:
        out = {
            "final_score": res["final_score"],
            "iterations": res["iterations"],
            "history": res["history"],
        }
        print(json.dumps(out, indent=2))
    else:
        print("final_score:", res["final_score"])
        print("iterations:", res["iterations"])
    return 0


def _cmd_domain(args: argparse.Namespace) -> int:
    ev = evaluate_rubric_domain(args.text, args.domain)
    if args.json:
        print(json.dumps(ev, indent=2, default=str))
    else:
        print("overall:", ev["overall"], "pass:", ev["pass"])
    return 0


def _cmd_swiss_dry_run(args: argparse.Namespace) -> int:
    task = {"task_type": "dry_run", "inputs": {"echo": args.text}}

    def executor(t: dict) -> str:
        return str(t["inputs"].get("echo", "ok"))

    res = validate_with_swiss_cheese(task, executor)
    if args.json:
        print(json.dumps(res, indent=2, default=str))
    else:
        print("success:", res.get("success"))
        if res.get("success"):
            print("assessment score:", res.get("assessment", {}).get("score"))
    return 0 if res.get("success") else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Quality validation (self-assessment / Swiss Cheese)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("assess", help="Run mandatory_self_assess")
    a.add_argument("--text", required=True, help="Text or output to score")
    a.add_argument(
        "--domain",
        choices=("statistics", "writing", "code", "methodology"),
        default=None,
    )
    a.add_argument("--max-iterations", type=int, default=5)
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=_cmd_assess)

    d = sub.add_parser("domain", help="Single evaluate_rubric_domain call")
    d.add_argument("--text", required=True)
    d.add_argument(
        "--domain",
        required=True,
        choices=("statistics", "writing", "code", "methodology"),
    )
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=_cmd_domain)

    s = sub.add_parser("swiss", help="Dry-run Swiss Cheese pipeline")
    s.add_argument("--text", default="hello")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=_cmd_swiss_dry_run)

    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
