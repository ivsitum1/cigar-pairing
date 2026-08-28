# Weekly crawl + map of HR drink shops (Tier A/B apply, C ask-queue, D staging dry-run).
# Does not commit and does not run in GitHub Actions.
#
#   powershell -File scripts/schedule-shop-gaps-scan.ps1 -Install
#   powershell -File scripts/schedule-shop-gaps-scan.ps1 -RunNow
#   powershell -File scripts/schedule-shop-gaps-scan.ps1 -Uninstall
#
# Run from app/:  powershell -File scripts/schedule-shop-gaps-scan.ps1 -Install

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$RunNow,
    [string]$Time = "08:00"
)

$ErrorActionPreference = "Stop"
$TaskName = "CigarRum-ShopGapsScan"
$ScriptsDir = $PSScriptRoot
$AppDir = Split-Path -Parent $ScriptsDir
$OutDir = Join-Path $ScriptsDir "output"
$Log = Join-Path $OutDir "shop-gaps-scan.log"
$Python = (Get-Command python -ErrorAction Stop).Source

function Invoke-Scan {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $Log -Value "`n==== $stamp ===="
    Push-Location $AppDir
    try {
        & $Python "scripts\scan-drink-shop-gaps.py" *>> $Log
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        & $Python "scripts\merge-drink-shops-additive.py" --apply --tiers a,b *>> $Log
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        & $Python "scripts\ingest-staged-drink-shops.py" --dry-run *>> $Log
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        & $Python "scripts\enrich-shop-ingest-stubs.py" --apply *>> $Log
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        & $Python "scripts\audit_drink_shops_preship.py" --check *>> $Log
        # audit may exit 1 (informational); do not fail the whole weekly task
        return 0
    }
    finally {
        Pop-Location
    }
}

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task '$TaskName'."
    exit 0
}

if ($RunNow) {
    $code = Invoke-Scan
    Write-Host "Pipeline exit code: $code (log: $Log)"
    Write-Host "Report: $(Join-Path $OutDir 'shop_gaps_report.json')"
    Write-Host "Staging: $(Join-Path $OutDir 'shop_ingest_staging.json')"
    Write-Host "Ask queue: $(Join-Path $OutDir 'catalog_ask_queue.json')"
    exit $code
}

if (-not $Install) {
    Write-Host @"
Usage:
  -Install     register a weekly Monday task at $Time
  -Uninstall   remove the task
  -RunNow      run full drink-shop pipeline once
  -Time 08:00  weekly start time (with -Install)

Pipeline:
  1. scan-drink-shop-gaps.py          (crawl + tier A/B/C/D + ask + staging)
  2. merge-drink-shops-additive.py --apply --tiers a,b
  3. ingest-staged-drink-shops.py --dry-run   (manual --apply after review)
  4. audit_drink_shops_preship.py --check
"@
    exit 1
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$arg = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -RunNow"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg -WorkingDirectory $AppDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $Time
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "Registered '$TaskName' weekly on Monday at $Time."
Write-Host "Log: $Log"
Write-Host "Report: $(Join-Path $OutDir 'shop_gaps_report.json')"
Write-Host "The task does not commit. Review git diff / staging / ask-queue before shipping."
