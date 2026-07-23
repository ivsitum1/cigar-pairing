# Install Windows Task Scheduler job for Machine weekly digest (brain repo).
# Usage (repo root, elevated optional):
#   powershell -NoProfile -ExecutionPolicy Bypass -File 40_operations/scripts/install_machine_weekly_task.ps1

param(
    [string]$TaskName = "AgentRules-MachineWeeklyDigest",
    [string]$WeekDay = "Sunday",
    [string]$Time = "08:00",
    [string]$EnvFile = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Runner = Join-Path $Root "40_operations\scripts\run_machine_weekly_digest.ps1"

if (-not (Test-Path $Runner)) {
    Write-Error "Runner not found: $Runner"
}

$argList = "-NoProfile -ExecutionPolicy Bypass -File `"$Runner`""
if ($EnvFile) {
    $argList += " -EnvFile `"$EnvFile`""
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argList
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $WeekDay -At $Time
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "Installed scheduled task: $TaskName ($WeekDay $Time)"
Write-Host "Runner: $Runner"
