@echo off
REM Watch mode script for Windows
REM Automatically runs tests when files change
REM Run from project root: scripts\run_tests_watch.bat

echo ========================================
echo   Pytest Watch Mode
echo ========================================
echo.
echo Testovi ce se automatski pokrenuti kada sacuvate bilo koji Python fajl.
echo Pritisnite Ctrl+C za zaustavljanje.
echo.
echo Pokretanje watch mode-a...
echo.

python -m pytest_watch --runner "pytest -v --tb=short"

pause
