# Weekly brain maintenance: regenerate graph indexes, bound memory growth,
# report link integrity, and emit a freshness report. Safe to run repeatedly.
# Invoked by the AgentRules-WeeklyMaintenance scheduled task, or by hand.

$ErrorActionPreference = "Continue"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Scripts = Join-Path $RepoRoot "40_operations\scripts"
$LogDir = Join-Path $RepoRoot "40_operations\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$Log = Join-Path $LogDir ("weekly_maintenance_{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))
$env:PYTHONPATH = $Scripts

function Step($name, $cmd) {
    "=== $name @ $(Get-Date -Format o) ===" | Tee-Object -FilePath $Log -Append
    & $cmd 2>&1 | Tee-Object -FilePath $Log -Append
}

Set-Location $RepoRoot
Step "regenerate folder indexes" { python "$Scripts\generate_folder_md_indexes.py" --root . }
Step "memory maintenance"        { python "$Scripts\memory_maintenance.py" }
Step "link integrity report"     { python "$Scripts\check_md_links.py" --root . --show 0 }
Step "brain freshness"           { python "$Scripts\brain_freshness.py" }

# Autonomous learning: distil memory signal into committed skill/rule updates.
"=== weekly learning @ $(Get-Date -Format o) ===" | Tee-Object -FilePath $Log -Append
& "$Scripts\run_weekly_learning.ps1" 2>&1 | Tee-Object -FilePath $Log -Append

Write-Host "Weekly maintenance complete. Log: $Log"
