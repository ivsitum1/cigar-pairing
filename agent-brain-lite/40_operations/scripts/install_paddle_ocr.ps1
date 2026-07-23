# One-shot OCR stack: Python 3.12 venv + PaddlePaddle + paddleocr
$ErrorActionPreference = "Stop"
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Repo

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Error "Windows py launcher required."
}

$v312 = $false
try { py -3.12 --version | Out-Null; $v312 = $true } catch {}
if (-not $v312) {
    Write-Host "Installing Python 3.12..."
    py install 3.12
}

$venv = Join-Path $Repo ".venv-ocr"
if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
    py -3.12 -m venv $venv
}

& (Join-Path $venv "Scripts\python.exe") -m pip install -U pip
& (Join-Path $venv "Scripts\python.exe") -m pip install PyPDF2
# GPU first (RTX 4060 / CUDA); install_paddle_ocr.py falls back to CPU if GPU wheel fails
& (Join-Path $venv "Scripts\python.exe") (Join-Path $Repo "40_operations\scripts\install_paddle_ocr.py") --skip-bootstrap
& (Join-Path $venv "Scripts\python.exe") (Join-Path $Repo "40_operations\scripts\link_ocr_venv_path.py")

Write-Host "Done. Use: .\40_operations\scripts\extract_pdf_ocr.ps1 -Root . -Ocr auto"
