#!/usr/bin/env python3
"""
Awakening Ritual – output a short state summary for Discovery (Pipeline 7B) session start.
Reads .agent/MEMORY.md, handoff log, 30_system/04_documentation/context/log.md and commit.md.
Use before or at Step 1 of Pipeline 7B to avoid re-discovering the same directions.

Usage:
    python 40_operations/scripts/awakening.py
    python 40_operations/scripts/awakening.py --lines 15
    python 40_operations/scripts/awakening.py --memory-path .agent/MEMORY.md --handoff-path .agent/handoff_log.jsonl
"""
from pathlib import Path
import argparse


def _workspace_root() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    if (root / ".agent").exists() or (root / "30_system/behavior_rules").exists():
        return root
    return Path.cwd()


def read_tail(path: Path, lines: int) -> list[str]:
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return content.strip().splitlines()[-lines:] if lines else content.strip().splitlines()
    except OSError:
        return []


def read_handoff_tail(path: Path, n: int) -> list[str]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        return lines[-n:] if n else lines
    except OSError:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Awakening Ritual: state summary for Discovery session start")
    parser.add_argument("--memory-path", default=".agent/MEMORY.md", help="Path to MEMORY.md")
    parser.add_argument("--handoff-path", default=".agent/handoff_log.jsonl", help="Path to handoff log")
    parser.add_argument("--log-path", default="30_system/04_documentation/context/log.md", help="Path to OTA log")
    parser.add_argument("--commit-path", default="30_system/04_documentation/context/commit.md", help="Path to commit/phase")
    parser.add_argument("--lines", "-n", type=int, default=20, help="Last N lines to read from each text file; last N entries for handoff")
    args = parser.parse_args()

    root = _workspace_root()
    memory_path = root / args.memory_path
    handoff_path = root / args.handoff_path
    log_path = root / args.log_path
    commit_path = root / args.commit_path

    out: list[str] = ["--- Awakening (state summary) ---", ""]

    if memory_path.exists():
        mem_lines = read_tail(memory_path, args.lines)
        if mem_lines:
            out.append("**Recent memory (last entries):**")
            out.extend(mem_lines[-min(15, len(mem_lines)):])
            out.append("")
    else:
        out.append("(No .agent/MEMORY.md found.)")
        out.append("")

    if handoff_path.exists():
        handoff_lines = read_handoff_tail(handoff_path, args.lines)
        if handoff_lines:
            out.append("**Recent handoffs (last entries):**")
            for line in handoff_lines[-10:]:
                out.append(f"  {line[:120]}..." if len(line) > 120 else f"  {line}")
            out.append("")
    else:
        out.append("(No handoff log found.)")
        out.append("")

    if log_path.exists():
        log_lines = read_tail(log_path, args.lines)
        if log_lines:
            out.append("**Recent OTA log:**")
            out.extend(log_lines[-10:])
            out.append("")
    else:
        out.append("(No 30_system/04_documentation/context/log.md found.)")
        out.append("")

    if commit_path.exists():
        commit_content = commit_path.read_text(encoding="utf-8", errors="replace").strip()
        if commit_content:
            out.append("**Current phase (commit.md):**")
            out.append(commit_content[:500] + "..." if len(commit_content) > 500 else commit_content)
            out.append("")

    out.append("--- End state summary. Use above to avoid re-discovering same directions. ---")
    print("\n".join(out))


if __name__ == "__main__":
    main()
