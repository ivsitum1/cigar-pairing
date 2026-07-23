"""Contrast steering vectors in embedding space (representation engineering proxy)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .embedder import embed_mean, embed_texts


@dataclass
class SteeringVector:
    direction: np.ndarray
    positive_label: str
    negative_label: str
    magnitude: float

    def to_dict(self) -> dict:
        return {
            "positive_label": self.positive_label,
            "negative_label": self.negative_label,
            "magnitude": float(self.magnitude),
            "dim": int(self.direction.shape[0]),
        }


def derive_steering_vector(
    positive_texts: Sequence[str],
    negative_texts: Sequence[str],
    *,
    positive_label: str = "positive",
    negative_label: str = "negative",
) -> SteeringVector:
    pos = embed_mean(positive_texts)
    neg = embed_mean(negative_texts)
    raw = pos - neg
    mag = float(np.linalg.norm(raw))
    if mag < 1e-9:
        direction = raw
    else:
        direction = raw / mag
    return SteeringVector(
        direction=direction.astype(np.float32),
        positive_label=positive_label,
        negative_label=negative_label,
        magnitude=mag,
    )


def apply_steering(
    texts: Sequence[str],
    steering: SteeringVector,
    *,
    alpha: float = 0.35,
) -> np.ndarray:
    base = embed_texts(texts)
    if base.size == 0:
        return base
    steered = base + alpha * steering.direction.reshape(1, -1)
    norms = np.linalg.norm(steered, axis=1, keepdims=True)
    norms = np.where(norms < 1e-9, 1.0, norms)
    return (steered / norms).astype(np.float32)


def cosine_to_direction(vectors: np.ndarray, direction: np.ndarray) -> np.ndarray:
    if vectors.size == 0:
        return np.zeros(0, dtype=np.float32)
    d = direction.reshape(1, -1)
    return (vectors @ d.T).ravel().astype(np.float32)
