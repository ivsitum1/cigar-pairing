@echo off
REM Start PaddleOCR API (Windows). Uses backend\.venv (Python 3.12).
cd /d "%~dp0"
call .venv\Scripts\activate.bat
set FLAGS_use_mkldnn=0
set PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
uvicorn app.main:app --host 0.0.0.0 --port 8787
