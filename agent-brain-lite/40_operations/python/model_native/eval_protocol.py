"""Baseline vs steered evaluation protocol for model-native transforms."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .embedder import embed_texts
from .steering import SteeringVector, apply_steering, cosine_to_direction, derive_steering_vector


@dataclass
class EvalReport:
    baseline_mean_alignment: float
    steered_mean_alignment: float
    delta: float
    improved: bool
    n_prompts: int
    alpha: float

    def to_dict(self) -> dict:
        return {
            "baseline_mean_alignment": round(self.baseline_mean_alignment, 4),
            "steered_mean_alignment": round(self.steered_mean_alignment, 4),
            "delta": round(self.delta, 4),
            "improved": self.improved,
            "n_prompts": self.n_prompts,
            "alpha": self.alpha,
            "claim_status": "VERIFIED" if self.improved else "INFERRED",
        }


def run_baseline_vs_steered(
    eval_prompts: Sequence[str],
    positive_texts: Sequence[str],
    negative_texts: Sequence[str],
    *,
    alpha: float = 0.35,
) -> tuple[SteeringVector, EvalReport]:
    steering = derive_steering_vector(positive_texts, negative_texts)
    baseline = embed_texts(eval_prompts)
    steered = apply_steering(eval_prompts, steering, alpha=alpha)
    base_scores = cosine_to_direction(baseline, steering.direction)
    steer_scores = cosine_to_direction(steered, steering.direction)
    b_mean = float(np.mean(base_scores)) if base_scores.size else 0.0
    s_mean = float(np.mean(steer_scores)) if steer_scores.size else 0.0
    delta = s_mean - b_mean
    return steering, EvalReport(
        baseline_mean_alignment=b_mean,
        steered_mean_alignment=s_mean,
        delta=delta,
        improved=delta > 0,
        n_prompts=len(eval_prompts),
        alpha=alpha,
    )
