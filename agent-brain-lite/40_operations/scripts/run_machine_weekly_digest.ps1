# Weekly Machine digest runner (brain repo).
param(
    [switch]$DryRun,
    [string]$EnvFile = ""
)

$ErrorActionPreference = "Continue"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

$envPath = $EnvFile
if (-not $envPath) {
    $envPath = Join-Path $Root ".env.local"
}
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $name = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim().Trim('"').Trim("'")
        if ($name) { Set-Item -Path "Env:$name" -Value $value }
    }
    Write-Host "Loaded env from $envPath"
}

$pyArgs = @("40_operations/scripts/machine_weekly_digest.py")
if ($DryRun) { $pyArgs += "--dry-run" }

python @pyArgs
if ($LASTEXITCODE -eq 0 -and -not $DryRun) {
    python 40_operations/scripts/dreaming_daemon.py
}
exit $LASTEXITCODE
