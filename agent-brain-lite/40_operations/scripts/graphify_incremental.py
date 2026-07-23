#!/usr/bin/env python3
"""Commit-aware partial Graphify update from git diff (LARGER maintenance)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
GRAPH_OUT = WORKSPACE / "graphify-out"
STATE = GRAPH_OUT / "incremental_state.json"


def _git_changed_files(ref: str = "HEAD") -> list[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", ref],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=False,
        )
        if out.returncode != 0:
            out = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                check=False,
            )
        return [ln.strip().replace("\\", "/") for ln in out.stdout.splitlines() if ln.strip()]
    except OSError:
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Graphify incremental diff manifest")
    parser.add_argument("--ref", default="HEAD", help="Git ref to diff against (default: unstaged+staged vs HEAD)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    changed = _git_changed_files(args.ref)
    code_ext = {".py", ".md", ".mdc", ".json", ".ts", ".tsx", ".js"}
    targets = [p for p in changed if Path(p).suffix.lower() in code_ext]

    manifest = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "changed_files": targets,
        "count": len(targets),
        "action": "reindex_nodes_for_paths",
        "note": "Run full graphify build for merged.json if count > 50 or graph missing",
    }

    GRAPH_OUT.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        STATE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
