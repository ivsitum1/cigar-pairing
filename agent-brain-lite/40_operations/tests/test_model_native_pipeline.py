"""Tests for model-native steering (mocked embeddings)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from model_native.eval_protocol import run_baseline_vs_steered  # noqa: E402


def _fake_embed(texts):
    out = []
    for t in texts:
        upper = t.upper()
        if "POSITIVE" in upper:
            out.append(np.array([1.0, 0.0], dtype=np.float32))
        elif "NEGATIVE" in upper:
            out.append(np.array([0.0, 1.0], dtype=np.float32))
        else:
            out.append(np.array([0.5, 0.5], dtype=np.float32))
    return np.stack(out)


def _fake_mean(texts):
    return _fake_embed(texts).mean(axis=0)


def _patch_embedders():
    return (
        patch("model_native.embedder.embed_texts", side_effect=_fake_embed),
        patch("model_native.embedder.embed_mean", side_effect=_fake_mean),
        patch("model_native.steering.embed_texts", side_effect=_fake_embed),
        patch("model_native.steering.embed_mean", side_effect=_fake_mean),
        patch("model_native.eval_protocol.embed_texts", side_effect=_fake_embed),
    )


def test_steering_improves_alignment():
    p1, p2, p3, p4, p5 = _patch_embedders()
    with p1, p2, p3, p4, p5:
        pos = ["POSITIVE skill behavior"]
        neg = ["NEGATIVE skip behavior"]
        prompts = ["POSITIVE eval prompt"]
        _, report = run_baseline_vs_steered(prompts, pos, neg, alpha=0.5)
        assert report.improved
        assert report.delta > 0


def test_derive_steering_vector_unit_norm():
    p1, p2, p3, p4, p5 = _patch_embedders()
    with p1, p2, p3, p4, p5:
        from model_native.steering import derive_steering_vector

        sv = derive_steering_vector(["positive skill"], ["negative skip"])
        assert sv.direction.shape == (2,)
        assert abs(float(np.linalg.norm(sv.direction)) - 1.0) < 1e-5
