#!/usr/bin/env python3
"""
Contrastive reflection: compare success vs failure trajectories (EvoSC-style).

Usage:
  python 40_operations/scripts/contrastive_reflection.py \\
    --success 90_archive/artifacts/run_ok/trajectory.jsonl \\
    --failure 90_archive/artifacts/run_fail/trajectory.jsonl \\
    --task-domain statistics --json

  python 40_operations/scripts/contrastive_reflection.py --auto-latest --task-domain code_impl
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[2]
ARTIFACTS = WORKSPACE / "90_archive" / "artifacts"
ERROR_LOG = WORKSPACE / ".cursor" / "errors" / "error_log.jsonl"
WIKI_PATTERNS = WORKSPACE / "20_knowledge" / "wiki" / "concepts" / "Contrastive reflection patterns.md"
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_trajectory(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not path.is_file():
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def extract_atdp_steps(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for ev in events:
        if ev.get("event_type") == "atdp_step":
            payload = ev.get("payload") or {}
            steps.append(payload)
        elif ev.get("event_type") == "tool_selected":
            payload = ev.get("payload") or {}
            steps.append(
                {
                    "a": payload.get("selected_tool", ""),
                    "y": "success" if payload.get("success") else "failure",
                    "o": f"tool_selected success={payload.get('success')}",
                }
            )
    return steps


def summarize_trace(events: list[dict[str, Any]]) -> dict[str, Any]:
    atdp = extract_atdp_steps(events)
    tools = [
        (s.get("a") or "").strip()
        for s in atdp
        if (s.get("a") or "").strip()
    ]
    failures = [s for s in atdp if str(s.get("y", "")).lower() in {"failure", "fail", "error"}]
    return {
        "event_count": len(events),
        "atdp_steps": len(atdp),
        "tool_sequence": tools,
        "failure_steps": failures,
        "final_outcome": "failure" if failures else "success",
    }


def diff_traces(success: dict[str, Any], failure: dict[str, Any]) -> dict[str, Any]:
    s_tools = success.get("tool_sequence") or []
    f_tools = failure.get("tool_sequence") or []
    divergence_idx = None
    for i, (s, f) in enumerate(zip(s_tools, f_tools)):
        if s != f:
            divergence_idx = i
            break
    if divergence_idx is None and len(s_tools) != len(f_tools):
        divergence_idx = min(len(s_tools), len(f_tools))

    pitfall = ""
    success_pattern = ""
    if failure.get("failure_steps"):
        last_fail = failure["failure_steps"][-1]
        pitfall = f"Avoid: action={last_fail.get('a')} when observation={last_fail.get('o')}"
    if s_tools:
        success_pattern = f"Replicate tool order ending with: {s_tools[-3:] if len(s_tools) >= 3 else s_tools}"

    return {
        "divergence_index": divergence_idx,
        "success_tools": s_tools,
        "failure_tools": f_tools,
        "error_prone_insight": pitfall or "Failure trace had no ATDP steps; log with trajectory_emit --atdp",
        "success_pattern": success_pattern or "Success trace had no ATDP steps",
    }


def find_latest_pair(artifacts_root: Path) -> tuple[Path | None, Path | None]:
    runs = sorted(
        [p for p in artifacts_root.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    success_path = failure_path = None
    for run_dir in runs:
        trace = run_dir / "trajectory.jsonl"
        if not trace.is_file():
            continue
        events = load_trajectory(trace)
        summary = summarize_trace(events)
        if summary["final_outcome"] == "success" and success_path is None:
            success_path = trace
        elif summary["final_outcome"] == "failure" and failure_path is None:
            failure_path = trace
        if success_path and failure_path:
            break
    return success_path, failure_path


def append_error_log(task_domain: str, insight: str, fix: str) -> None:
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    next_id = 1
    if ERROR_LOG.is_file():
        for line in ERROR_LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    row = json.loads(line)
                    eid = str(row.get("id", ""))
                    if eid.startswith("E"):
                        next_id = max(next_id, int(eid[1:]) + 1)
                except json.JSONDecodeError:
                    pass
    entry = {
        "id": f"E{next_id}",
        "ts": _utc(),
        "cat": task_domain if task_domain in {"stats", "code", "writing", "methodology", "clinical"} else "code",
        "sev": "medium",
        "ctx": "contrastive_reflection",
        "err": insight[:500],
        "fix": fix[:500],
        "promoted": False,
    }
    with open(ERROR_LOG, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_wiki_note(diff: dict[str, Any], task_domain: str) -> Path:
    WIKI_PATTERNS.parent.mkdir(parents=True, exist_ok=True)
    block = (
        f"\n## {_utc()[:10]} — {task_domain}\n\n"
        f"- **Error-prone:** {diff.get('error_prone_insight', '')}\n"
        f"- **Success pattern:** {diff.get('success_pattern', '')}\n"
        f"- **Divergence index:** {diff.get('divergence_index')}\n"
    )
    if WIKI_PATTERNS.is_file():
        text = WIKI_PATTERNS.read_text(encoding="utf-8")
        if block.strip() not in text:
            WIKI_PATTERNS.write_text(text + block, encoding="utf-8")
    else:
        header = (
            "---\n"
            "title: Contrastive reflection patterns\n"
            "tags: [agent, evolution, trajectory]\n"
            "---\n\n"
            "# Contrastive reflection patterns\n\n"
            "Distilled from success vs failure trajectory pairs (EvoSC-style).\n"
        )
        WIKI_PATTERNS.write_text(header + block, encoding="utf-8")
    return WIKI_PATTERNS


def main() -> int:
    parser = argparse.ArgumentParser(description="Contrastive reflection on trajectory pairs")
    parser.add_argument("--success", type=Path, help="Success trajectory.jsonl")
    parser.add_argument("--failure", type=Path, help="Failure trajectory.jsonl")
    parser.add_argument("--auto-latest", action="store_true", help="Pick latest success/fail runs")
    parser.add_argument("--task-domain", default="code", help="stats|code|writing|methodology|clinical")
    parser.add_argument("--write-error-log", action="store_true", help="Append pitfall to error_log.jsonl")
    parser.add_argument("--write-wiki", action="store_true", help="Append patterns to wiki")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    success_path = args.success
    failure_path = args.failure
    if args.auto_latest:
        success_path, failure_path = find_latest_pair(ARTIFACTS)
    if not success_path or not failure_path:
        print("Need both success and failure trajectories", file=sys.stderr)
        return 2

    s_sum = summarize_trace(load_trajectory(success_path))
    f_sum = summarize_trace(load_trajectory(failure_path))
    diff = diff_traces(s_sum, f_sum)

    report = {
        "success_trace": str(success_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "failure_trace": str(failure_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "success_summary": s_sum,
        "failure_summary": f_sum,
        "contrastive": diff,
        "task_domain": args.task_domain,
        "generated_at": _utc(),
    }

    if args.write_error_log and diff.get("error_prone_insight"):
        append_error_log(args.task_domain, diff["error_prone_insight"], diff.get("success_pattern", ""))
        report["error_log_appended"] = True
    if args.write_wiki:
        report["wiki_path"] = str(write_wiki_note(diff, args.task_domain)).replace("\\", "/")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(report["contrastive"]["error_prone_insight"])
        print(report["contrastive"]["success_pattern"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
