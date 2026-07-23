#!/bin/bash
# Post-commit: append current commit to auto changelog (no amend — avoids hook recursion).
# Install: cp 40_operations/scripts/post-commit-hook.sh .git/hooks/post-commit && chmod +x .git/hooks/post-commit
# Optional fold: git add 30_system/docs/CHANGELOG_AUTO.md 30_system/docs/CHANGELOG_AUTO.jsonl && git commit --amend --no-edit --no-verify
#
# Skip hook (e.g. amend without double-append): SKIP_CHANGELOG=1 git commit --amend --no-edit

cd "$(git rev-parse --show-toplevel)"

if [ -n "${SKIP_CHANGELOG:-}" ]; then
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  python3 40_operations/scripts/changelog_auto.py
else
  python 40_operations/scripts/changelog_auto.py
fi

exit 0
