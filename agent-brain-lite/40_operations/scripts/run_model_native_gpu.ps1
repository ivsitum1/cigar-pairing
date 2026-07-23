# Residual-stream GPU pipeline (Python 3.12 + CUDA torch).
param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$Python312 = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
)

Set-Location $Root
if (-not (Test-Path $Python312)) {
    Write-Error "Python 3.12 not found at $Python312"
    exit 1
}
$env:MODEL_NATIVE_DEVICE = "cuda"
$env:MODEL_NATIVE_HOOK_MODEL = "gpt2"
& $Python312 40_operations\scripts\model_native_run.py run-gpu
exit $LASTEXITCODE
