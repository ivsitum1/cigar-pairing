#!/bin/sh
# Project post-commit: append to 05_version_control/CHANGELOG_AUTO.*
# Installed by project_init.py into <project>/.git/hooks/post-commit
#
# Skip: SKIP_CHANGELOG=1 git commit --amend --no-edit

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0

if [ -n "$SKIP_CHANGELOG" ]; then
  exit 0
fi

BRAIN="$ROOT/agent-rules"
if [ ! -f "$BRAIN/40_operations/scripts/project_changelog_auto.py" ]; then
  if [ -n "$AGENT_RULES_ROOT" ] && [ -f "$AGENT_RULES_ROOT/40_operations/scripts/project_changelog_auto.py" ]; then
    BRAIN="$AGENT_RULES_ROOT"
  else
    exit 0
  fi
fi

if command -v python3 >/dev/null 2>&1; then
  python3 "$BRAIN/40_operations/scripts/project_changelog_auto.py" --root "$ROOT"
else
  python "$BRAIN/40_operations/scripts/project_changelog_auto.py" --root "$ROOT"
fi
