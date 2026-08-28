# Start PaddleOCR API (loopback by default — set OCR_HOST=0.0.0.0 + OCR_API_TOKEN for LAN/APK)
Set-Location $PSScriptRoot
& .\.venv\Scripts\Activate.ps1
$env:FLAGS_use_mkldnn = "0"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"
$hostBind = if ($env:OCR_HOST) { $env:OCR_HOST } else { "127.0.0.1" }
$loopback = @("127.0.0.1", "localhost", "::1")
if ($hostBind -notin $loopback -and -not $env:OCR_API_TOKEN) {
  Write-Error "OCR_API_TOKEN is required when binding to $hostBind (non-loopback)."
  exit 1
}
uvicorn app.main:app --host $hostBind --port 8787
