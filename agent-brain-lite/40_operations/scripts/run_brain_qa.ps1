# Brain QA gate (PowerShell). Exit 1 if any check fails.
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

Write-Host "=== brain_health ==="
python 40_operations/scripts/brain_health.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== skill_registry validate ==="
python 40_operations/scripts/skill_registry.py validate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== workspace_inventory_audit ==="
python 40_operations/scripts/workspace_inventory_audit.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== brain_audit ==="
python 40_operations/scripts/brain_audit.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== pytest ==="
python -m pytest 40_operations/tests -q --tb=line
exit $LASTEXITCODE
