# Install CUDA-enabled PyTorch for Python 3.14 (cu128).
# Plain pip install torch gives CPU-only wheels on Windows.
param(
    [string]$WheelPath = "$env:TEMP\torch-2.10.0+cu128-cp314-win_amd64.whl",
    [switch]$DownloadIfMissing
)

$ErrorActionPreference = "Stop"
$url = "https://download.pytorch.org/whl/cu128/torch-2.10.0%2Bcu128-cp314-cp314-win_amd64.whl"
$expectedBytes = 3026403330

if ($DownloadIfMissing -and -not (Test-Path $WheelPath)) {
    Write-Host "[install_cuda_torch] Downloading wheel to $WheelPath ..."
    curl.exe -L --retry 5 --retry-delay 5 -o $WheelPath $url
}

if (-not (Test-Path $WheelPath)) {
    Write-Error "Wheel not found: $WheelPath. Run with -DownloadIfMissing or download manually."
}

$size = (Get-Item $WheelPath).Length
if ($size -lt ($expectedBytes * 0.99)) {
    Write-Error "Wheel incomplete ($size bytes). Wait for download to finish."
}

Write-Host "[install_cuda_torch] Installing from local wheel ..."
python -m pip install --force-reinstall $WheelPath
python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'; print('OK', torch.__version__, torch.version.cuda)"
