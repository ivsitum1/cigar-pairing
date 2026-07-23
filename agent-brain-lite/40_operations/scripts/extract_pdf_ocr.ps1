# Extract PDFs with PaddleOCR using the project OCR venv (Python 3.12).
param(
    [string]$Root = ".",
    [ValidateSet("auto", "paddle", "off")]
    [string]$Ocr = "auto",
    [string]$OnlyPrefix = "",
    [switch]$ForceOcr,
    [switch]$PruneStale,
    [switch]$Resume,
    [string]$Report = ""
)

$ErrorActionPreference = "Stop"
$env:FLAGS_use_mkldnn = "0"
$env:FLAGS_use_onednn = "0"
$env:FLAGS_enable_mkldnn = "0"
if (-not $env:PADDLE_OCR_DEVICE) { $env:PADDLE_OCR_DEVICE = "gpu" }
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Py = Join-Path $Repo ".venv-ocr\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    Write-Error "Missing .venv-ocr. Run: py -3.12 -m venv .venv-ocr; then python 40_operations/scripts/install_paddle_ocr.py"
}
$Args = @(
    (Join-Path $Repo "40_operations\scripts\extract_pdf_library_to_md.py"),
    "--root", (Resolve-Path $Root).Path,
    "--ocr", $Ocr
)
if ($OnlyPrefix) { $Args += @("--only-prefix", $OnlyPrefix) }
if ($ForceOcr) { $Args += "--force-ocr" }
if ($PruneStale) { $Args += "--prune-stale" }
if ($Resume) { $Args += "--resume" }
if ($Report) { $Args += @("--report", $Report) }
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $Py @Args *>&1 | ForEach-Object { Write-Host $_ }
$code = $LASTEXITCODE
$ErrorActionPreference = $prevEap
if ($code -ne 0) { exit $code }
