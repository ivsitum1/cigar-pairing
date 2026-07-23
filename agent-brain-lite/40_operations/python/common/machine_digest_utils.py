"""Machine weekly digest helpers (secondary count, brain health summary)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def latest_digest_path(task_dir: Path) -> Path | None:
    candidates = sorted(task_dir.glob("machine_digest_*.md"), reverse=True)
    return candidates[0] if candidates else None


def count_digest_proposals(digest_path: Path) -> int:
    if not digest_path.is_file():
        return 0
    text = digest_path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"^### Proposal \d+:", text, flags=re.MULTILINE))


def count_pending_proposals(task_dir: Path, week: str | None = None) -> tuple[int, str | None]:
    """Return (pending_count, digest_filename). Pending = defer verdict in decisions JSON."""
    digest = latest_digest_path(task_dir)
    if digest is None:
        return 0, None
    week_match = re.search(r"machine_digest_(\d{4}-W\d{2})\.md$", digest.name)
    label = week or (week_match.group(1) if week_match else None)
    decisions_path = task_dir / f"machine_digest_decisions_{label}.json" if label else None
    if decisions_path and decisions_path.is_file():
        try:
            data = json.loads(decisions_path.read_text(encoding="utf-8"))
            pending = sum(1 for d in data.get("decisions", []) if d.get("verdict") == "defer")
            if pending:
                return pending, digest.name
        except json.JSONDecodeError:
            pass
    return count_digest_proposals(digest), digest.name


def secondary_count_message(task_dir: Path) -> str | None:
    count, fname = count_pending_proposals(task_dir)
    if count <= 0 or not fname:
        return None
    return (
        f'Secondary queue: {count} upgrade proposals in `{fname}` (pending review). '
        'Say "open machine digest" for detail.'
    )


def run_brain_health_summary(repo_root: Path) -> str:
    script = repo_root / "40_operations" / "scripts" / "brain_health.py"
    if not script.is_file():
        return "brain_health script missing"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode not in (0, 1) and not result.stdout.strip():
            return f"brain_health error (exit {result.returncode})"
        data = json.loads(result.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError) as exc:
        return f"brain_health unavailable: {exc}"
    if data.get("ok"):
        return "PASS"
    failed: list[str] = []
    for key, val in data.items():
        if key == "ok":
            continue
        if val in ("", None, {}, []):
            continue
        if isinstance(val, dict) and any(str(v).startswith("FAIL") or v is False for v in val.values()):
            failed.append(key)
        elif isinstance(val, str) and ("FAIL" in val or "missing" in val.lower()):
            failed.append(key)
    return "FAIL: " + ", ".join(failed) if failed else "FAIL (see brain_health --json)"
