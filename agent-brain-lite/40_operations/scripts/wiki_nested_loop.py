#!/usr/bin/env python3
"""LOOP-4: nested wiki self-improvement loop with human gate every 3rd cycle.

Orchestrates stage planning and handoff files; does not auto-edit Tier 0 rules.
See: 30_system/docs/LOOP-3_wiki_self_improving_kb.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[2]
TASK_DIR = WORKSPACE / ".agent" / "task"
WIKI_ROOT = WORKSPACE / "20_knowledge" / "wiki"

STAGES: tuple[str, ...] = ("ingest", "daily-update", "wiki-synthesize", "wiki-lint")
HUMAN_GATE_EVERY = 3
DEFAULT_LINT_THRESHOLD = 50


@dataclass
class LoopState:
    cycle: int = 0
    last_stage: str = ""
    stopped: bool = False
    stop_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def state_path(slug: str) -> Path:
    return TASK_DIR / f"loop_{slug}_state.json"


def handoff_path(slug: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return TASK_DIR / f"loop_{stamp}_{slug}_handoff.md"


def load_state(slug: str) -> LoopState:
    path = state_path(slug)
    if not path.is_file():
        return LoopState()
    data = json.loads(path.read_text(encoding="utf-8"))
    return LoopState(**{k: data[k] for k in LoopState.__dataclass_fields__})


def save_state(slug: str, state: LoopState) -> None:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    state_path(slug).write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")


def run_lint_check(*, dry_run: bool) -> tuple[int, str]:
    """Proxy lint: obsidian connectivity broken-link count."""
    script = WORKSPACE / "40_operations" / "scripts" / "obsidian_connectivity_check.py"
    if not script.is_file() or not WIKI_ROOT.is_dir():
        return 0, "wiki lint skipped (no wiki root or script)"
    if dry_run:
        return 0, "dry-run lint skipped"
    proc = subprocess.run(
        [sys.executable, str(script), "--root", str(WIKI_ROOT)],
        capture_output=True,
        text=True,
        cwd=str(WORKSPACE),
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    broken = 0
    for line in out.splitlines():
        if "broken" in line.lower():
            parts = line.split()
            for p in parts:
                if p.isdigit():
                    broken = max(broken, int(p))
    return broken, out.strip() or f"exit {proc.returncode}"


def next_stage_index(current: str) -> int:
    if not current or current not in STAGES:
        return 0
    idx = STAGES.index(current)
    return (idx + 1) % len(STAGES)


def advance_cycle(state: LoopState, stage: str, *, lint_errors: int, lint_threshold: int) -> LoopState:
    state.last_stage = stage
    if stage == STAGES[-1]:
        state.cycle += 1
    if lint_errors > lint_threshold:
        state.stopped = True
        state.stop_reason = f"lint_errors {lint_errors} > threshold {lint_threshold}"
    return state


def human_gate_needed(cycle: int) -> bool:
    return cycle > 0 and cycle % HUMAN_GATE_EVERY == 0


def write_handoff(
    slug: str,
    *,
    completed: str,
    next_stage: str,
    blockers: list[str],
    cycle: int,
    gate: bool,
) -> Path:
    path = handoff_path(slug)
    body = (
        f"Completed: {completed}\n"
        f"Next: {next_stage}\n"
        f"Blockers: {blockers[0] if blockers else 'none'}\n"
        f"Human_gate_needed: {'yes' if gate else 'no'}\n"
        f"Cycle: {cycle}/{HUMAN_GATE_EVERY}\n"
    )
    path.write_text(body, encoding="utf-8")
    return path


def plan_step(
    slug: str,
    *,
    dry_run: bool = False,
    lint_threshold: int = DEFAULT_LINT_THRESHOLD,
    reset: bool = False,
) -> dict[str, Any]:
    state = LoopState() if reset else load_state(slug)
    if state.stopped:
        return {
            "slug": slug,
            "status": "stopped",
            "reason": state.stop_reason,
            "cycle": state.cycle,
        }

    stage_idx = next_stage_index(state.last_stage)
    stage = STAGES[stage_idx]
    lint_errors, lint_note = (0, "dry-run") if dry_run else run_lint_check(dry_run=False)
    if stage == STAGES[-1] and not dry_run:
        lint_errors, lint_note = run_lint_check(dry_run=False)

    advance_cycle(state, stage, lint_errors=lint_errors, lint_threshold=lint_threshold)
    gate = human_gate_needed(state.cycle)
    next_stage = STAGES[next_stage_index(stage)] if not state.stopped else "stop"
    completed = f"Planned stage `{stage}` for slug `{slug}` (cycle {state.cycle})"
    blockers: list[str] = []
    if state.stopped:
        blockers.append(state.stop_reason)
    if gate:
        blockers.append("Human gate: review before Tier 0 edits or bulk rename")

    handoff_file = write_handoff(
        slug,
        completed=completed,
        next_stage=next_stage,
        blockers=blockers,
        cycle=state.cycle % HUMAN_GATE_EVERY or HUMAN_GATE_EVERY,
        gate=gate,
    )
    if not dry_run:
        save_state(slug, state)

    try:
        handoff_rel = str(handoff_file.relative_to(WORKSPACE)).replace("\\", "/")
    except ValueError:
        handoff_rel = str(handoff_file)

    return {
        "slug": slug,
        "status": "stopped" if state.stopped else "ok",
        "stage": stage,
        "cycle": state.cycle,
        "human_gate_needed": gate,
        "lint_errors": lint_errors,
        "lint_note": lint_note[:500],
        "handoff": handoff_rel,
        "dry_run": dry_run,
        "skill_hint": {
            "ingest": "wiki-ingest / obsidian-wiki-ingest / ingest-url",
            "daily-update": "daily-update SKILL",
            "wiki-synthesize": "wiki-synthesize SKILL",
            "wiki-lint": "wiki-lint SKILL + wiki-stage-commit when approved",
        }.get(stage, ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LOOP-4 nested wiki loop planner")
    parser.add_argument("--slug", default="wiki", help="Loop run slug for state files")
    parser.add_argument("--dry-run", action="store_true", help="Plan only; do not persist state")
    parser.add_argument("--reset", action="store_true", help="Reset cycle counter")
    parser.add_argument("--lint-threshold", type=int, default=DEFAULT_LINT_THRESHOLD)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = plan_step(
        args.slug,
        dry_run=args.dry_run,
        lint_threshold=args.lint_threshold,
        reset=args.reset,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status={result['status']} stage={result.get('stage')} cycle={result.get('cycle')}")
        if result.get("handoff"):
            print(f"handoff: {result['handoff']}")
        if result.get("human_gate_needed"):
            print("HUMAN GATE: review handoff before Tier 0 / bulk edits")
    return 0 if result.get("status") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
