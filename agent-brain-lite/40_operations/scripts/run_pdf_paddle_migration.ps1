# Full PaddleOCR re-extraction for reference library + ingest hooks.
# Requires: .venv-ocr, PDFs synced under reference_library/ and 00_inbox/raw/
param(
    [string]$Root = ".",
    [switch]$SkipArchive,
    [switch]$SkipExtract,
    [switch]$SkipIngest,
    [switch]$RebuildRag,
    [string[]]$DomainsOnly = @()
)

$ErrorActionPreference = "Stop"
$env:FLAGS_use_mkldnn = "0"
$env:FLAGS_use_onednn = "0"
$env:FLAGS_enable_mkldnn = "0"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"
$env:PADDLE_OCR_DEVICE = "gpu"
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location (Resolve-Path (Join-Path $Repo $Root)).Path

$LogDir = Join-Path $Repo "data\pdf_extract"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir ("migration_{0:yyyy-MM-dd_HHmm}.log" -f (Get-Date))

function Write-Log([string]$Msg) {
    $line = "[{0:yyyy-MM-dd HH:mm:ss}] {1}" -f (Get-Date), $Msg
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding utf8
}

$Extract = Join-Path $Repo "40_operations\scripts\extract_pdf_ocr.ps1"
$Py = Join-Path $Repo ".venv-ocr\Scripts\python.exe"

if (-not (Test-Path $Py)) {
    Write-Error "Missing .venv-ocr. Run: .\40_operations\scripts\install_paddle_ocr.ps1"
}

Write-Log "=== PaddleOCR migration start (root=$Repo) ==="

Write-Log "Inventory audit"
& (Join-Path $Repo ".venv-ocr\Scripts\python.exe") `
    (Join-Path $Repo "40_operations\scripts\audit_books_md_extraction.py") `
    --root $Repo 2>&1 | Tee-Object -FilePath $LogFile -Append

if (-not $SkipArchive) {
    $Archive = Join-Path $Repo "90_archive\extractions\books_md_pypdf_2026-05"
    if (-not (Test-Path $Archive)) {
        Write-Log "Archiving books_md snapshot to $Archive (first run only)"
        $Src = Join-Path $Repo "20_knowledge\wiki\sources\books_md"
        if (Test-Path $Src) {
            New-Item -ItemType Directory -Force -Path (Split-Path $Archive -Parent) | Out-Null
            Copy-Item -Path $Src -Destination $Archive -Recurse -Force
        }
    } else {
        Write-Log "Archive already exists: $Archive"
    }
}

$Prefixes = @(
    "reference_library/statistics",
    "reference_library/writing",
    "reference_library/opinions",
    "reference_library/coding",
    "reference_library/medicine/anesthesiology",
    "reference_library/medicine/emergency",
    "reference_library/medicine/intensive_care",
    "reference_library/medicine/textbooks",
    "reference_library/temp_pdfs",
    "00_inbox/raw"
)

if ($DomainsOnly.Count -gt 0) {
    $Prefixes = @($DomainsOnly)
}

if (-not $SkipExtract) {
    foreach ($prefix in $Prefixes) {
        Write-Log "Extract: $prefix"
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $Extract -Root $Repo -Ocr paddle -ForceOcr -OnlyPrefix $prefix `
            -PruneStale -Resume -Report auto *>&1 | Tee-Object -FilePath $LogFile -Append
        $ErrorActionPreference = $prevEap
        if ($LASTEXITCODE -ne 0) {
            Write-Log "WARN: extract batch exited $LASTEXITCODE for prefix $prefix — retry once with --resume"
            $ErrorActionPreference = "Continue"
            & $Extract -Root $Repo -Ocr paddle -ForceOcr -OnlyPrefix $prefix `
                -PruneStale -Resume -Report auto *>&1 | Tee-Object -FilePath $LogFile -Append
            $ErrorActionPreference = $prevEap
            if ($LASTEXITCODE -ne 0) {
                Write-Log "WARN: retry still exited $LASTEXITCODE for $prefix (failed PDFs skipped in progress.json)"
            }
        }
    }
}

if (-not $SkipIngest) {
    Write-Log "ingest_pdf_sources.py"
    & $Py (Join-Path $Repo "40_operations\scripts\ingest_pdf_sources.py") --root $Repo 2>&1 |
        Tee-Object -FilePath $LogFile -Append

    $LinkHubs = Join-Path $Repo "40_operations\scripts\link_books_md_hubs.py"
    if (Test-Path $LinkHubs) {
        Write-Log "link_books_md_hubs.py"
        & $Py $LinkHubs --root $Repo 2>&1 | Tee-Object -FilePath $LogFile -Append
    }
}

Write-Log "Post-migration audit"
& $Py (Join-Path $Repo "40_operations\scripts\audit_books_md_extraction.py") --root $Repo 2>&1 |
    Tee-Object -FilePath $LogFile -Append

Write-Log "Final migration report (MD + JSON)"
& $Py (Join-Path $Repo "40_operations\scripts\report_pdf_migration.py") --root $Repo 2>&1 |
    Tee-Object -FilePath $LogFile -Append
Write-Log "Report: data/pdf_extract/migration_report_latest.md"

if ($RebuildRag) {
    . (Join-Path $Repo "40_operations\scripts\_books_rag_paths.ps1")
    $env:BOOKS_RAG_DATA_DIR = $BooksRagDataDir
    Write-Log "build_books_rag_index.py --force (index dir: $BooksRagDataDir)"
    Remove-Item (Join-Path $BooksRagDataDir ".build.lock") -Force -ErrorAction SilentlyContinue
    $RagPy = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" }
    & $RagPy (Join-Path $Repo "40_operations\scripts\build_books_rag_index.py") --root $Repo --force 2>&1 |
        Tee-Object -FilePath $LogFile -Append
    if ($LASTEXITCODE -ne 0) {
        Write-Log "WARN: RAG rebuild exited $LASTEXITCODE"
    } else {
        Write-Log "RAG index rebuild complete."
    }
} else {
    Write-Log "=== Migration extract/ingest complete. Next: build_books_rag_index.py --force ==="
}
Write-Log "Log: $LogFile"
