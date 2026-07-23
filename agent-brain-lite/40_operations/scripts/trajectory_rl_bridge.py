#!/usr/bin/env python3
"""Bridge trajectory benchmark failures into skill-gap / self-eval learning."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Trajectory RL bridge for skill-gap pipeline")
    parser.add_argument(
        "--manifest",
        default="30_system/docs/AGENT_BENCHMARK_RL_DEMO.json",
        help="Benchmark manifest with trajectory_path and optional skill_id",
    )
    parser.add_argument("--scan", action="store_true", help="List trajectory failures (JSON)")
    parser.add_argument(
        "--propose-learning",
        action="store_true",
        help="Run self_eval_learning_loop in propose mode (trajectory-enriched candidates)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    from trajectory_rl.candidates import scan_manifest

    manifest_path = WORKSPACE / args.manifest
    failures = scan_manifest(manifest_path)
    payload = {
        "manifest": str(manifest_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "failure_count": len(failures),
        "failures": [
            {
                "run_id": f.run_id,
                "skill_id": f.skill_id,
                "trajectory_score": f.trajectory_score,
                "weak_metrics": f.weak_metrics,
                "trace_path": str(f.trace_path.relative_to(WORKSPACE)).replace("\\", "/"),
                "reasons": f.reasons,
            }
            for f in failures
        ],
    }

    if args.scan or not args.propose_learning:
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for row in payload["failures"]:
                print(f"{row['skill_id']}: score={row['trajectory_score']} trace={row['trace_path']}")
        return 0

    cmd = [
        sys.executable,
        str(WORKSPACE / "40_operations/scripts/self_eval_learning_loop.py"),
        "--mode",
        "propose",
        "--max-candidates",
        str(max(1, len(failures))),
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True, check=False)
    out = {"trajectory_scan": payload, "learning_loop_exit": proc.returncode}
    if proc.stdout.strip():
        try:
            out["learning_summary"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            out["learning_stdout"] = proc.stdout
    if proc.stderr.strip():
        out["learning_stderr"] = proc.stderr
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
