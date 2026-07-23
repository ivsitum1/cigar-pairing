"""Automatic verifier learning cycle: export → incremental train (usage-driven)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .verifier_ml import (
    MIN_LABELED_ROWS,
    collect_training_rows,
    maybe_incremental_train,
    ml_blend_active,
)
from .verifier_usage_ledger import ledger_path, read_rows

WORKSPACE = Path(__file__).resolve().parents[3]
STATE_PATH = WORKSPACE / ".agent" / "memory" / "verifier_learning_state.json"
PROGRESS_PATH = WORKSPACE / ".agent" / "memory" / "verifier_training_progress.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(0, int(raw))
    except ValueError:
        return default


def cycle_disabled() -> bool:
    return os.environ.get("VERIFIER_LEARNING_CYCLE_DISABLED", "").strip() in {"1", "true", "TRUE"}


def load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def labeled_row_count() -> int:
    return len(collect_training_rows())


def ledger_event_count() -> int:
    return len(read_rows())


def should_run_cycle(*, trigger: str, state: dict[str, Any] | None = None) -> tuple[bool, str]:
    """Throttle heavy cycle work to avoid hook latency."""
    if cycle_disabled():
        return False, "cycle_disabled"
    st = state if state is not None else load_state()
    if trigger in {"sessionEnd", "stop", "manual", "daily"}:
        return True, f"trigger_{trigger}"

    min_interval_sec = _env_int("VERIFIER_CYCLE_MIN_INTERVAL_SEC", 600)
    min_ledger_delta = _env_int("VERIFIER_CYCLE_MIN_LEDGER_DELTA", 5)
    last_ts = st.get("last_cycle_at")
    last_ledger = int(st.get("last_cycle_ledger_count") or 0)
    current_ledger = ledger_event_count()
    if last_ts:
        try:
            last_dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
            if elapsed < min_interval_sec and (current_ledger - last_ledger) < min_ledger_delta:
                return False, "throttled"
        except ValueError:
            pass
    if (current_ledger - last_ledger) >= min_ledger_delta:
        return True, "ledger_delta"
    return False, "no_threshold"


def _run_rcml_export() -> dict[str, Any]:
    script = WORKSPACE / "40_operations" / "scripts" / "rcml_export_live.py"
    if not script.is_file():
        return {"ok": False, "reason": "script_missing"}
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=120,
            check=False,
        )
        if proc.returncode != 0:
            return {"ok": False, "reason": "export_failed", "stderr": (proc.stderr or "")[:500]}
        try:
            return {"ok": True, **json.loads(proc.stdout or "{}")}
        except json.JSONDecodeError:
            return {"ok": True, "raw": (proc.stdout or "")[:300]}
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}


def _write_progress(payload: dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_learning_cycle(*, trigger: str = "manual", force: bool = False) -> dict[str, Any]:
    """
    Usage-driven pipeline:
    1. Count labeled rows (ledger + correction evals)
    2. Export live Rcml JSONL (deduped)
    3. Incremental sklearn train when enough new rows accumulated
    """
    if cycle_disabled() and not force:
        return {"ok": False, "reason": "cycle_disabled"}

    state = load_state()
    run, why = should_run_cycle(trigger=trigger, state=state)
    if not run and not force:
        return {"ok": True, "skipped": True, "reason": why, "labeled_rows": labeled_row_count()}

    row_count = labeled_row_count()
    min_rows = _env_int("VERIFIER_ML_MIN_ROWS", MIN_LABELED_ROWS)
    export_result = _run_rcml_export()
    train_result = maybe_incremental_train(force=force or trigger in {"sessionEnd", "stop", "daily"})

    state.update(
        {
            "last_cycle_at": _utc_now(),
            "last_cycle_trigger": trigger,
            "last_cycle_ledger_count": ledger_event_count(),
            "last_labeled_row_count": row_count,
            "last_export": export_result,
            "last_train": train_result,
        }
    )
    save_state(state)

    progress = {
        "updated_at": _utc_now(),
        "labeled_rows": row_count,
        "min_rows_for_train": min_rows,
        "rows_until_train": max(0, min_rows - row_count),
        "ml_blend_active": ml_blend_active(),
        "last_train_row_count": state.get("last_train_row_count", train_result.get("train_count")),
        "ledger_path": str(ledger_path()),
        "trigger": trigger,
    }
    _write_progress(progress)

    return {
        "ok": True,
        "trigger": trigger,
        "labeled_rows": row_count,
        "export": export_result,
        "train": train_result,
        "ml_blend_active": progress["ml_blend_active"],
        "progress": progress,
    }
