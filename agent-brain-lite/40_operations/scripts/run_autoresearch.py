#!/usr/bin/env python3
"""Autoresearch orchestration entrypoint for this workspace."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = ROOT / "90_archive/artifacts"
DOCS = ROOT / "30_system/docs"


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def append_orchestration_log(payload: dict) -> None:
    path = DOCS / "AUTORESEARCH_RUNS.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run autoresearch learning loop with contract metadata.")
    parser.add_argument("--mode", choices=["propose", "apply"], default="propose")
    parser.add_argument("--window-days", type=int, default=7)
    parser.add_argument("--max-candidates", type=int, default=3)
    parser.add_argument("--accept-threshold", type=float, default=0.10)
    parser.add_argument("--rollback-threshold", type=float, default=0.00)
    parser.add_argument("--tie-breaker", choices=["accept", "revert"], default="revert")
    parser.add_argument("--allow-rule-apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(ROOT / "40_operations/scripts" / "self_eval_learning_loop.py"),
        "--mode",
        args.mode,
        "--window-days",
        str(args.window_days),
        "--max-candidates",
        str(args.max_candidates),
        "--accept-threshold",
        str(args.accept_threshold),
        "--rollback-threshold",
        str(args.rollback_threshold),
        "--tie-breaker",
        args.tie_breaker,
        "--json",
    ]
    if args.allow_rule_apply:
        cmd.append("--allow-rule-apply")
    if args.dry_run:
        cmd.append("--dry-run")

    code, out, err = run_cmd(cmd)
    if code != 0:
        print(err or out)
        return code

    summary = json.loads(out)
    run_id = summary.get("run_id", "unknown")
    run_artifacts = ARTIFACTS / run_id

    orchestration_record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "mode": args.mode,
        "entrypoint": "40_operations/scripts/run_autoresearch.py",
        "contract_refs": [
            "30_system/docs/autoresearch_hybrid_spec.md",
            "30_system/docs/autoresearch_metric_gate.md",
            "30_system/docs/autoresearch_orchestration_contract.md",
        ],
        "artifact_paths": summary.get("artifact_paths", {}),
        "results_count": len(summary.get("results", [])),
    }
    append_orchestration_log(orchestration_record)

    # ensure concise markdown summary exists for rapid human review
    md_summary = run_artifacts / "autoresearch_summary.md"
    md_summary.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Autoresearch Run Summary `{run_id}`",
        "",
        f"- Mode: `{args.mode}`",
        f"- Candidates: `{summary.get('candidates')}`",
        f"- Results count: `{len(summary.get('results', []))}`",
        "",
        "## Contract References",
        "",
        "- `30_system/docs/autoresearch_hybrid_spec.md`",
        "- `30_system/docs/autoresearch_metric_gate.md`",
        "- `30_system/docs/autoresearch_orchestration_contract.md`",
        "",
        "## Artifacts",
        "",
        f"- `90_archive/artifacts/{run_id}/manifest.json`",
        f"- `90_archive/artifacts/{run_id}/metrics.json`",
        f"- `90_archive/artifacts/{run_id}/decision.md`",
    ]
    md_summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps({"summary": summary, "orchestration": orchestration_record}, ensure_ascii=False, indent=2))
    else:
        print(f"Autoresearch run: {run_id} | mode={args.mode} | results={len(summary.get('results', []))}")
        print(f"Summary file: {md_summary.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
