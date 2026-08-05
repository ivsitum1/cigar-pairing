# Start PaddleOCR API
Set-Location $PSScriptRoot
& .\.venv\Scripts\Activate.ps1
$env:FLAGS_use_mkldnn = "0"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"
uvicorn app.main:app --host 0.0.0.0 --port 8787
