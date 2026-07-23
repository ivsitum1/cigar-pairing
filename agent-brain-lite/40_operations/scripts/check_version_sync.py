#!/usr/bin/env python3
"""Check that VERSION.md was updated when rules files changed."""
from __future__ import annotations

import subprocess
import sys

_BEHAVIOR_RULES_SKIP = frozenset(
    {
        "30_system/behavior_rules/CHANGELOG.md",
        "30_system/behavior_rules/VERSION.md",
        "30_system/behavior_rules/README.md",
    }
)


def _is_rules_file(path: str) -> bool:
    if path.startswith(".cursor/rules/") and path.endswith(".mdc"):
        return True
    if path.startswith("30_system/behavior_rules/") and path.endswith(".md"):
        return path not in _BEHAVIOR_RULES_SKIP
    return False


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    changed = [f for f in result.stdout.strip().split("\n") if f]
    rules_changed = [f for f in changed if _is_rules_file(f)]
    version_updated = any("VERSION" in f for f in changed)

    if rules_changed and not version_updated:
        print("WARNING: rules files changed but VERSION.md not staged.")
        print("Changed rules files:", rules_changed)
        print("Run: bump VERSION.md (patch for content edits) and stage it.")
        # Exit 0 = warning only, not blocking (change to sys.exit(1) to enforce hard block)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
