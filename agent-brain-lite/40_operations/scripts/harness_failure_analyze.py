#!/usr/bin/env python3
"""Analyze trajectory failures and suggest deterministic harness rule snippets (no auto-apply)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
ARTIFACTS = WORKSPACE / "90_archive" / "artifacts"


def _load_latest_trace() -> Path | None:
    if not ARTIFACTS.is_dir():
        return None
    candidates = sorted(ARTIFACTS.glob("*/trajectory.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def analyze_trace(trace_path: Path) -> dict:
    failures: Counter[str] = Counter()
    prescreen_hints: list[str] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        et = rec.get("event_type", "")
        payload = rec.get("payload") or {}
        if et == "tool_selected" and not payload.get("success", True):
            tool = payload.get("tool_selected") or payload.get("tool") or "unknown"
            failures[tool] += 1
        if payload.get("prescreen_hint"):
            prescreen_hints.append(str(payload["prescreen_hint"]))

    suggestions: list[str] = []
    for tool, count in failures.most_common(5):
        suggestions.append(
            f"# Repeated failure on {tool} ({count}x): add deterministic contract check "
            f"in .cursor/rules or MCP tool schema before retry."
        )
    if prescreen_hints:
        suggestions.append(f"# Prescreen hints seen: {prescreen_hints[:3]}")

    return {
        "trace": str(trace_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "failure_tools": dict(failures),
        "suggestions": suggestions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness failure analyzer")
    parser.add_argument("--trace", default="", help="Path to trajectory.jsonl")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    trace = Path(args.trace) if args.trace else _load_latest_trace()
    if not trace or not trace.is_file():
        print("No trajectory trace found", file=sys.stderr)
        return 1
    report = analyze_trace(trace)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for s in report["suggestions"]:
            print(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
