# Copy books_rag index from GPU machine (or USB export) to local C:\books_rag.
# No rebuild needed on the destination PC if embedding model matches.
param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,
    [string]$DestPath = "C:\books_rag",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$src = $SourcePath.TrimEnd('\')
if (-not (Test-Path $src)) {
    Write-Error "Source not found: $src"
}

Write-Host "Source: $src"
Write-Host "Dest:   $DestPath"
Write-Host ""
Write-Host "Examples:"
Write-Host "  D:\books_rag_export"
Write-Host "  \\GPU-PC\c`$\books_rag"
Write-Host ""

$robocopyArgs = @(
    $src,
    $DestPath,
    "/E", "/Z", "/FFT", "/R:2", "/W:5",
    "/XD", ".cache",
    "/XF", ".build.lock"
)
if ($WhatIf) {
    $robocopyArgs += "/L"
}

Write-Host "robocopy $($robocopyArgs -join ' ')"
& robocopy @robocopyArgs
$rc = $LASTEXITCODE
if ($rc -ge 8) {
    Write-Error "robocopy failed with exit code $rc"
}

Write-Host ""
Write-Host "Next:"
Write-Host "  python 40_operations/scripts/books_rag_repair_manifest.py --root ."
Write-Host "  python 40_operations/scripts/books_rag_verify.py --json --cpu-ok"
