#!/bin/bash
# run_all_checks.sh - Pre-commit validation, brain_status, optional pytest
# Run from repo root

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== 1. Pre-commit validation ==="
"$ROOT/40_operations/scripts/pre-commit-hook.sh"

echo ""
echo "=== 2. Brain status ==="
python3 "$ROOT/40_operations/scripts/brain_status.py"

echo ""
echo "=== 3. Brain health ==="
python3 "$ROOT/40_operations/scripts/brain_health.py" --json

echo ""
echo "=== 4. Skill registry ==="
python3 "$ROOT/40_operations/scripts/skill_registry.py" validate

echo ""
echo "=== 5. Error ops audit ==="
python3 "$ROOT/.cursor/scripts/error_ops.py" audit

echo ""
echo "=== 6. Rules link validation ==="
python3 "$ROOT/40_operations/scripts/validate_rules_links.py" --root "$ROOT"

echo ""
echo "=== 7. Non-markdown bridge validation ==="
python3 "$ROOT/40_operations/scripts/validate_non_md_index.py" --root "$ROOT"

echo ""
echo "=== 8. Workspace optimization check ==="
python3 "$ROOT/40_operations/scripts/workspace_optimization_check.py" --root "$ROOT"

echo ""
echo "=== 9. Pytest ==="
python3 -m pytest 40_operations/tests/ -q

echo ""
echo "All checks passed"
