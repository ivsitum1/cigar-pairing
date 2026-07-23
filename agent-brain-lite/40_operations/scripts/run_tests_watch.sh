#!/bin/bash
# Watch mode script for Linux/Mac
# Automatically runs tests when files change
# Run from project root: ./40_operations/scripts/run_tests_watch.sh

echo "========================================"
echo "  Pytest Watch Mode"
echo "========================================"
echo ""
echo "Testovi će se automatski pokrenuti kada sačuvate bilo koji Python fajl."
echo "Pritisnite Ctrl+C za zaustavljanje."
echo ""
echo "Pokretanje watch mode-a..."
echo ""

python -m pytest_watch --runner "pytest -v --tb=short"
