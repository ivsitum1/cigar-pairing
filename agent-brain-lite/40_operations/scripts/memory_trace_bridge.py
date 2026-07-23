#!/usr/bin/env python3
"""Promote successful memory decisions from trajectories to solved_lemmas (AutoMem loop 2, no LoRA)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

WORKSPACE = Path(__file__).resolve().parents[2]
_HARNESS_PY = WORKSPACE / "40_operations" / "python"
if str(_HARNESS_PY) not in sys.path:
    sys.path.insert(0, str(_HARNESS_PY))

SOLVED_LEMMAS = WORKSPACE / ".agent" / "solved_lemmas.jsonl"
ARTIFACTS_DIR = WORKSPACE / "90_archive" / "artifacts"

MEMORY_TOOL_HINTS = (
    "context_sync",
    "memory_hierarchy",
    "fold-lemma",
    "fold_lemma",
    "memory_hook",
    "memory_trim",
    "solved_lemmas",
    "memory_trace_bridge",
)
MEMORY_OPS = frozenset({"log", "read", "write", "plan"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iter_trajectory_files(extra: list[Path] | None = None) -> Iterator[Path]:
    if extra:
        for p in extra:
            if p.is_file():
                yield p
    if ARTIFACTS_DIR.is_dir():
        for path in sorted(ARTIFACTS_DIR.glob("*/trajectory.jsonl")):
            yield path
    session_ptr = WORKSPACE / ".agent" / "memory" / "trajectory_session.json"
    if session_ptr.is_file():
        data = json.loads(session_ptr.read_text(encoding="utf-8"))
        trace = data.get("trace_path") or data.get("path")
        if trace:
            p = WORKSPACE / trace if not Path(trace).is_absolute() else Path(trace)
            if p.is_file():
                yield p


def _load_existing_subgoals() -> set[str]:
    if not SOLVED_LEMMAS.is_file():
        return set()
    out: set[str] = set()
    for line in SOLVED_LEMMAS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        subgoal = rec.get("subgoal", "")
        if subgoal:
            out.add(subgoal)
    return out


def _is_successful_memory_event(event: dict[str, Any]) -> bool:
    payload = event.get("payload") or {}
    event_type = event.get("event_type", "")

    memory_op = str(payload.get("memory_op", "")).lower()
    if memory_op in MEMORY_OPS and payload.get("success", True) is not False:
        return True

    if event_type == "tool_result":
        if payload.get("schema_valid") is True or payload.get("context_ok") is True:
            tool = str(payload.get("tool_name") or payload.get("selected_tool") or "").lower()
            if any(h in tool for h in MEMORY_TOOL_HINTS):
                return True
        exit_code = payload.get("exit_code")
        if exit_code == 0:
            tool = str(payload.get("tool_name") or payload.get("command") or "").lower()
            if any(h in tool for h in MEMORY_TOOL_HINTS):
                return True

    if event_type == "tool_selected":
        tool = str(payload.get("selected_tool") or payload.get("tool_name") or "").lower()
        if any(h in tool for h in MEMORY_TOOL_HINTS):
            return payload.get("tool_correct") is True

    if event_type == "final_answer":
        score = payload.get("golden_set_score")
        if score is not None and float(score) >= 0.8:
            if payload.get("memory_promotion") or payload.get("memory_op"):
                return True

    return False


def _rel_path(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE)).replace("\\", "/")
    except ValueError:
        return path.as_posix()


def _lemma_from_event(event: dict[str, Any], trace_path: Path) -> dict[str, str] | None:
    payload = event.get("payload") or {}
    subgoal = (
        payload.get("subgoal")
        or payload.get("plan_step_id")
        or payload.get("step_id")
        or payload.get("memory_op")
    )
    if not subgoal:
        tool = payload.get("selected_tool") or payload.get("tool_name") or "memory_action"
        subgoal = f"Memory trace: {tool}"

    summary = payload.get("summary") or payload.get("rationale") or payload.get("note")
    if not summary:
        summary = (
            f"Successful memory decision from {trace_path.parent.name} "
            f"({event.get('event_type', 'event')})."
        )

    rel_trace = _rel_path(trace_path)
    return {
        "ts": event.get("ts") or _utc_now(),
        "subgoal": str(subgoal)[:200],
        "summary": str(summary)[:500],
        "provenance": rel_trace,
    }


def scan_trajectories(*, extra_paths: list[Path] | None = None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for trace_path in _iter_trajectory_files(extra_paths):
        for line_no, line in enumerate(
            trace_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not _is_successful_memory_event(event):
                continue
            lemma = _lemma_from_event(event, trace_path)
            if lemma:
                lemma["trace_line"] = line_no
                lemma["trace_path"] = _rel_path(trace_path)
                candidates.append(lemma)
    return candidates


def promote(
    *,
    dry_run: bool = False,
    sync_hierarchy: bool = False,
    extra_paths: list[Path] | None = None,
) -> dict[str, Any]:
    existing = _load_existing_subgoals()
    candidates = scan_trajectories(extra_paths=extra_paths)
    promoted: list[dict[str, str]] = []
    skipped = 0

    for cand in candidates:
        subgoal = cand["subgoal"]
        if subgoal in existing:
            skipped += 1
            continue
        record = {
            "ts": cand["ts"],
            "subgoal": subgoal,
            "summary": cand["summary"],
            "provenance": cand["provenance"],
        }
        promoted.append(record)
        existing.add(subgoal)

    if promoted and not dry_run:
        SOLVED_LEMMAS.parent.mkdir(parents=True, exist_ok=True)
        with SOLVED_LEMMAS.open("a", encoding="utf-8") as fh:
            for rec in promoted:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    hierarchy_added = 0
    if sync_hierarchy and promoted and not dry_run:
        from harness.memory_hierarchy import sync_from_solved_lemmas

        hierarchy_added = sync_from_solved_lemmas(SOLVED_LEMMAS)

    return {
        "candidates": len(candidates),
        "promoted": len(promoted),
        "skipped_duplicates": skipped,
        "hierarchy_nodes_added": hierarchy_added,
        "dry_run": dry_run,
        "records": promoted,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bridge trajectory memory events → solved_lemmas.jsonl (AutoMem, no LoRA)"
    )
    parser.add_argument("--scan", action="store_true", help="List promotion candidates only")
    parser.add_argument("--promote", action="store_true", help="Append new lemmas to solved_lemmas.jsonl")
    parser.add_argument(
        "--sync-hierarchy",
        action="store_true",
        help="After promote, run sync_from_solved_lemmas on memory_hierarchy index",
    )
    parser.add_argument("--trajectory", action="append", default=[], help="Extra trajectory.jsonl path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    extra = [Path(p) for p in args.trajectory]
    if args.scan or not args.promote:
        rows = scan_trajectories(extra_paths=extra or None)
        payload = {"candidate_count": len(rows), "candidates": rows}
    else:
        payload = promote(
            dry_run=args.dry_run,
            sync_hierarchy=args.sync_hierarchy,
            extra_paths=extra or None,
        )

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
