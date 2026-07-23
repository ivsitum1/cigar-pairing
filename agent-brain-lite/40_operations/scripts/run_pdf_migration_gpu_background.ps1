# Starts full PaddleOCR migration on GPU + RAG rebuild; logs to data/pdf_extract/
param([string]$Root = ".")

$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$LogDir = Join-Path $Repo "data\pdf_extract"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$OutLog = Join-Path $LogDir ("background_migration_{0:yyyy-MM-dd_HHmm}.log" -f (Get-Date))

$env:PADDLE_OCR_DEVICE = "gpu"
$env:FLAGS_use_mkldnn = "0"
$env:FLAGS_use_onednn = "0"
$env:FLAGS_enable_mkldnn = "0"

Set-Location $Repo

# Watchdog optional: set $env:PDF_MIGRATION_WATCHDOG=1 before starting background migration.
if ($env:PDF_MIGRATION_WATCHDOG -eq "1") {
    $WatchScript = Join-Path $Repo "40_operations\scripts\watch_pdf_migration.ps1"
    Start-Process powershell -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $WatchScript,
        "-Root", $Root,
        "-IntervalMinutes", "15",
        "-StaleMinutes", "90",
        "-AutoKillStuck"
    ) -WindowStyle Hidden
}

& (Join-Path $Repo "40_operations\scripts\run_pdf_paddle_migration.ps1") `
    -Root $Root -RebuildRag *>&1 | Tee-Object -FilePath $OutLog
