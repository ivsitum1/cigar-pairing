# Monthly arXiv skill scout — run from Task Scheduler (repo root as cwd).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $RepoRoot
& py -3 "40_operations\scripts\arxiv_monthly_scan.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& py -3 "40_operations\scripts\arxiv_self_evolving_scan.py" --period monthly
exit $LASTEXITCODE
