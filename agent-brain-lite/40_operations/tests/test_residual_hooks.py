"""Tests for residual-stream math helpers (no torch load)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

WORKSPACE = Path(__file__).resolve().parents[2]
PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(PY_ROOT))

from model_native.gpu_pipeline import _cosine_rows, _unit_norm  # noqa: E402


def test_gpu_pipeline_unit_norm_logic():
    direction = _unit_norm(np.array([3.0, 4.0], dtype=np.float32))
    vecs = np.array([[3.0, 4.0], [0.0, 1.0]], dtype=np.float32)
    scores = _cosine_rows(vecs, direction)
    assert scores[0] > scores[1]
