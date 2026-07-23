# Run one incremental books RAG index batch (default 50 new/changed files).
# Schedule nightly: Task Scheduler -> python build script or this wrapper.
param(
    [int]$MaxFiles = 50,
    [string]$Root = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
)

Set-Location $Root
. (Join-Path $Root "40_operations\scripts\_books_rag_paths.ps1")
$env:BOOKS_RAG_DATA_DIR = $BooksRagDataDir
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Error "python not found on PATH"
    exit 1
}

Write-Host "Books RAG batch: max-files=$MaxFiles root=$Root"
& python "40_operations/scripts/build_books_rag_index.py" --root $Root --max-files $MaxFiles
exit $LASTEXITCODE
