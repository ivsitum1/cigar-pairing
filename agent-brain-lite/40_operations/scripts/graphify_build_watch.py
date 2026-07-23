#!/usr/bin/env python3
"""Snapshot Graphify full-build activity for loop monitoring."""
from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = REPO_ROOT / "40_operations" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "40_operations" / "python"))
from common.cursor_paths import cursor_terminals_dir  # noqa: E402

LOG = REPO_ROOT / "40_operations" / "logs" / "graphify_build_watch.jsonl"
BUILD_TERMINAL_HINT = "graphify_brain_build.py --full"


def _find_build_terminal() -> Path | None:
    terminals = cursor_terminals_dir(REPO_ROOT)
    if not terminals or not terminals.is_dir():
        return None
    candidates: list[tuple[float, Path]] = []
    for p in terminals.glob("*.txt"):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if BUILD_TERMINAL_HINT in text or "graphify extract" in text and "--backend ollama" in text:
            candidates.append((p.stat().st_mtime, p))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def _parse_terminal(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    chunk_done = re.findall(r"chunk (\d+)/(\d+) done", text)
    chunk_fail = re.findall(r"chunk (\d+)/(\d+) failed", text)
    last_done = chunk_done[-1] if chunk_done else None
    last_fail = chunk_fail[-1] if chunk_fail else None
    running = "running_for_ms:" in text.split("---")[-1] if "---" in text else False
    exit_m = re.search(r"^exit_code:\s*(\S+)", text, re.MULTILINE)
    elapsed_m = re.search(r"running_for_ms:\s*(\d+)", text)
    return {
        "terminal": str(path.name),
        "running": exit_m is None and "command:" in text,
        "exit_code": exit_m.group(1) if exit_m else None,
        "elapsed_ms": int(elapsed_m.group(1)) if elapsed_m else None,
        "last_chunk_done": f"{last_done[0]}/{last_done[1]}" if last_done else None,
        "last_chunk_failed": f"{last_fail[0]}/{last_fail[1]}" if last_fail else None,
        "chunks_done_count": len(chunk_done),
        "chunks_failed_count": len(chunk_fail),
        "invalid_json_warnings": text.count("invalid JSON"),
        "truncation_warnings": text.count("truncated at max_completion_tokens"),
        "tail": "\n".join(text.strip().splitlines()[-8:]),
    }


def main() -> int:
    report_path = REPO_ROOT / "graphify-out" / "GRAPH_REPORT.md"
    graph_path = REPO_ROOT / "graphify-out" / "graph.json"
    term = _find_build_terminal()
    snap = {
        "ts": datetime.now(UTC).isoformat(),
        "graph_report": report_path.is_file(),
        "graph_json_bytes": graph_path.stat().st_size if graph_path.is_file() else 0,
        "terminal": _parse_terminal(term) if term else None,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snap, ensure_ascii=False) + "\n")

    t = snap.get("terminal") or {}
    if t.get("running"):
        pct = ""
        if t.get("last_chunk_done"):
            cur, tot = t["last_chunk_done"].split("/")
            pct = f" ({int(cur)*100//int(tot)}%)"
        print(
            f"STATUS=RUNNING chunk={t.get('last_chunk_done')}{pct} "
            f"done={t.get('chunks_done_count')} fail={t.get('chunks_failed_count')} "
            f"invalid_json={t.get('invalid_json_warnings')}"
        )
    elif t.get("exit_code") is not None:
        print(f"STATUS=STOPPED exit_code={t['exit_code']} last_done={t.get('last_chunk_done')}")
    elif snap["graph_report"]:
        print("STATUS=COMPLETE graphify build finished (GRAPH_REPORT.md exists, no active terminal)")
    else:
        print("STATUS=UNKNOWN no active graphify terminal found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
