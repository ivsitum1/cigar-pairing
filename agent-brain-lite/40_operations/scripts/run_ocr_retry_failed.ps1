# Retry failed PDF extractions with routing: PyMuPDF raster Paddle vs PyPDF2 text layer.
param(
    [string]$Root = ".",
    [switch]$DryRun,
    [switch]$SkipMillerPypdf,
    [switch]$SkipRaster
)

$ErrorActionPreference = "Stop"
$env:FLAGS_use_mkldnn = "0"
$env:FLAGS_use_onednn = "0"
$env:FLAGS_enable_mkldnn = "0"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"
$env:PADDLE_OCR_RASTER_FALLBACK = "1"

$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location (Resolve-Path (Join-Path $Repo $Root)).Path
$Py = Join-Path $Repo ".venv-ocr\Scripts\python.exe"
$Extract = Join-Path $Repo "40_operations\scripts\extract_pdf_library_to_md.py"
$Diagnose = Join-Path $Repo "40_operations\scripts\diagnose_pdf_ocr_gaps.py"

if (-not (Test-Path $Py)) {
    Write-Error "Missing .venv-ocr. Run: .\40_operations\scripts\install_paddle_ocr.ps1"
}

Write-Host "=== Diagnose gaps ==="
& $Py $Diagnose --root $Repo

if ($DryRun) {
    Write-Host "DryRun: no extraction started."
    exit 0
}

if (-not $SkipMillerPypdf) {
    Write-Host "=== Miller / OOM: PyPDF2 text layer ==="
    & $Py $Extract --root $Repo --ocr off --retry-failed --prune-stale `
        --only-prefix "Miller_Anesthesia_10e_2024"
    & $Py $Extract --root $Repo --ocr off --retry-failed --prune-stale `
        --only-prefix "Miller&_039_s Anesthesia"
}

if (-not $SkipRaster) {
    Write-Host "=== Failed PDFs: Paddle + PyMuPDF raster fallback ==="
    & $Py $Extract --root $Repo --ocr paddle --force-ocr --retry-failed --prune-stale --report auto
}

Write-Host "=== Refresh migration report ==="
& $Py (Join-Path $Repo "40_operations\scripts\report_pdf_migration.py") --root $Repo

Write-Host "Done. See data/pdf_extract/OCR_RETRY_STRATEGY.md and migration_report_latest.md"
