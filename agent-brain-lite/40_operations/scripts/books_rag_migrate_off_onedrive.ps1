# Move books RAG index off OneDrive: keep C:\books_rag canonical, remove repo chroma copies.
param(
    [switch]$SetUserEnv,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Legacy = Join-Path $Root "data\books_rag"
$Canonical = "C:\books_rag"

Write-Host "Canonical index: $Canonical"
Write-Host "Legacy repo path: $Legacy"

if ($SetUserEnv) {
    if ($WhatIf) {
        Write-Host "[WhatIf] setx BOOKS_RAG_DATA_DIR $Canonical"
    } else {
        setx BOOKS_RAG_DATA_DIR $Canonical | Out-Null
        $env:BOOKS_RAG_DATA_DIR = $Canonical
        Write-Host "Set user env BOOKS_RAG_DATA_DIR=$Canonical (new shells only for setx)."
    }
}

$removeNames = @(
    "chroma",
    "manifest.json",
    "build_progress.json",
    "build_progress-*.json",
    "manifest-*.json",
    "full_build.log",
    "full_build-*.log",
    "rag_rebuild_watchdog.log",
    "eval_report.json",
    "install_status.json",
    "build_process_status.json",
    "smoke_hook.json",
    ".build.lock",
    ".cache"
)

foreach ($pattern in $removeNames) {
    Get-ChildItem -Path $Legacy -Filter $pattern -Force -ErrorAction SilentlyContinue | ForEach-Object {
        if ($WhatIf) {
            Write-Host "[WhatIf] Remove $($_.FullName)"
        } else {
            Write-Host "Remove $($_.FullName)"
            Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction Stop
        }
    }
}

if (-not (Test-Path $Canonical)) {
    New-Item -ItemType Directory -Path $Canonical -Force | Out-Null
    Write-Host "Created $Canonical"
}

if (-not $WhatIf) {
    if (-not (Test-Path (Join-Path $Canonical "chroma"))) {
        Write-Host "WARNING: $Canonical\chroma missing. Run:"
        Write-Host "  python 40_operations/scripts/build_books_rag_index.py --root `"$Root`" --force"
    } else {
        Write-Host "OK: chroma present under $Canonical"
    }
}

Write-Host "Done. Repo data/books_rag keeps README.md + .gitkeep only."
