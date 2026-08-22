# Weekly local ping of known shop product URLs (stock only).
# Does not commit, does not run in GitHub Actions.
#
#   powershell -File scripts/schedule-availability-refresh.ps1 -Install
#   powershell -File scripts/schedule-availability-refresh.ps1 -RunNow
#   powershell -File scripts/schedule-availability-refresh.ps1 -Uninstall
#
# Run from app/:  powershell -File scripts/schedule-availability-refresh.ps1 -Install

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$RunNow,
    [string]$Time = "09:00"
)

$ErrorActionPreference = "Stop"
$TaskName = "CigarRum-AvailabilityRefresh"
$ScriptsDir = $PSScriptRoot
$AppDir = Split-Path -Parent $ScriptsDir
$OutDir = Join-Path $ScriptsDir "output"
$Log = Join-Path $OutDir "availability-refresh.log"
$Python = (Get-Command python -ErrorAction Stop).Source

function Invoke-Refresh {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $Log -Value "`n==== $stamp ===="
    Push-Location $AppDir
    try {
        & $Python "scripts\refresh-availability.py" --sleep 2 *>> $Log
        return $LASTEXITCODE
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
    $code = Invoke-Refresh
    Write-Host "Refresh exit code: $code (log: $Log)"
    exit $code
}

if (-not $Install) {
    Write-Host @"
Usage:
  -Install     register a weekly Sunday task at $Time
  -Uninstall   remove the task
  -RunNow      run refresh-availability.py once
  -Time 09:00  weekly start time (with -Install)
"@
    exit 1
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$arg = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -RunNow"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg -WorkingDirectory $AppDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At $Time
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "Registered '$TaskName' weekly on Sunday at $Time."
Write-Host "Log: $Log"
Write-Host "The task does not commit. After a run, review git diff and commit when the stock snapshot should ship."
