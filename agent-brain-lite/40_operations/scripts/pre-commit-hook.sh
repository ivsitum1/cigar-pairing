#!/bin/bash
# Pre-commit hook for agent-rules repo
# Install: cp 40_operations/scripts/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

# 1. Validate Cursor rules frontmatter
if [ -d ".cursor/rules" ]; then
  for f in .cursor/rules/*.mdc; do
    [ -f "$f" ] || continue
    if ! head -1 "$f" | grep -q "^---"; then
      echo "Missing frontmatter: $f"
      exit 1
    fi
  done
fi

# 2. Check for common R mistakes (error memory items)
# Skip rubrics (pattern detectors) and tests — they mention subset/setwd/T/F in strings
if git diff --cached --name-only | grep -q "\.R$"; then
  for f in $(git diff --cached --name-only | grep "\.R$"); do
    [ -f "$f" ] || continue
    case "$f" in
      40_operations/tests/*) continue ;;
      *) ;;
    esac
    if grep -n "subset(" "$f" 2>/dev/null | grep -v "#" | grep -q .; then
      echo "Warning: $f uses subset() - prefer dplyr::filter()"
    fi
    if grep -n "setwd(" "$f" 2>/dev/null | grep -v "#" | grep -q .; then
      echo "Error: $f uses setwd(). Use here::here() instead."
      exit 1
    fi
    if grep -nE '\bT\b|\bF\b' "$f" 2>/dev/null | grep -v "#" | grep -v "TRUE\|FALSE" | grep -v 'Pr(>F)' | grep -q .; then
      echo "Warning: $f may use T/F - use TRUE/FALSE"
    fi
  done
fi

# 3. Validate skill registry consistency
echo "Validating skill registry..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/skill_registry.py" validate || exit 1

# 4. Changelog runs in post-commit only (see 40_operations/scripts/post-commit-hook.sh)

# 5. Manuscript changed - remind about AI check
if git diff --cached --name-only | grep -qE "manuscript|paper|draft"; then
  echo "Manuscript changed - consider running AI detection check"
fi

echo "Pre-commit checks passed"
exit 0
