"""Lazy sentence-transformer embedder for model-native pipeline."""
from __future__ import annotations

from functools import lru_cache
from typing import Sequence

import numpy as np

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _model_name() -> str:
    import os

    return os.environ.get("MODEL_NATIVE_EMBED_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


@lru_cache(maxsize=1)
def _load_model():
    import os
    import sys
    from pathlib import Path
    from sentence_transformers import SentenceTransformer

    ops = Path(__file__).resolve().parents[1] / "common"
    parent = ops.parent
    if str(parent) not in sys.path:
        sys.path.insert(0, str(parent))
    from common.gpu import log_device, resolve_device

    dev = resolve_device(os.environ.get("MODEL_NATIVE_DEVICE", "auto"))
    log_device(f"model_native embedder({_model_name()})")
    return SentenceTransformer(_model_name(), device=dev)


def embed_texts(texts: Sequence[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)
    model = _load_model()
    vectors = model.encode(list(texts), convert_to_numpy=True, normalize_embeddings=True)
    return np.asarray(vectors, dtype=np.float32)


def embed_mean(texts: Sequence[str]) -> np.ndarray:
    mat = embed_texts(texts)
    if mat.size == 0:
        raise ValueError("empty text list for embedding mean")
    mean = mat.mean(axis=0)
    norm = np.linalg.norm(mean)
    if norm < 1e-9:
        return mean
    return mean / norm
