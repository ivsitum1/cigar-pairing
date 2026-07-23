#!/bin/bash
# worktree_cleanup.sh - List and remove git worktrees
# Usage: ./worktree_cleanup.sh              # list
#        ./worktree_cleanup.sh -r <path>    # remove one

set -e

REMOVE=""
while getopts "r:" opt; do
  case $opt in
    r) REMOVE="$OPTARG" ;;
    *) echo "Usage: $0 [-r <path>]"; exit 1 ;;
  esac
done

MAIN_REPO=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Not in a git repository"; exit 1; }

if [[ -n "$REMOVE" ]]; then
  PATH_RESOLVED=$(cd "$MAIN_REPO" && (cd "$REMOVE" 2>/dev/null && pwd) || echo "$(cd "$MAIN_REPO" && pwd)/$REMOVE")
  echo "Removing worktree: $PATH_RESOLVED"
  git worktree remove "$PATH_RESOLVED" --force
  echo "Done. Prune: git worktree prune"
  exit 0
fi

echo "Worktrees:"
git worktree list
echo ""
echo "To remove: $0 -r <path>"
