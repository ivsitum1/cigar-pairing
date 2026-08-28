@echo off
REM Start PaddleOCR API (Windows). Loopback by default; LAN needs OCR_HOST + OCR_API_TOKEN.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
set FLAGS_use_mkldnn=0
set PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
if not defined OCR_HOST set OCR_HOST=127.0.0.1
if /I not "%OCR_HOST%"=="127.0.0.1" if /I not "%OCR_HOST%"=="localhost" if /I not "%OCR_HOST%"=="::1" (
  if not defined OCR_API_TOKEN (
    echo OCR_API_TOKEN is required when binding to %OCR_HOST% ^(non-loopback^).
    exit /b 1
  )
)
uvicorn app.main:app --host %OCR_HOST% --port 8787
