"""Pytest path setup for harness python package."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_HARNESS_PY = REPO_ROOT / "40_operations" / "python"
if str(_HARNESS_PY) not in sys.path:
    sys.path.insert(0, str(_HARNESS_PY))
