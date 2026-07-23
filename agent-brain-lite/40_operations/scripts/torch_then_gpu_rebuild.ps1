# Wait for torch wheel download, install CUDA torch, then optional books_rag rebuild.
param(
    [string]$WheelPath = "$env:TEMP\torch-2.10.0+cu128-cp314-win_amd64.whl",
    [switch]$SkipRebuild
)

$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$expectedBytes = 3026403330

Write-Host "[torch_then_rebuild] Waiting for wheel >= 99% of $expectedBytes bytes ..."
while ($true) {
    if (Test-Path $WheelPath) {
        $size = (Get-Item $WheelPath).Length
        $pct = [math]::Round(100.0 * $size / $expectedBytes, 1)
        Write-Host "  wheel: $pct% ($size bytes)"
        if ($size -ge ($expectedBytes * 0.99)) { break }
    } else {
        Write-Host "  wheel: not started"
    }
    Start-Sleep -Seconds 60
}

& "$PSScriptRoot\install_cuda_torch.ps1" -WheelPath $WheelPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($SkipRebuild) { exit 0 }

$env:BOOKS_RAG_DATA_DIR = "C:\books_rag"
$env:AGENT_COMPUTE_DEVICE = "auto"
Set-Location $root
if (Test-Path "C:\books_rag\.build.lock") { Remove-Item "C:\books_rag\.build.lock" -Force }
python 40_operations/scripts/build_books_rag_index.py --root . --force
exit $LASTEXITCODE
