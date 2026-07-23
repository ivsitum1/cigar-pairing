# run_all_checks.ps1 - Pre-commit validation, brain_status, optional pytest
# Run from repo root

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

Write-Host "=== 1. Pre-commit validation ===" -ForegroundColor Cyan
& "$PSScriptRoot\pre-commit-hook.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 2. Brain status ===" -ForegroundColor Cyan
python "$PSScriptRoot\brain_status.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 3. Brain health ===" -ForegroundColor Cyan
python "$PSScriptRoot\brain_health.py" --json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 4. Skill registry ===" -ForegroundColor Cyan
python "$PSScriptRoot\skill_registry.py" validate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 5. Error ops audit ===" -ForegroundColor Cyan
python "$Root\.cursor\scripts\error_ops.py" audit

Write-Host "`n=== 6. Rules link validation ===" -ForegroundColor Cyan
python "$PSScriptRoot\validate_rules_links.py" --root "$Root"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 7. Non-markdown bridge validation ===" -ForegroundColor Cyan
python "$PSScriptRoot\validate_non_md_index.py" --root "$Root"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 8. Workspace optimization check ===" -ForegroundColor Cyan
python "$PSScriptRoot\workspace_optimization_check.py" --root "$Root"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 9. Pytest ===" -ForegroundColor Cyan
python -m pytest 40_operations/tests/ -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nAll checks passed" -ForegroundColor Green
