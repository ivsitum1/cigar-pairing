#!/bin/bash
# worktree_add.sh - Create git worktree with symlinks for .env
# Usage: ./worktree_add.sh -b <branch> -p <dir>
# Example: ./worktree_add.sh -b feature/xyz -p ../agent-rules-feature-xyz

set -e

BRANCH=""
PATH_ARG=""

while getopts "b:p:" opt; do
  case $opt in
    b) BRANCH="$OPTARG" ;;
    p) PATH_ARG="$OPTARG" ;;
    *) echo "Usage: $0 -b <branch> -p <path>"; exit 1 ;;
  esac
done

if [[ -z "$BRANCH" || -z "$PATH_ARG" ]]; then
  echo "Usage: $0 -b <branch> -p <path>"
  exit 1
fi

MAIN_REPO=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Not in a git repository"; exit 1; }
PATH_RESOLVED=$(cd "$MAIN_REPO" && (cd "$PATH_ARG" 2>/dev/null && pwd) || echo "$(cd "$MAIN_REPO" && pwd)/$PATH_ARG")

echo "Creating worktree: branch=$BRANCH path=$PATH_RESOLVED"
git worktree add -b "$BRANCH" "$PATH_RESOLVED"

# Symlink .env if it exists in main repo
MAIN_ENV="$MAIN_REPO/.env"
if [[ -f "$MAIN_ENV" && ! -e "$PATH_RESOLVED/.env" ]]; then
  ln -s "$MAIN_ENV" "$PATH_RESOLVED/.env"
  echo "Symlinked .env -> main repo"
fi

# Create .env.local for DB isolation
SAFE_BRANCH=$(echo "$BRANCH" | tr '/\' '_')
ENV_LOCAL="$PATH_RESOLVED/.env.local"
if [[ ! -f "$ENV_LOCAL" ]]; then
  echo "DB_NAME=project_test_$SAFE_BRANCH" > "$ENV_LOCAL"
  echo "Created .env.local with DB_NAME=project_test_$SAFE_BRANCH"
fi

echo ""
echo "Next: cd \"$PATH_RESOLVED\" then open in Cursor"
