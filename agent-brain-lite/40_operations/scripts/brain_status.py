#!/usr/bin/env python3
"""Quick status of the whole system. Exit 0 if ok, 1 if something missing."""
import json
import sys
from pathlib import Path

AGENT_RULES = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = AGENT_RULES.parent if (AGENT_RULES.parent / "01_input").exists() else AGENT_RULES
AGENT = PROJECT_ROOT / ".agent"
CONTEXT = PROJECT_ROOT / "30_system/04_documentation" / "context"
CURSOR = PROJECT_ROOT / ".cursor"

MEMORY = AGENT / "MEMORY.md"
HANDOFF = AGENT / "handoff_log.jsonl"
ERROR_LOG = CURSOR / "errors" / "error_log.jsonl"
MAIN = CONTEXT / "main.md"
COMMIT = CONTEXT / "commit.md"
LOG = CONTEXT / "log.md"
TASK = AGENT / "task"


def _configure_utf8_stdout() -> None:
    """
    Ensure we can print UTF-8 characters on Windows terminals.
    """
    try:
        # Python 3.7+: reconfigure available on sys.stdout/stderr.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        # If reconfiguration fails, we still want the status command to work.
        pass


def main() -> int:
    _configure_utf8_stdout()
    issues = []

    # MEMORY last 5 entries (lines matching [YYYY-MM-DD])
    print("--- MEMORY (last 5) ---")
    if MEMORY.exists():
        all_lines = MEMORY.read_text(encoding="utf-8").split("\n")
        entries = [l for l in all_lines if l.strip() and l.strip().startswith("[2") and "]" in l][-5:]
        lines = entries or [l for l in all_lines if l.strip() and not l.startswith("#") and not l.startswith("---") and "**" not in l[:5]][-5:]
        for line in lines:
            print(line)
    else:
        print("(none)")
        issues.append("MEMORY.md missing")

    # handoff last 3
    print("\n--- Handoff (last 3) ---")
    if HANDOFF.exists():
        lines = [
            l
            for l in HANDOFF.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            if l.strip()
        ]
        for line in lines[-3:]:
            try:
                j = json.loads(line)
                print(f"  {j.get('from','?')} -> {j.get('to','?')}: {j.get('done','')}")
            except json.JSONDecodeError:
                print(f"  {line[:60]}...")
    else:
        print("(none)")

    # error count
    print("\n--- Errors ---")
    if ERROR_LOG.exists():
        n = sum(
            1
            for l in ERROR_LOG.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            if l.strip()
        )
        print(f"  error_log: {n} entries")
    else:
        print("  error_log: (none)")

    # research list
    print("\n--- Research / task output ---")
    if TASK.exists():
        md_files = list(TASK.glob("*.md"))
        if md_files:
            for f in sorted(md_files)[-5:]:
                print(f"  {f.name}")
        else:
            print("  (none)")
    else:
        print("  (none)")

    # Checks
    print("\n--- Checks ---")
    for name, path in [("main.md", MAIN), ("commit.md", COMMIT), ("log.md", LOG)]:
        ok = path.exists()
        print(f"  {name}: {'ok' if ok else 'MISSING'}")
        if not ok:
            issues.append(name)

    if issues:
        print(f"\nIssues: {', '.join(issues)}")
        return 1
    print("\nAll ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
